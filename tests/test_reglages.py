import tempfile
import unittest
from pathlib import Path

import chemins
import reglages


class TestReglages(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._sauve = chemins.REGLAGES_FICHIER
        chemins.REGLAGES_FICHIER = Path(self._tmp.name) / "reglages.json"

    def tearDown(self):
        chemins.REGLAGES_FICHIER = self._sauve
        self._tmp.cleanup()

    def test_defaut_sans_fichier(self):
        self.assertEqual(reglages.dernier_parcours(), reglages.PARCOURS_DEFAUT)

    def test_definir_puis_relire(self):
        reglages.definir_parcours("be_c")
        self.assertEqual(reglages.dernier_parcours(), "be_c")

    def test_fichier_corrompu_retombe_sur_defaut(self):
        chemins.REGLAGES_FICHIER.write_text("{ pas du json", encoding="utf-8")
        self.assertEqual(reglages.dernier_parcours("hybride"), "hybride")


if __name__ == "__main__":
    unittest.main()
