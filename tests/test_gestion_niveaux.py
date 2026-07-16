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
        # Le parcours est niché sous une racine de contenu à lui, sans quoi
        # _id_pris_ailleurs verrait les autres tmpXXXX du dossier temp système
        # comme des parcours voisins (l'unicité d'id se lit sur tout contenu/).
        self.dossier = Path(self._tmp.name) / "parcours"
        self.dossier.mkdir()
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

    def test_edition_fichiers_et_meta_aller_retour(self):
        gestion_niveaux.ajouter_niveau(self.dossier, "ex01", "Titre initial")
        gestion_niveaux.ecrire_fichier_niveau(self.dossier, "ex01", "enonce.md", "# Nouvel énoncé")
        gestion_niveaux.ecrire_fichier_niveau(self.dossier, "ex01", "corrige.c", "int main(){return 0;}")
        self.assertEqual(
            gestion_niveaux.lire_fichier_niveau(self.dossier, "ex01", "enonce.md"),
            "# Nouvel énoncé")
        meta = gestion_niveaux.lire_meta(self.dossier, "ex01")
        meta["titre"] = "Titre modifié"
        meta["sortie_attendue"] = ["ligne 1", "ligne 2"]
        gestion_niveaux.ecrire_meta(self.dossier, "ex01", meta)
        relu = gestion_niveaux.lire_meta(self.dossier, "ex01")
        self.assertEqual(relu["titre"], "Titre modifié")
        self.assertEqual(relu["sortie_attendue"], ["ligne 1", "ligne 2"])

    def test_edition_niveau_absent_leve(self):
        with self.assertRaises(ValueError):
            gestion_niveaux.lire_meta(self.dossier, "fantome")


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


class TestUniciteIdEntreParcours(unittest.TestCase):
    """Un id doit être unique dans tout contenu/, pas dans son seul parcours : le
    compagnon ne reçoit que l'id d'une étape et noterait deux homonymes l'un pour
    l'autre. La GUI (ajouter/réattacher) ne doit donc pas créer d'homonyme. Miroir de
    la garde de atelier_contenu.commande_nouvelle_etape."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.racine = Path(self._tmp.name)         # racine de contenu factice
        self.be_c = self.racine / "be_c"
        self.perso = self.racine / "perso"
        for d in (self.be_c, self.perso):
            d.mkdir()
            _parcours_neuf(d)
        gestion_niveaux.ajouter_niveau(self.be_c, "ex05_rectangle", "Rectangle")

    def tearDown(self):
        self._tmp.cleanup()

    def test_ajout_refuse_un_id_actif_dans_un_autre_parcours(self):
        with self.assertRaises(ValueError) as ctx:
            gestion_niveaux.ajouter_niveau(self.perso, "ex05_rectangle", "Homonyme")
        self.assertIn("be_c", str(ctx.exception))
        # rien ne doit avoir été créé dans perso
        self.assertFalse((self.perso / "ex05_rectangle").exists())
        self.assertEqual(gestion_niveaux.lister_niveaux(self.perso), [])

    def test_ajout_refuse_un_id_detache_dans_un_autre_parcours(self):
        # détaché dans be_c : le dossier reste, la collision serait juste différée
        gestion_niveaux.retirer_niveau(self.be_c, "ex05_rectangle")
        with self.assertRaises(ValueError):
            gestion_niveaux.ajouter_niveau(self.perso, "ex05_rectangle", "Homonyme")

    def test_ajout_autorise_un_id_libre_ailleurs(self):
        chemin = gestion_niveaux.ajouter_niveau(self.perso, "ex06_cercle", "Cercle")
        self.assertTrue(chemin.exists())
        self.assertEqual(gestion_niveaux.lister_niveaux(self.perso), ["ex06_cercle"])

    def test_reattacher_refuse_si_homonyme_actif_ailleurs(self):
        # Deux homonymes sur disque ne peuvent venir que d'ailleurs (CLI, branche,
        # montage manuel) puisque la GUI les refuse désormais. On plante donc à la
        # main un ex05 détaché dans perso, be_c gardant le sien actif (setUp).
        detache = self.perso / "ex05_rectangle"
        detache.mkdir()
        (detache / "meta.json").write_text(
            json.dumps({"id": "ex05_rectangle", "titre": "Intrus"}) + "\n",
            encoding="utf-8")
        with self.assertRaises(ValueError) as ctx:
            gestion_niveaux.reattacher_niveau(self.perso, "ex05_rectangle")
        self.assertIn("be_c", str(ctx.exception))
        # perso ne l'a pas repris malgré tout
        self.assertEqual(gestion_niveaux.lister_niveaux(self.perso), [])


class TestSynchroniserNotation(unittest.TestCase):
    """La GUI doit tenir compagnon/etapes_notees.json à jour quand elle touche le
    parcours noté, sinon retirer un niveau plafonne la note de toute la promo."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        racine = Path(self._tmp.name)          # racine de contenu factice
        self.dossier = racine / "be_c"         # parcours noté factice
        self.dossier.mkdir()
        _parcours_neuf(self.dossier)
        for i in "abc":
            gestion_niveaux.ajouter_niveau(self.dossier, f"ex_{i}", i.upper())
        self.notation = racine / "etapes_notees.json"
        from compagnon import notation
        notation.ecrire("be_c", ["ex_a", "ex_b", "ex_c"], self.notation)

    def tearDown(self):
        self._tmp.cleanup()

    def test_retrait_realigne_la_liste_et_previent(self):
        from compagnon import notation
        gestion_niveaux.retirer_niveau(self.dossier, "ex_b")
        message = gestion_niveaux.synchroniser_notation(self.dossier, self.notation)
        self.assertIsNotNone(message)
        self.assertIn("redéployé", message)
        self.assertEqual(notation.charger(self.notation), ["ex_a", "ex_c"])

    def test_ajout_ajoute_a_la_liste_notee(self):
        from compagnon import notation
        gestion_niveaux.ajouter_niveau(self.dossier, "ex_d", "D")
        gestion_niveaux.synchroniser_notation(self.dossier, self.notation)
        self.assertEqual(notation.charger(self.notation),
                         ["ex_a", "ex_b", "ex_c", "ex_d"])

    def test_deja_aligne_ne_dit_rien(self):
        self.assertIsNone(
            gestion_niveaux.synchroniser_notation(self.dossier, self.notation))

    def test_autre_parcours_note_reste_intact(self):
        from compagnon import notation
        notation.ecrire("un_autre", ["x"], self.notation)
        gestion_niveaux.retirer_niveau(self.dossier, "ex_b")
        message = gestion_niveaux.synchroniser_notation(self.dossier, self.notation)
        self.assertIsNone(message)
        self.assertEqual(notation.charger(self.notation), ["x"])

    def test_pas_de_compagnon_pas_d_erreur(self):
        absent = Path(self._tmp.name) / "pas_la" / "etapes_notees.json"
        self.assertIsNone(
            gestion_niveaux.synchroniser_notation(self.dossier, absent))

    def test_refuse_d_ecrire_la_vraie_notation_depuis_une_racine_de_test(self):
        # Le piège vécu côté ligne de commande : un parcours temporaire nommé comme le
        # parcours noté ne doit jamais écraser la vraie notation du dépôt.
        import atelier_contenu
        reel = atelier_contenu.FICHIER_NOTATION
        avant = reel.read_bytes() if reel.exists() else None
        message = gestion_niveaux.synchroniser_notation(self.dossier, reel)
        self.assertIsNone(message)
        apres = reel.read_bytes() if reel.exists() else None
        self.assertEqual(avant, apres)


if __name__ == "__main__":
    unittest.main()
