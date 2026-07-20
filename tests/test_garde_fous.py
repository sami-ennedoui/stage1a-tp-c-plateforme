"""Tests du garde-fou structurel : verdict de porte, masquage, et branchement au tuteur.

Le module n'avait aucun test, et c'est precisement ce qui a laisse passer deux defauts :
son appel avait disparu de tuteur_ia lors de la separation des lignees, et son rattrapage
d'exception concluait « ce code n'ouvre pas la porte » a partir d'une compilation qui
n'avait pas eu lieu. Les deux cas sont couverts ici.
"""
import types
import unittest
from unittest import mock

import chemins
import garde_fous
import modele_etape
import tuteur_ia


def _etape(id_etape="ex01_types"):
    for e in modele_etape.charger_parcours(chemins.contenu_racine("be_c")):
        if e.id == id_etape:
            return e
    raise AssertionError(f"etape {id_etape} absente du parcours be_c")


def _en_bloc(code: str) -> str:
    return f"Voici comment faire.\n\n```c\n{code}\n```\n\nBonne chance."


class TestExtraction(unittest.TestCase):
    def test_extrait_chaque_bloc(self):
        r = "avant\n```c\nUN\n```\nentre\n```\nDEUX\n```\napres"
        self.assertEqual(garde_fous.extraire_blocs_c(r), ["UN\n", "DEUX\n"])

    def test_sans_bloc_la_porte_est_fermee(self):
        self.assertEqual(garde_fous.verdict(_etape(), "juste de la prose"), "ferme")


class TestVerdictReel(unittest.TestCase):
    """Compile pour de vrai : c'est le comportement qui juge, pas le vocabulaire."""

    def test_le_corrige_ouvre_la_porte(self):
        e = _etape()
        corrige = (e.dossier / "corrige.c").read_text(encoding="utf-8")
        self.assertEqual(garde_fous.verdict(e, _en_bloc(corrige)), "ouvre")

    def test_un_code_hors_sujet_laisse_la_porte_fermee(self):
        e = _etape()
        inoffensif = '#include <stdio.h>\nint main(void){ printf("bonjour"); return 0; }\n'
        self.assertEqual(garde_fous.verdict(e, _en_bloc(inoffensif)), "ferme")

    def test_masquage_retire_le_corrige_et_garde_la_prose(self):
        e = _etape()
        corrige = (e.dossier / "corrige.c").read_text(encoding="utf-8")
        sortie = garde_fous.masquer_si_solution(e, _en_bloc(corrige))
        self.assertNotIn("var_double", sortie)
        self.assertIn("Bonne chance", sortie)
        self.assertIn("c'est donc la solution", sortie)

    def test_reponse_inoffensive_rendue_telle_quelle(self):
        e = _etape()
        r = _en_bloc('printf("%c", c);')
        self.assertEqual(garde_fous.masquer_si_solution(e, r), r)


class TestIndecidable(unittest.TestCase):
    """Sans compilateur, le garde-fou doit se taire en masquant, pas en laissant passer."""

    def _sans_compilateur(self):
        return mock.patch.object(garde_fous.executeur, "porte_programme",
                                 side_effect=OSError("gcc introuvable"))

    def test_verdict_indecidable_et_non_ferme(self):
        e = _etape()
        with self._sans_compilateur():
            self.assertEqual(garde_fous.verdict(e, _en_bloc("peu importe")), "indecidable")

    def test_le_code_est_masque_quand_on_ne_peut_pas_juger(self):
        # Non-regression du fail-open : avant, l'exception rendait False, le code
        # passait entier, et le garde-fou se croyait actif.
        e = _etape()
        with self._sans_compilateur():
            sortie = garde_fous.masquer_si_solution(e, _en_bloc("SECRET_A_NE_PAS_LAISSER"))
        self.assertNotIn("SECRET_A_NE_PAS_LAISSER", sortie)
        self.assertIn("par prudence", sortie)

    def test_indecidable_n_est_pas_annonce_comme_une_solution(self):
        e = _etape()
        with self._sans_compilateur():
            sortie = garde_fous.masquer_si_solution(e, _en_bloc("peu importe"))
        self.assertNotIn("c'est donc la solution", sortie)

    def test_solution_ouvre_la_porte_reste_faux_si_indecidable(self):
        e = _etape()
        with self._sans_compilateur():
            self.assertFalse(garde_fous.solution_ouvre_la_porte(e, _en_bloc("x")))


class TestBranchementAuTuteur(unittest.TestCase):
    """Le defaut trouve le 20 juillet : garde_fous existait mais tuteur_ia ne l'appelait
    plus, alors que docs/04-doc-technique.md le decrit comme l'etape 1 de la chaine."""

    # Commande bidon que _commande() rendra, et seule chose que l'aiguillage intercepte.
    SENTINELLE = ["--moteur-de-test--"]

    def _reponse_du_moteur(self, texte):
        """Intercepte le seul appel au moteur, en laissant passer tous les autres.

        « tuteur_ia.subprocess » n'est pas une copie locale, c'est le module subprocess
        lui-meme, celui qu'executeur utilise pour appeler gcc. Un patch large coupait donc
        aussi la compilation : le garde-fou rendait « indecidable » et le test echouait en
        accusant le code alors que le defaut etait dans le test. On n'intercepte que la
        commande sentinelle, le reste part au vrai subprocess.run."""
        vrai_run = tuteur_ia.subprocess.run
        faux = types.SimpleNamespace(returncode=0, stdout=texte, stderr="")

        def aiguillage(commande, *args, **kwargs):
            if list(commande) == self.SENTINELLE:
                return faux
            return vrai_run(commande, *args, **kwargs)

        return mock.patch.object(tuteur_ia.subprocess, "run", side_effect=aiguillage)

    def test_demander_aide_masque_une_reponse_qui_donne_la_solution(self):
        # Assertions choisies apres verification, et pas au juge : exiger la
        # disparition de « var_double » ne prouve rien du tout, le filtre lexical
        # l'obtient deja seul quand le garde-fou est debranche. Ce qui discrimine
        # c'est QUI a masque. On exige donc le message du garde-fou structurel,
        # et l'absence du marqueur lexical -- sa presence voudrait dire que le
        # garde-fou n'a servi que de rattrapage ligne a ligne.
        # Exiger le message « solution » plutot qu'un simple « garde-fou » n'est
        # pas cosmetique non plus : sans compilateur le garde-fou repond
        # « indecidable », et le test passerait alors sans avoir rien compile.
        e = _etape()
        corrige = (e.dossier / "corrige.c").read_text(encoding="utf-8")
        with mock.patch.object(tuteur_ia, "_moteur_choisi", return_value="faux-moteur"), \
             mock.patch.object(tuteur_ia, "_commande", return_value=self.SENTINELLE), \
             self._reponse_du_moteur(_en_bloc(corrige)):
            sortie = tuteur_ia.demander_aide(e, "", "comment faire ?", 3)
        self.assertIn("c'est donc la solution", sortie)
        self.assertNotIn(tuteur_ia.MARQUE_MASQUE, sortie)
        self.assertNotIn("var_double", sortie)


if __name__ == "__main__":
    unittest.main()
