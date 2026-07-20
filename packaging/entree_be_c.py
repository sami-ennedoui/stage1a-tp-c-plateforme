"""Point d'entree du .exe PyInstaller : force le parcours be_c, puis lance l'atelier.

Sert d'entree au build fige (voir packaging/build_exe.txt). Le .exe n'a pas
d'arguments au double-clic, donc on impose --parcours be_c ici. On respecte un
--parcours deja fourni (utile pour tester un autre parcours en ligne de commande).
"""
import sys

if "--parcours" not in " ".join(sys.argv):
    sys.argv += ["--parcours", "be_c"]

from atelier_snake import main

main()
