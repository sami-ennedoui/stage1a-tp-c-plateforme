import os
import unittest
from unittest import mock

import chemins
import tuteur_ia
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

    def test_prompt_sans_historique_n_en_parle_pas(self):
        p = construire_prompt(self.etape, "code", "ma question", 0)
        self.assertNotIn("Échanges précédents", p)

    def test_prompt_injecte_l_historique(self):
        hist = [("pourquoi 320 donne 64 ?", "reflechis au nombre de bits")]
        p = construire_prompt(self.etape, "code", "et 256 alors ?", 0, historique=hist)
        self.assertIn("Échanges précédents", p)
        self.assertIn("pourquoi 320 donne 64 ?", p)
        self.assertIn("reflechis au nombre de bits", p)
        self.assertIn("et 256 alors ?", p)      # la question courante reste présente

    def test_reponse_est_erreur(self):
        self.assertTrue(tuteur_ia.reponse_est_erreur(tuteur_ia.ERR_TIMEOUT))
        self.assertTrue(tuteur_ia.reponse_est_erreur(tuteur_ia.ERR_INDISPONIBLE))
        self.assertFalse(tuteur_ia.reponse_est_erreur("Voici une vraie piste d'aide."))

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


class TestMoteur(unittest.TestCase):
    """Sélection du moteur IA et construction de la commande selon le moteur."""

    def test_commande_claude_utilise_p(self):
        self.assertEqual(tuteur_ia._commande("claude", "PROMPT"),
                         ["claude", "-p", "PROMPT"])

    def test_commande_codex_utilise_exec(self):
        self.assertEqual(tuteur_ia._commande("codex", "PROMPT"),
                         ["codex", "exec", "--skip-git-repo-check", "PROMPT"])

    def test_atelier_ai_force_le_moteur_si_present(self):
        with mock.patch.dict(os.environ, {"ATELIER_AI": "codex"}, clear=True), \
             mock.patch("tuteur_ia.shutil.which", lambda b: "/x/" + b):
            self.assertEqual(tuteur_ia._moteur_choisi(), "codex")

    def test_atelier_ai_ignore_si_absent_du_path(self):
        with mock.patch.dict(os.environ, {"ATELIER_AI": "codex"}, clear=True), \
             mock.patch("tuteur_ia.shutil.which", lambda b: None):
            self.assertIsNone(tuteur_ia._moteur_choisi())

    def test_autodetection_prefere_claude(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch("tuteur_ia.shutil.which",
                        lambda b: "/x/" + b if b in ("claude", "codex") else None):
            self.assertEqual(tuteur_ia._moteur_choisi(), "claude")

    def test_autodetection_retombe_sur_codex(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch("tuteur_ia.shutil.which",
                        lambda b: "/x/codex" if b == "codex" else None):
            self.assertEqual(tuteur_ia._moteur_choisi(), "codex")

    def test_aucun_moteur_disponible(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch("tuteur_ia.shutil.which", lambda b: None):
            self.assertIsNone(tuteur_ia._moteur_choisi())
            self.assertFalse(tuteur_ia.moteur_disponible())


if __name__ == "__main__":
    unittest.main()
