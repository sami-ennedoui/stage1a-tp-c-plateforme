"""Bascule du tuteur et commande IA configurable.

Deux demandes du poste Linux. Les tests portent sur le comportement observable :
est-ce qu'une requete part, et avec quelle ligne de commande -- pas sur le fait
qu'un attribut vaut True.
"""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import chemins
import reglages
import tuteur_ia


class BaseReglages(unittest.TestCase):
    """Isole reglages.json dans un dossier jetable, comme tests/test_reglages.py."""

    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.patch = mock.patch.object(chemins, "REGLAGES_FICHIER",
                                       Path(self.d.name) / "reglages.json")
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.d.cleanup()


class TestReglagesTuteur(BaseReglages):
    def test_actif_par_defaut(self):
        self.assertTrue(reglages.tuteur_actif())

    def test_bascule_persiste(self):
        reglages.definir_tuteur_actif(False)
        self.assertFalse(reglages.tuteur_actif())
        reglages.definir_tuteur_actif(True)
        self.assertTrue(reglages.tuteur_actif())

    def test_la_bascule_ne_perd_pas_les_autres_reglages(self):
        reglages.definir_parcours("be_c")
        reglages.definir_tuteur_actif(False)
        reglages.definir_commande_ia("moteur --flag")
        self.assertEqual(reglages.dernier_parcours(), "be_c")
        self.assertFalse(reglages.tuteur_actif())
        self.assertEqual(reglages.commande_ia(), "moteur --flag")

    def test_commande_vide_par_defaut(self):
        self.assertEqual(reglages.commande_ia(), "")


class TestBasculeCoupeLaRequete(BaseReglages):
    """Le masquage des boutons est cosmetique ; c'est l'envoi qui doit s'arreter."""

    def _etape(self):
        import modele_etape
        return [e for e in modele_etape.charger_parcours(chemins.contenu_racine("be_c"))
                if e.id == "ex01_types"][0]

    def test_desactive_aucun_sous_processus_n_est_lance(self):
        reglages.definir_tuteur_actif(False)
        with mock.patch.object(tuteur_ia.subprocess, "run") as faux:
            reponse = tuteur_ia.demander_aide(self._etape(), "", "aide ?", 1)
        faux.assert_not_called()
        self.assertEqual(reponse, tuteur_ia.ERR_DESACTIVE)

    def test_le_message_de_desactivation_est_distinct_de_l_indisponibilite(self):
        # Un moteur absent est une panne, un tuteur coupe est une consigne : melanger
        # les deux enverrait l'etudiant chercher une reparation qui n'existe pas.
        self.assertNotEqual(tuteur_ia.ERR_DESACTIVE, tuteur_ia.ERR_INDISPONIBLE)
        self.assertTrue(tuteur_ia.reponse_est_erreur(tuteur_ia.ERR_DESACTIVE))

    def test_desactive_le_tuteur_n_est_pas_disponible(self):
        reglages.definir_tuteur_actif(False)
        self.assertFalse(tuteur_ia.tuteur_disponible())


class TestCommandePersonnalisee(BaseReglages):
    def test_sans_commande_l_auto_detection_joue(self):
        with mock.patch.dict(tuteur_ia.os.environ, {}, clear=True), \
             mock.patch.object(tuteur_ia.shutil, "which", side_effect=lambda n: "/x/" + n):
            self.assertEqual(tuteur_ia._moteur_choisi(), "claude")

    def test_la_commande_reglee_prend_le_pas(self):
        reglages.definir_commande_ia("mon-moteur --brut")
        with mock.patch.dict(tuteur_ia.os.environ, {}, clear=True), \
             mock.patch.object(tuteur_ia.shutil, "which", side_effect=lambda n: "/x/" + n):
            self.assertEqual(tuteur_ia._moteur_choisi(), tuteur_ia.MOTEUR_COMMANDE)
            self.assertEqual(tuteur_ia._commande(tuteur_ia.MOTEUR_COMMANDE, "QUESTION"),
                             ["mon-moteur", "--brut", "QUESTION"])

    def test_la_variable_d_environnement_l_emporte_sur_le_reglage(self):
        reglages.definir_commande_ia("celle-du-fichier")
        with mock.patch.dict(tuteur_ia.os.environ, {"ATELIER_AI_CMD": "celle-de-l-env"}), \
             mock.patch.object(tuteur_ia.shutil, "which", side_effect=lambda n: "/x/" + n):
            self.assertEqual(tuteur_ia.commande_personnalisee(), "celle-de-l-env")

    def test_marqueur_prompt_place_la_question_ou_on_veut(self):
        reglages.definir_commande_ia("moteur {prompt} --apres")
        with mock.patch.dict(tuteur_ia.os.environ, {}, clear=True):
            self.assertEqual(tuteur_ia._commande(tuteur_ia.MOTEUR_COMMANDE, "QUESTION"),
                             ["moteur", "QUESTION", "--apres"])

    def test_commande_dont_le_binaire_n_existe_pas_vaut_pas_de_moteur(self):
        # Doit se voir comme « pas de tuteur » et non exploser au premier clic.
        reglages.definir_commande_ia("binaire-qui-n-existe-pas --x")
        with mock.patch.dict(tuteur_ia.os.environ, {}, clear=True), \
             mock.patch.object(tuteur_ia.shutil, "which", return_value=None):
            self.assertIsNone(tuteur_ia._moteur_choisi())

    def test_guillemets_respectes_dans_la_commande(self):
        reglages.definir_commande_ia('"C:/mes outils/moteur.exe" --lent')
        with mock.patch.dict(tuteur_ia.os.environ, {}, clear=True):
            self.assertEqual(tuteur_ia._commande(tuteur_ia.MOTEUR_COMMANDE, "Q"),
                             ["C:/mes outils/moteur.exe", "--lent", "Q"])


if __name__ == "__main__":
    unittest.main()
