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


class TestNouvelleEtape(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.racine = Path(self._tmp.name)
        ac.commande_nouveau_parcours("be_c", racine=self.racine)
        for id_etape in ("ex01", "ex02"):
            ac.commande_nouvelle_etape("be_c", id_etape, titre=f"Titre {id_etape}",
                                       racine=self.racine)

    def tearDown(self):
        self._tmp.cleanup()

    def test_ajout_a_la_fin_par_defaut(self):
        ac.commande_nouvelle_etape("be_c", "ex03", titre="Titre ex03", racine=self.racine)
        donnees = _lire_parcours(self.racine / "be_c")
        self.assertEqual(donnees["ordre"], ["ex01", "ex02", "ex03"])

    def test_insertion_apres(self):
        ac.commande_nouvelle_etape("be_c", "ex_milieu", titre="Titre milieu",
                                   apres="ex01", racine=self.racine)
        donnees = _lire_parcours(self.racine / "be_c")
        self.assertEqual(donnees["ordre"], ["ex01", "ex_milieu", "ex02"])

    def test_cree_les_fichiers_du_squelette(self):
        dossier = self.racine / "be_c" / "ex01"
        for nom_fichier in ("meta.json", "enonce.md", "starter.c", "corrige.c"):
            self.assertTrue((dossier / nom_fichier).exists(), nom_fichier)

    def test_meta_correcte(self):
        meta = json.loads((self.racine / "be_c" / "ex01" / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["id"], "ex01")
        self.assertEqual(meta["titre"], "Titre ex01")
        self.assertEqual(meta["type"], "programme")
        self.assertEqual(meta["mode"], "programme")
        self.assertEqual(meta["fichier_edite"], "programme.c")
        self.assertEqual(meta["cran_debloque"], 1)

    def test_cran_personnalise(self):
        ac.commande_nouvelle_etape("be_c", "ex03", titre="Titre ex03", cran=2, racine=self.racine)
        meta = json.loads((self.racine / "be_c" / "ex03" / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["cran_debloque"], 2)

    def test_refuse_parcours_inexistant(self):
        code = ac.commande_nouvelle_etape("inconnu", "ex03", titre="X", racine=self.racine)
        self.assertNotEqual(code, 0)

    def test_refuse_id_deja_pris(self):
        avant = _lire_parcours(self.racine / "be_c")
        code = ac.commande_nouvelle_etape("be_c", "ex01", titre="Autre", racine=self.racine)
        self.assertNotEqual(code, 0)
        self.assertEqual(_lire_parcours(self.racine / "be_c"), avant)

    def test_refuse_id_invalide(self):
        avant = _lire_parcours(self.racine / "be_c")
        for mauvais_id in ("Ex-03", "ex 03", "ex/03", "ÉTAPE"):
            with self.subTest(id=mauvais_id):
                code = ac.commande_nouvelle_etape("be_c", mauvais_id, titre="X", racine=self.racine)
                self.assertNotEqual(code, 0)
        self.assertEqual(_lire_parcours(self.racine / "be_c"), avant)

    def test_refuse_apres_absent(self):
        avant = _lire_parcours(self.racine / "be_c")
        code = ac.commande_nouvelle_etape("be_c", "ex03", titre="X", apres="ex_fantome",
                                          racine=self.racine)
        self.assertNotEqual(code, 0)
        self.assertEqual(_lire_parcours(self.racine / "be_c"), avant)
        self.assertFalse((self.racine / "be_c" / "ex03").exists())


if __name__ == "__main__":
    unittest.main()
