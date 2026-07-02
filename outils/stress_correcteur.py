#!/usr/bin/env python3
"""Stress-test de robustesse du correcteur (porte_programme), sans IA.

On soumet des programmes pathologiques (boucle infinie, crash, sortie enorme,
lecture stdin excessive, octets non-UTF8...) et on verifie que la porte repond
proprement : un Resultat, pas d'exception, pas de blocage au-dela du delai, pas
d'explosion memoire. C'est ce qui garantit qu'un code d'etudiant tordu ne fige
pas la fenetre.

Usage : python outils/stress_correcteur.py
"""
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

import executeur
from modele_etape import charger_etape

# On reutilise une etape existante pour la config de la porte (entree, etc.),
# mais on injecte notre propre code pathologique. ex01 n'a pas d'entree.
ETAPE = charger_etape(RACINE / "contenu" / "be_c" / "ex01_types")

CAS = [
    ("boucle infinie sans sortie",
     "int main(void){ while(1){} return 0; }", "delai"),
    # NB : une boucle infinie qui inonde stdout n'est PAS testee ici : capture_output
    # bufferise sans plafond jusqu'au delai (15s) -> risque memoire. Voir le cas fini
    # ci-dessous et l'analyse dans le rapport.
    ("sortie enorme mais finie (~50 Mo)",
     '#include <stdio.h>\nint main(void){ for(long i=0;i<50000000L;i++) putchar(65); return 0; }', "gros"),
    ("crash: dereference NULL",
     "int main(void){ int*p=0; *p=1; return 0; }", "erreur"),
    ("division par zero",
     "int main(void){ int a=1,b=0; return a/b; }", "erreur"),
    ("exit code non nul",
     "int main(void){ return 3; }", "erreur"),
    ("lit plus de stdin que fourni",
     "#include <stdio.h>\nint main(void){ int x; while(scanf(\"%d\",&x)==1){} return 0; }", "ok/delai"),
    ("octets non-UTF8 dans la sortie",
     '#include <stdio.h>\nint main(void){ putchar(0xFF); putchar(0xFE); return 0; }', "ferme"),
    ("pas de main",
     "int pas_de_main(void){ return 0; }", "compile"),
    ("code vide",
     "", "compile"),
    ("warning mais compile (variable inutilisee)",
     "#include <stdio.h>\nint main(void){ int x; printf(\"ok\\n\"); return 0; }", "ferme"),
]


def main() -> int:
    executeur.assurer_compilateur_sur_path()
    incidents = []
    for nom, code, attendu in CAS:
        t0 = time.monotonic()
        etat = "?"
        try:
            r = executeur.porte_programme(ETAPE, code)
            dt = time.monotonic() - t0
            etat = "OUVRE" if r.ok else "FERME"
            premiere = r.sortie.splitlines()[0] if r.sortie else ""
            # borne de securite : la porte ne doit jamais depasser largement son delai (15s)
            trop_long = dt > 40
            if trop_long:
                incidents.append((nom, f"trop long : {dt:.0f}s"))
            print(f"[{ 'LENT' if trop_long else 'ok ' }] {nom:42s} {etat:5s} {dt:5.1f}s  {premiere[:60]}")
        except Exception as e:
            dt = time.monotonic() - t0
            incidents.append((nom, f"EXCEPTION {type(e).__name__}: {e}"))
            print(f"[!! ] {nom:42s} EXCEPTION apres {dt:.1f}s : {type(e).__name__}: {e}")

    print()
    if incidents:
        print(f"INCIDENTS : {len(incidents)}")
        for nom, msg in incidents:
            print(f"   {nom} : {msg}")
    else:
        print("Aucun incident : la porte repond proprement a tous les cas (pas d'exception, "
              "pas de blocage au-dela du delai).")
    return 1 if incidents else 0


if __name__ == "__main__":
    sys.exit(main())
