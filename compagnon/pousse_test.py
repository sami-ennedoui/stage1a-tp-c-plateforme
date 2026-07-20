"""Pousse une note d'essai au carnet Moodle pour l'appairage le plus récent.
Usage : python -m compagnon.pousse_test 42.0
À lancer dans le shell Render, où vivent la base et les variables d'environnement."""
import json
import os
import sys
from pathlib import Path

from compagnon import base, lti

BASE_DEFAUT = Path(__file__).resolve().parent / "compagnon.sqlite3"

if __name__ == "__main__":
    valeur = float(sys.argv[1])
    cx = base.ouvrir(os.environ.get("COMPAGNON_BASE", str(BASE_DEFAUT)))
    ligne = cx.execute("SELECT sub, ags_claim FROM appairages ORDER BY cree DESC LIMIT 1").fetchone()
    if ligne is None:
        sys.exit("aucun appairage : cliquer d'abord l'activité dans Moodle")
    lti.pousser_score(ligne["sub"], valeur, json.loads(ligne["ags_claim"]))
    print(f"note {valeur} poussée pour {ligne['sub']}")
