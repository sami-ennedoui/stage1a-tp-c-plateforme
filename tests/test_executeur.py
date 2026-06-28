import unittest
import chemins
from modele_etape import charger_etape
from executeur import porte_perso


class TestPortePerso(unittest.TestCase):
    def setUp(self):
        self.etape = charger_etape(chemins.CONTENU / "perso_P1")
        self.corrige = (self.etape.dossier / "corrige.c").read_text(encoding="utf-8")
        self.starter = (self.etape.dossier / "starter.c").read_text(encoding="utf-8")

    def test_corrige_passe(self):
        r = porte_perso(self.etape, self.corrige)
        self.assertTrue(r.ok, r.sortie)

    def test_starter_echoue(self):
        r = porte_perso(self.etape, self.starter)
        self.assertFalse(r.ok, r.sortie)


if __name__ == "__main__":
    unittest.main()
