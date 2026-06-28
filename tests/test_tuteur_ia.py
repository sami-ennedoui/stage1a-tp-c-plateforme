import unittest
import chemins
from modele_etape import charger_etape
from tuteur_ia import construire_prompt, filtre_solution


class TestTuteur(unittest.TestCase):
    def setUp(self):
        self.etape = charger_etape(chemins.CONTENU / "perso_P1")

    def test_prompt_n0_interdit_le_code(self):
        p = construire_prompt(self.etape, "code", "comment faire ?", 0)
        self.assertIn("explique", p.lower())
        self.assertIn("sans donner", p.lower())

    def test_prompt_n1_propose_un_squelette(self):
        p = construire_prompt(self.etape, "code", "comment faire ?", 1)
        self.assertIn("squelette", p.lower())

    def test_prompt_n2_demande_de_justifier(self):
        p = construire_prompt(self.etape, "code", "comment faire ?", 2)
        self.assertIn("justifier", p.lower())

    def test_prompt_n3_est_libre(self):
        p = construire_prompt(self.etape, "code", "comment faire ?", 3)
        self.assertIn("libre", p.lower())

    def test_filtre_masque_la_ligne_solution(self):
        corrige = "void f(int* p){\n    *p_etat = MENU_PARAMETRAGE;\n}\n"
        reponse = ("Voici la correction :\n"
                   "    *p_etat = MENU_PARAMETRAGE;\n"
                   "et voilà, c'est tout.")
        filtre = filtre_solution(reponse, corrige)
        self.assertNotIn("*p_etat = MENU_PARAMETRAGE;", filtre)
        self.assertIn("Voici la correction", filtre)
        self.assertIn("c'est tout", filtre)


if __name__ == "__main__":
    unittest.main()
