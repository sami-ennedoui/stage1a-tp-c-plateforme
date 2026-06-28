import unittest
from pathlib import Path
import chemins
from modele_etape import charger_parcours, charger_etape


class TestModeleEtape(unittest.TestCase):
    def test_parcours_dans_l_ordre(self):
        etapes = charger_parcours(chemins.CONTENU)
        self.assertEqual([e.id for e in etapes], ["perso_P1", "jalon1_parametrage"])

    def test_champs_perso(self):
        e = charger_etape(chemins.CONTENU / "perso_P1")
        self.assertEqual(e.type, "perso")
        self.assertEqual(e.mode, "test_fourni")
        self.assertEqual(e.cran_debloque, 1)

    def test_champs_jalon(self):
        e = charger_etape(chemins.CONTENU / "jalon1_parametrage")
        self.assertEqual(e.type, "jalon")
        self.assertEqual(e.mode, "test_a_ecrire")
        self.assertEqual(e.fichier_edite, "GestionMenuParametrage.c")


if __name__ == "__main__":
    unittest.main()
