#!/usr/bin/env python3
"""Atelier Snake. Lance l'appli, ou les autotests sans écran.
  python3 atelier_snake.py             lance la fenêtre
  python3 atelier_snake.py --selftest  vérifie les portes sans écran
  python3 atelier_snake.py --smoketest construit la fenêtre sans l'afficher
"""
import sys

import chemins
import executeur
from modele_etape import charger_parcours, charger_etape


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


def smoketest() -> int:
    from PyQt6.QtWidgets import QApplication
    import fenetre
    app = QApplication.instance() or QApplication([])
    f = fenetre.construire(app)
    print("SMOKETEST OK, fenêtre construite :", f.windowTitle())
    return 0


def main():
    if "--selftest" in sys.argv:
        sys.exit(1 if selftest() else 0)
    if "--smoketest" in sys.argv:
        sys.exit(smoketest())
    from PyQt6.QtWidgets import QApplication
    import fenetre
    app = QApplication(sys.argv)
    f = fenetre.Fenetre()
    f.resize(1280, 800)
    f.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
