import json
import tempfile
import unittest
from pathlib import Path

import gestion_niveaux
from modele_etape import charger_parcours


def _parcours_neuf(dossier: Path):
    """Crée un parcours.json vide dans un dossier temporaire."""
    (dossier / "parcours.json").write_text(
        json.dumps({"ordre": [], "mode": "isole"}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")


class TestGestionNiveaux(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dossier = Path(self._tmp.name)
        _parcours_neuf(self.dossier)

    def tearDown(self):
        self._tmp.cleanup()

    def test_ajout_cree_dossier_gabarits_et_ordre(self):
        gestion_niveaux.ajouter_niveau(
            self.dossier, "ex01_types", "Exercice 1",
            mode="programme", sortie_attendue=["int : 260"])
        d = self.dossier / "ex01_types"
        for nom in ("meta.json", "enonce.md", "starter.c", "corrige.c"):
            self.assertTrue((d / nom).exists(), f"{nom} manquant")
        self.assertEqual(gestion_niveaux.lister_niveaux(self.dossier), ["ex01_types"])
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["titre"], "Exercice 1")
        self.assertEqual(meta["sortie_attendue"], ["int : 260"])
        # le niveau créé est lisible par le modèle de l'appli
        etapes = charger_parcours(self.dossier)
        self.assertEqual([e.id for e in etapes], ["ex01_types"])

    def test_ajout_refuse_doublon(self):
        gestion_niveaux.ajouter_niveau(self.dossier, "ex01", "Un")
        with self.assertRaises(ValueError):
            gestion_niveaux.ajouter_niveau(self.dossier, "ex01", "Un bis")

    def test_ajout_refuse_id_invalide(self):
        for mauvais in ("Ex01", "01ex", "ex 1", "ex-1", ""):
            with self.assertRaises(ValueError):
                gestion_niveaux.ajouter_niveau(self.dossier, mauvais, "Titre")

    def test_retrait_detache_sans_effacer(self):
        gestion_niveaux.ajouter_niveau(self.dossier, "ex01", "Un")
        gestion_niveaux.retirer_niveau(self.dossier, "ex01")
        self.assertEqual(gestion_niveaux.lister_niveaux(self.dossier), [])
        # le dossier reste sur le disque, niveau détaché
        self.assertTrue((self.dossier / "ex01" / "meta.json").exists())
        self.assertEqual(gestion_niveaux.dossiers_detaches(self.dossier), ["ex01"])

    def test_reattacher_un_detache(self):
        gestion_niveaux.ajouter_niveau(self.dossier, "ex01", "Un")
        gestion_niveaux.retirer_niveau(self.dossier, "ex01")
        gestion_niveaux.reattacher_niveau(self.dossier, "ex01")
        self.assertEqual(gestion_niveaux.lister_niveaux(self.dossier), ["ex01"])

    def test_ajout_refuse_ecraser_dossier_detache(self):
        gestion_niveaux.ajouter_niveau(self.dossier, "ex01", "Un")
        gestion_niveaux.retirer_niveau(self.dossier, "ex01")
        with self.assertRaises(ValueError):
            gestion_niveaux.ajouter_niveau(self.dossier, "ex01", "Un neuf")

    def test_deplacer_change_l_ordre(self):
        for i in "abc":
            gestion_niveaux.ajouter_niveau(self.dossier, f"ex_{i}", i.upper())
        gestion_niveaux.deplacer_niveau(self.dossier, "ex_c", -1)
        self.assertEqual(gestion_niveaux.lister_niveaux(self.dossier),
                         ["ex_a", "ex_c", "ex_b"])
        gestion_niveaux.deplacer_niveau(self.dossier, "ex_a", -1)  # déjà en tête, sans effet
        self.assertEqual(gestion_niveaux.lister_niveaux(self.dossier),
                         ["ex_a", "ex_c", "ex_b"])

    def test_ajout_a_une_position(self):
        for i in "abc":
            gestion_niveaux.ajouter_niveau(self.dossier, f"ex_{i}", i.upper())
        gestion_niveaux.ajouter_niveau(self.dossier, "ex_z", "Z", position=1)
        self.assertEqual(gestion_niveaux.lister_niveaux(self.dossier),
                         ["ex_a", "ex_z", "ex_b", "ex_c"])


class TestAuteur(unittest.TestCase):
    def setUp(self):
        # redirige le fichier de config vers un temporaire, sans toucher au dépôt
        import chemins
        self._tmp = tempfile.TemporaryDirectory()
        self._sauve = chemins.AUTEUR_FICHIER
        chemins.AUTEUR_FICHIER = Path(self._tmp.name) / "auteur.json"

    def tearDown(self):
        import chemins
        chemins.AUTEUR_FICHIER = self._sauve
        self._tmp.cleanup()

    def test_defaut_puis_changement(self):
        import auteur
        self.assertTrue(auteur.verifier(auteur.MDP_DEFAUT))
        auteur.definir("nouveau-secret")
        self.assertTrue(auteur.verifier("nouveau-secret"))
        self.assertFalse(auteur.verifier(auteur.MDP_DEFAUT))

    def test_mot_de_passe_vide_refuse(self):
        import auteur
        with self.assertRaises(ValueError):
            auteur.definir("")


if __name__ == "__main__":
    unittest.main()
