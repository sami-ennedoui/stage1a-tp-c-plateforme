#!/usr/bin/env python3
"""Banc de smoke-tests du correcteur (mode démo).

Pour chaque exercice, on demande au tuteur d'ÉCRIRE le programme (moteur claude ou
codex, comme dans l'appli), puis on passe la porte et on regarde comment le
correcteur réagit. On peut demander plusieurs variantes : une solution correcte,
ou des variantes volontairement fautives, pour vérifier que la porte les rejette.

Prérequis : gcc sur le PATH (w64devkit) et un moteur IA sur le PATH (claude ou
codex), comme pour l'appli. On force le moteur avec --moteur ou la variable
ATELIER_AI.

Exemples :
  python outils/demo_smoketest.py                      # ex01 seul, les 3 variantes
  python outils/demo_smoketest.py --tous               # les 14 exercices
  python outils/demo_smoketest.py --exos ex01_types,ex05_rectangle
  python outils/demo_smoketest.py --variantes correcte # que la solution correcte
  python outils/demo_smoketest.py --moteur codex --tous
"""
import argparse
import os
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

import executeur
import tuteur_ia
from modele_etape import charger_etape

# variante -> (consigne passée au tuteur, comportement attendu de la porte)
VARIANTES = {
    "correcte": ("", "OUVRE"),
    "format": ("Introduis une erreur de format d'affichage typique, par exemple un %d "
               "pour un nombre a virgule. Le programme doit quand meme compiler.", "FERME"),
    "compilation": ("Introduis une petite erreur de compilation typique d'un debutant, "
                    "par exemple un point-virgule manquant.", "FERME"),
    "incomplete": ("N'affiche qu'une partie de ce qui est demande : oublie volontairement "
                   "une des lignes attendues.", "FERME"),
}


def contenu(parcours: str) -> Path:
    return RACINE / "contenu" / parcours


def lister_exos(parcours: str) -> list[str]:
    d = contenu(parcours)
    return sorted(p.name for p in d.iterdir() if p.is_dir())


def main() -> int:
    ap = argparse.ArgumentParser(description="Banc de smoke-tests du correcteur (mode démo)")
    ap.add_argument("--parcours", default="be_c")
    ap.add_argument("--moteur", choices=("claude", "codex"), help="force le moteur IA")
    ap.add_argument("--exos", help="liste d'exercices séparés par des virgules")
    ap.add_argument("--tous", action="store_true", help="tous les exercices du parcours")
    ap.add_argument("--variantes", default="correcte,format,compilation",
                    help="variantes à tester, séparées par des virgules "
                         f"(parmi {', '.join(VARIANTES)})")
    args = ap.parse_args()

    executeur.assurer_compilateur_sur_path()
    if args.moteur:
        os.environ["ATELIER_AI"] = args.moteur
    if not tuteur_ia.moteur_disponible():
        print("Aucun moteur IA disponible (claude ou codex sur le PATH). Abandon.")
        return 2

    if args.exos:
        exos = [e.strip() for e in args.exos.split(",") if e.strip()]
    elif args.tous:
        exos = lister_exos(args.parcours)
    else:
        exos = ["ex01_types"]

    variantes = [v.strip() for v in args.variantes.split(",") if v.strip()]
    inconnues = [v for v in variantes if v not in VARIANTES]
    if inconnues:
        print("Variantes inconnues :", ", ".join(inconnues))
        return 2

    print(f"Moteur : {tuteur_ia._moteur_choisi()}   parcours : {args.parcours}")
    print(f"Exercices : {len(exos)}   variantes : {', '.join(variantes)}\n")

    conformes = 0
    total = 0
    surprises = []
    for nom in exos:
        d = contenu(args.parcours) / nom
        if not (d / "meta.json").exists():
            print(f"  {nom} : introuvable, ignoré")
            continue
        etape = charger_etape(d)
        print(f"== {nom} ==")
        for v in variantes:
            consigne, attendu = VARIANTES[v]
            code = tuteur_ia.generer_solution(etape, consigne)
            total += 1
            if tuteur_ia.reponse_est_erreur(code):
                print(f"   {v:12s} moteur en echec : {code}")
                surprises.append((nom, v, "moteur en echec"))
                continue
            r = executeur.porte_programme(etape, code)
            etat = "OUVRE" if r.ok else "FERME"
            conforme = (etat == attendu)
            conformes += conforme
            marque = "ok " if conforme else "!! "
            detail = "" if r.ok else "  (" + (r.sortie.splitlines()[0] if r.sortie else "") + ")"
            print(f"   {marque}{v:12s} attendu {attendu:5s} -> {etat}{detail}")
            if not conforme:
                surprises.append((nom, v, f"attendu {attendu}, obtenu {etat}"))
        print()

    print(f"Conformes : {conformes}/{total}")
    if surprises:
        print("À regarder :")
        for nom, v, msg in surprises:
            print(f"   {nom} / {v} : {msg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
