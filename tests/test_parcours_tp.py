"""Vérifie le parcours tp_c (questions du BE C, programmes complets) sans interface :
pour chaque exercice, le corrigé passe la porte programme et le starter échoue."""
import unittest

import chemins
import executeur
from modele_etape import charger_parcours_complet


class TestParcoursTP(unittest.TestCase):

    def setUp(self):
        self.parcours = charger_parcours_complet(chemins.contenu_racine("tp_c"))

    def test_mode_et_etapes(self):
        self.assertEqual(self.parcours.mode, "isole")
        self.assertEqual([e.id for e in self.parcours.etapes],
                         ["tp_operateurs", "tp_controle", "tp_rectangle", "tp_second_degre"])
        for e in self.parcours.etapes:
            self.assertEqual(e.mode, "programme")

    def test_corrige_passe_starter_echoue(self):
        for etape in self.parcours.etapes:
            corrige = (etape.dossier / "corrige.c").read_text(encoding="utf-8")
            starter = (etape.dossier / "starter.c").read_text(encoding="utf-8")
            with self.subTest(etape=etape.id):
                self.assertTrue(executeur.porte_programme(etape, corrige).ok,
                                f"{etape.id} : le corrigé devrait passer la porte")
                self.assertFalse(executeur.porte_programme(etape, starter).ok,
                                 f"{etape.id} : le starter ne devrait pas passer la porte")


if __name__ == "__main__":
    unittest.main()
