"""Vérifie le parcours perso sans interface : pour chaque séance, le corrigé passe
la porte perso et le starter échoue. Valide aussi que le tuteur trouve son corrigé."""
import unittest

import chemins
import executeur
from modele_etape import charger_parcours_complet


class TestParcoursPerso(unittest.TestCase):

    def setUp(self):
        self.parcours = charger_parcours_complet(chemins.contenu_racine("perso"))

    def test_mode_et_etapes(self):
        self.assertEqual(self.parcours.mode, "isole")
        self.assertEqual([e.id for e in self.parcours.etapes],
                         ["s1_types", "s2_pointeurs", "s3_tableaux", "s4_sousprog"])

    def test_corrige_passe_starter_echoue(self):
        for etape in self.parcours.etapes:
            corrige = (etape.dossier / "corrige.c").read_text(encoding="utf-8")
            starter = (etape.dossier / "starter.c").read_text(encoding="utf-8")
            with self.subTest(etape=etape.id):
                self.assertTrue(executeur.porte_perso(etape, corrige).ok,
                                f"{etape.id} : le corrigé devrait passer la porte")
                self.assertFalse(executeur.porte_perso(etape, starter).ok,
                                 f"{etape.id} : le starter ne devrait pas passer la porte")

    def test_tuteur_trouve_le_corrige(self):
        import tuteur_ia
        for etape in self.parcours.etapes:
            chemin = tuteur_ia._chemin_corrige(etape)
            with self.subTest(etape=etape.id):
                self.assertTrue(chemin.exists(),
                                f"{etape.id} : le corrigé {chemin} devrait exister")


if __name__ == "__main__":
    unittest.main()
