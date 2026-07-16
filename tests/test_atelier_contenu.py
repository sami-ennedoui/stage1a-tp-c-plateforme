"""Tests de l'outil d'édition de contenu atelier_contenu.py.
Travaille toujours dans un répertoire temporaire, jamais dans le vrai contenu/."""
import json
import tempfile
import unittest
from pathlib import Path

import atelier_contenu as ac


def _lire_parcours(dossier: Path) -> dict:
    return json.loads((dossier / "parcours.json").read_text(encoding="utf-8"))


class TestNouveauParcours(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.racine = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_cree_parcours_vide(self):
        code = ac.commande_nouveau_parcours("mon_td", racine=self.racine)
        self.assertEqual(code, 0)
        donnees = _lire_parcours(self.racine / "mon_td")
        self.assertEqual(donnees, {"ordre": [], "mode": "isole"})

    def test_fichier_bien_forme(self):
        ac.commande_nouveau_parcours("mon_td", racine=self.racine)
        texte = (self.racine / "mon_td" / "parcours.json").read_text(encoding="utf-8")
        self.assertTrue(texte.endswith("}\n"))

    def test_refuse_nom_deja_pris(self):
        ac.commande_nouveau_parcours("mon_td", racine=self.racine)
        avant = _lire_parcours(self.racine / "mon_td")
        code = ac.commande_nouveau_parcours("mon_td", racine=self.racine)
        self.assertNotEqual(code, 0)
        self.assertEqual(_lire_parcours(self.racine / "mon_td"), avant)


if __name__ == "__main__":
    unittest.main()
