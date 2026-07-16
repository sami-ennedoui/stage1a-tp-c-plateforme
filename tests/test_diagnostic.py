import json
import tempfile
import unittest
from pathlib import Path

import chemins
import diagnostic


class TestDiagnostic(unittest.TestCase):
    def test_parcours_disponibles_sur_dossier_temp(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            for nom in ("be_c", "hybride"):
                (base / nom).mkdir()
                (base / nom / "parcours.json").write_text("{}", encoding="utf-8")
            (base / "sans_parcours").mkdir()  # dossier sans parcours.json, ignoré
            self.assertEqual(diagnostic.parcours_disponibles(base), ["be_c", "hybride"])

    def test_parcours_disponibles_trouve_be_c_reel(self):
        # le vrai dossier contenu/ du dépôt contient au moins be_c
        noms = diagnostic.parcours_disponibles()
        self.assertIn("be_c", noms)

    def test_outils_couvre_les_trois(self):
        noms = [nom for nom, _ in diagnostic.outils()]
        self.assertEqual(noms, list(diagnostic.OUTILS))

    def test_chemins_cles_pointent_sur_le_parcours(self):
        cles = dict(diagnostic.chemins_cles("be_c"))
        self.assertEqual(cles["Contenu du parcours"], chemins.contenu_racine("be_c"))
        self.assertEqual(cles["Dossier de l'appli"], chemins.RACINE)


if __name__ == "__main__":
    unittest.main()
