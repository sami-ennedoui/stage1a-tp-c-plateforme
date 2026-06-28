import unittest
import tempfile
from pathlib import Path
import chemins
from modele_etape import charger_parcours
from progression import (Progression, charger, sauver, etape_deverrouillee,
                         valider, cran_disponible)


class TestProgression(unittest.TestCase):
    def setUp(self):
        self.parcours = charger_parcours(chemins.CONTENU)
        self.p1, self.j1 = self.parcours[0], self.parcours[1]

    def test_depart_seule_premiere_deverrouillee(self):
        prog = Progression(etapes_faites=[], cran_max=0)
        self.assertTrue(etape_deverrouillee(self.p1, self.parcours, prog))
        self.assertFalse(etape_deverrouillee(self.j1, self.parcours, prog))
        self.assertEqual(cran_disponible(prog), 0)

    def test_valider_debloque_la_suite_et_le_cran(self):
        prog = valider(self.p1, Progression(etapes_faites=[], cran_max=0))
        self.assertIn("perso_P1", prog.etapes_faites)
        self.assertEqual(prog.cran_max, 1)
        self.assertTrue(etape_deverrouillee(self.j1, self.parcours, prog))

    def test_sauver_puis_charger(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "p.json"
            sauver(Progression(["perso_P1"], 1), f)
            relu = charger(f)
            self.assertEqual(relu.etapes_faites, ["perso_P1"])
            self.assertEqual(relu.cran_max, 1)

    def test_charger_absent_rend_vierge(self):
        relu = charger(Path("/tmp/nexiste_pas_42.json"))
        self.assertEqual(relu.etapes_faites, [])
        self.assertEqual(relu.cran_max, 0)


if __name__ == "__main__":
    unittest.main()
