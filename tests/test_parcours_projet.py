"""Vérifie le parcours projet sans interface : le squelette échoue aux portes logiques,
le corrigé les passe. Valide aussi que parcours.json et les meta.json sont bien formés."""
import shutil
import tempfile
import unittest
from pathlib import Path

import chemins
import executeur
from espace_projet import EspaceProjet
from modele_etape import charger_parcours_complet


class TestParcoursProjet(unittest.TestCase):

    def setUp(self):
        self.parcours = charger_parcours_complet(chemins.contenu_racine("projet"))
        self.tmp = Path(tempfile.mkdtemp(prefix="test_projet_"))
        self._compteur = 0

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_parcours_bien_forme(self):
        self.assertEqual(self.parcours.mode, "projet")
        self.assertEqual([e.id for e in self.parcours.etapes],
                         ["init", "deplacement", "capstone"])

    def test_capstone_est_une_porte_build(self):
        capstone = self.parcours.etapes[-1]
        self.assertEqual(capstone.porte, "build")
        self.assertIsNone(capstone.harnais)

    def _passe_les_portes(self, etape, code):
        """Vrai si ce code passe tous les harnais de l'étape, dans un espace neuf."""
        # chemin inexistant : initialiser() ne copie que si le dossier est absent
        self._compteur += 1
        session = self.tmp / f"esp_{self._compteur}"
        espace = EspaceProjet(chemins.PROJET_CORRIGE, session)
        espace.initialiser()
        for h in etape.harnais:
            r = executeur.porte_logique(
                espace, etape.fichier_edite, code, chemins.RACINE / h, etape.sources)
            if not r.ok:
                return False
        return True

    def test_squelette_echoue_corrige_passe(self):
        for etape in self.parcours.etapes:
            if etape.porte != "logique":
                continue
            squelette = (chemins.PROJET_SQUELETTE / etape.fichier_edite).read_text(encoding="utf-8")
            corrige = (chemins.PROJET_CORRIGE / etape.fichier_edite).read_text(encoding="utf-8")
            with self.subTest(etape=etape.id):
                self.assertFalse(self._passe_les_portes(etape, squelette),
                                 f"{etape.id} : le squelette ne devrait pas passer la porte")
                self.assertTrue(self._passe_les_portes(etape, corrige),
                                f"{etape.id} : le corrigé devrait passer la porte")


if __name__ == "__main__":
    unittest.main()
