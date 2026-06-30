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

    def test_filtre_masque_meme_si_corrige_commente(self):
        """Les corrigés portent un commentaire en fin de ligne. Une solution propre
        de l'IA, sans ce commentaire, doit quand même être masquée."""
        corrige = ("int valeur_dans_char(int n) {\n"
                   "    char c = n;     /* n est rangé sur un octet */\n"
                   "    return c;       /* relu, par exemple 320 redonne 64 */\n"
                   "}\n")
        reponse = ("La solution :\n"
                   "char c = n;\n"
                   "return c;\n"
                   "Voilà.")
        filtre = filtre_solution(reponse, corrige)
        self.assertEqual(filtre.count("char c = n;"), 0)
        self.assertEqual(filtre.count("return c;"), 0)
        self.assertIn("La solution", filtre)
        self.assertIn("Voilà", filtre)

    def test_filtre_masque_malgre_les_espaces(self):
        """Une solution reproduite avec un espacement différent doit aussi être masquée."""
        corrige = "double calculer_y(double a, double b, double x) {\n    return a * x + b;\n}\n"
        reponse = "Essaie :\nreturn a*x+b;\nC'est tout."
        filtre = filtre_solution(reponse, corrige)
        self.assertNotIn("return a*x+b;", filtre)
        self.assertIn("Essaie", filtre)
        self.assertIn("C'est tout", filtre)


if __name__ == "__main__":
    unittest.main()
