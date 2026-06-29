"""Tests unitaires pour EspaceProjet.

L'espace de travail vit dans un répertoire temporaire hors du dépôt suivi,
pour ne pas polluer git ni laisser de binaires commités.
"""
import tempfile
import unittest
from pathlib import Path

import chemins
from espace_projet import EspaceProjet


class TestEspaceProjetInitialisation(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.session = Path(self._tmpdir.name) / "espace_test"
        self.espace = EspaceProjet(chemins.PROJET_CORRIGE, self.session)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_initialiser_cree_la_copie(self):
        self.assertFalse(self.session.exists())
        self.espace.initialiser()
        self.assertTrue(self.session.exists())
        self.assertTrue(self.espace.dossier_snake.exists())
        self.assertTrue(self.espace.build_sh.exists())

    def test_initialiser_ne_recopie_pas_si_deja_present(self):
        """La deuxième initialisation ne doit pas effacer les modifications de l'étudiant."""
        self.espace.initialiser()
        marqueur = self.session / "marqueur.txt"
        marqueur.write_text("present", encoding="utf-8")
        self.espace.initialiser()
        self.assertTrue(marqueur.exists(), "initialiser() a effacé la copie existante")

    def test_reinitialiser_restaure_la_source(self):
        self.espace.initialiser()
        original = self.espace.lire_fichier("SNAKE/GestionJeu.c")
        self.espace.ecrire_fichier("SNAKE/GestionJeu.c", "/* cassé volontairement */\n")
        self.espace.reinitialiser()
        restaure = self.espace.lire_fichier("SNAKE/GestionJeu.c")
        self.assertEqual(restaure, original,
                         "reinitialiser() n'a pas restauré le fichier depuis la source")

    def test_reinitialiser_cree_si_absent(self):
        self.assertFalse(self.session.exists())
        self.espace.reinitialiser()
        self.assertTrue(self.session.exists())


class TestEspaceProjetFichiers(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.session = Path(self._tmpdir.name) / "espace_fichiers"
        self.espace = EspaceProjet(chemins.PROJET_CORRIGE, self.session)
        self.espace.initialiser()

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_ecrire_puis_lire_round_trip(self):
        contenu = "int x = 42; /* test */\n"
        self.espace.ecrire_fichier("SNAKE/GestionJeu.c", contenu)
        lu = self.espace.lire_fichier("SNAKE/GestionJeu.c")
        self.assertEqual(lu, contenu)

    def test_lire_fichier_source_intact(self):
        """Le fichier corrigé dans la source et la copie initialisée doivent être identiques."""
        original = (chemins.PROJET_CORRIGE / "SNAKE" / "GestionJeu.c").read_text(encoding="utf-8")
        copie = self.espace.lire_fichier("SNAKE/GestionJeu.c")
        self.assertEqual(original, copie)


class TestEspaceProjetChemins(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.session = Path(self._tmpdir.name) / "espace_chemins"
        self.espace = EspaceProjet(chemins.PROJET_CORRIGE, self.session)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_chemin_racine(self):
        self.assertEqual(self.espace.chemin_racine, self.session)

    def test_build_sh_pointe_dans_la_copie(self):
        self.assertEqual(self.espace.build_sh, self.session / "build.sh")

    def test_dossier_snake_pointe_dans_la_copie(self):
        self.assertEqual(self.espace.dossier_snake, self.session / "SNAKE")


if __name__ == "__main__":
    unittest.main()
