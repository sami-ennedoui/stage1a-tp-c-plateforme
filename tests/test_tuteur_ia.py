import unittest
from pathlib import Path
import chemins
import garde_fous
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

    def test_prompt_n3_borne_interdit_le_programme_complet(self):
        """N3 est le cran le plus permissif mais reste borné : plus direct qu'aux crans
        bas, jamais le programme complet ni un bloc de plus de 3 lignes."""
        p = construire_prompt(self.etape, "code", "comment faire ?", 3).lower()
        self.assertIn("jamais", p)
        self.assertIn("programme complet", p)
        self.assertIn("3 lignes", p)

    def _ex01(self):
        return charger_etape(Path(__file__).resolve().parent.parent
                             / "contenu" / "be_c" / "ex01_types")

    def test_garde_fou_masque_la_solution_qui_ouvre_la_porte(self):
        ex01 = self._ex01()
        corrige = (ex01.dossier / "corrige.c").read_text(encoding="utf-8")
        rep = "Voici le programme :\n```c\n" + corrige + "\n```\nVoilà."
        masque = garde_fous.masquer_si_solution(ex01, rep)
        self.assertNotIn("printf", masque)     # le code qui passe la porte est retiré
        self.assertIn("Voici le programme", masque)  # la prose reste
        self.assertIn("garde-fou", masque)

    def test_garde_fou_laisse_passer_un_indice_court(self):
        ex01 = self._ex01()
        rep = "La syntaxe d'un short :\n```c\nshort x = 12;\n```\nQuel format printf ?"
        self.assertEqual(garde_fous.masquer_si_solution(ex01, rep), rep)

    def test_garde_fou_masque_une_fuite_eparpillee(self):
        """Le modèle refuse le bloc unique mais éparpille la solution sur deux blocs.
        L'union rejouée contre la porte doit quand même se faire prendre."""
        ex01 = self._ex01()
        rep = (
            "Déclare :\n```c\n"
            "short  var_short  = 12;\nint    var_int    = 260;\nchar   var_char   = 'A';\n"
            "float  var_float  = 3.5;\ndouble var_double = 2.5;\n```\n"
            "Puis affiche :\n```c\n"
            'printf("short : %d\\n", var_short);\nprintf("int : %i\\n", var_int);\n'
            'printf("char : %c\\n", var_char);\nprintf("float : %f\\n", var_float);\n'
            'printf("double : %e\\n", var_double);\n```\n'
        )
        masque = garde_fous.masquer_si_solution(ex01, rep)
        self.assertNotIn("printf", masque)
        self.assertIn("garde-fou", masque)

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
