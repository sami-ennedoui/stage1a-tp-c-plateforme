"""Tests unitaires pour porte_logique et construire_et_jouer_projet.

Tous les espaces de travail vivent dans des répertoires temporaires hors du dépôt suivi,
pour ne pas polluer git ni commettre de binaires.
"""
import tempfile
import unittest
from pathlib import Path

import chemins
from espace_projet import EspaceProjet
from executeur import construire_et_jouer_projet, porte_logique

# Sources logiques nécessaires à la compilation du harnais test_deplacement.
SOURCES_DEPLACEMENT = [
    "SNAKE/GestionJeu.c",
    "SNAKE/VariablesGlobales.c",
    "SNAKE/InitialisationJeu.c",
]
HARNAIS_DEPLACEMENT = chemins.PROJET_CORRIGE / "tests_logique" / "test_deplacement.c"


class TestPorteLogique(unittest.TestCase):
    """Prouve que porte_logique compile et exécute réellement, et que le code de sortie fait foi."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        session = Path(self._tmpdir.name) / "espace_porte"
        self.espace = EspaceProjet(chemins.PROJET_CORRIGE, session)
        self.espace.initialiser()
        # Lit le GestionJeu.c corrigé depuis l'espace initialisé (copie fidèle de la source).
        self.corrige = self.espace.lire_fichier("SNAKE/GestionJeu.c")

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_corrige_passe_la_porte(self):
        """Le fichier GestionJeu.c corrigé doit faire passer le harnais test_deplacement (exit 0)."""
        r = porte_logique(
            self.espace,
            "SNAKE/GestionJeu.c",
            self.corrige,
            HARNAIS_DEPLACEMENT,
            SOURCES_DEPLACEMENT,
        )
        self.assertTrue(r.ok, "Le fichier corrigé aurait dû passer la porte.\n" + r.sortie)

    def test_version_cassee_echoue(self):
        """Un GestionJeu.c volontairement cassé doit faire échouer le harnais (exit non nul)."""
        # On remplace GestionJeu.c par un fichier qui ne définit pas SP_Avancer_Serpent.
        # Le harnais de test échouera à la liaison : undefined reference.
        casse = "/* cassé volontairement : aucune fonction définie */\nint x = 42;\n"
        r = porte_logique(
            self.espace,
            "SNAKE/GestionJeu.c",
            casse,
            HARNAIS_DEPLACEMENT,
            SOURCES_DEPLACEMENT,
        )
        self.assertFalse(r.ok, "Un fichier cassé aurait dû faire échouer la porte.\n" + r.sortie)


class TestConstruireEtJouerProjet(unittest.TestCase):
    """Prouve que le build du projet complet réussit et produit un binaire."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        session = Path(self._tmpdir.name) / "espace_build"
        self.espace = EspaceProjet(chemins.PROJET_CORRIGE, session)
        self.espace.initialiser()

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_build_reussit_et_binaire_present(self):
        """Le build.sh doit compiler sans erreur et produire un binaire 'snake' dans SNAKE/.
        On passe lancer=False pour ne pas ouvrir de fenêtre SDL pendant les tests."""
        r = construire_et_jouer_projet(self.espace, lancer=False)
        self.assertTrue(r.ok, "Le build a échoué alors que la source est le corrigé.\n" + r.sortie)
        binaire = self.espace.dossier_snake / "snake"
        self.assertTrue(
            binaire.exists(),
            f"Le binaire est introuvable à l'emplacement attendu : {binaire}",
        )


if __name__ == "__main__":
    unittest.main()
