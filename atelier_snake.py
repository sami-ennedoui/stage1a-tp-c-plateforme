#!/usr/bin/env python3
"""Atelier Snake. Lance l'appli, ou les autotests sans écran.
  python3 atelier_snake.py                    lance la fenêtre, parcours hybride
  python3 atelier_snake.py --parcours projet  lance le parcours projet
  python3 atelier_snake.py --selftest         vérifie les portes sans écran
  python3 atelier_snake.py --releve           écrit releve.txt et l'affiche, sans écran
  python3 atelier_snake.py --smoketest        construit la fenêtre sans l'afficher
  python3 atelier_snake.py --demo             mode démo, tout débloqué, bouton Charger le corrigé
Le mode démo et --parcours se combinent : --demo --parcours projet charge le corrigé du projet.
"""
import sys
from pathlib import Path

# Le paquet portable Windows embarque la distribution « embeddable » de Python, qui tourne
# en mode isolé à cause de son fichier python3xx._pth : elle n'ajoute pas d'elle-même le
# dossier du script à sys.path, et elle ignore PYTHONPATH. Sans cette ligne, « import
# chemins » échoue au lancement. Sans effet sur un Python normal, où le dossier y est déjà.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import chemins
import executeur
from modele_etape import ParcoursIntrouvable, charger_etape


def _parcours_choisi() -> str:
    """Parcours à ouvrir. Priorité à --parcours <nom> ou --parcours=<nom>, sinon le
    dernier parcours mémorisé dans reglages.json (défaut be_c au tout premier lancement)."""
    for i, a in enumerate(sys.argv):
        if a.startswith("--parcours="):
            return a.split("=", 1)[1]
        if a == "--parcours" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    import reglages
    return reglages.dernier_parcours()


def selftest() -> int:
    echecs = 0

    p1 = charger_etape(chemins.CONTENU / "perso_P1")
    if not executeur.porte_perso(p1, (p1.dossier / "corrige.c").read_text()).ok:
        print("FAIL P1 : le corrigé devrait passer"); echecs += 1
    if executeur.porte_perso(p1, (p1.dossier / "starter.c").read_text()).ok:
        print("FAIL P1 : le starter ne devrait pas passer"); echecs += 1

    j1 = charger_etape(chemins.CONTENU / "jalon1_parametrage")
    ref = (j1.dossier / "test_reference.c").read_text()
    jug = executeur.juger_test(j1, ref)
    if not jug.test_solide:
        print("FAIL jalon1 : le test de référence devrait être jugé solide\n", jug.sortie)
        echecs += 1
    if not executeur.porte_jalon(j1, (j1.dossier / "corrige.c").read_text(), ref).ok:
        print("FAIL jalon1 : la porte du corrigé devrait passer"); echecs += 1

    print("SELFTEST OK" if echecs == 0 else f"SELFTEST {echecs} ECHEC(S)")
    return echecs


def releve_cli() -> int:
    import releve
    contenu = releve.texte(_parcours_choisi())
    releve.ecrire(contenu)
    print(contenu)
    return 0


def smoketest() -> int:
    from PyQt6.QtWidgets import QApplication
    import fenetre
    import theme
    app = QApplication.instance() or QApplication([])
    theme.appliquer(app)
    f = fenetre.construire(app, parcours_nom=_parcours_choisi())
    print("SMOKETEST OK, fenêtre construite :", f.windowTitle())
    return 0


def main():
    if "--selftest" in sys.argv:
        sys.exit(1 if selftest() else 0)
    if "--releve" in sys.argv:
        sys.exit(releve_cli())
    if "--smoketest" in sys.argv:
        sys.exit(smoketest())
    from PyQt6.QtWidgets import QApplication
    import fenetre
    import theme
    app = QApplication(sys.argv)
    theme.appliquer(app)
    f = fenetre.Fenetre(demo="--demo" in sys.argv, parcours_nom=_parcours_choisi())
    f.resize(1280, 800)
    f.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except ParcoursIntrouvable as e:
        # message lisible plutôt qu'une trace Python : le paquet portable ne livre pas
        # forcément tous les parcours du dépôt, et lancer.bat garde la fenêtre ouverte.
        print(f"\n{e}\n", file=sys.stderr)
        sys.exit(1)
