"""Tests de l'outil d'édition de contenu atelier_contenu.py.
Travaille toujours dans un répertoire temporaire, jamais dans le vrai contenu/."""
import json
import tempfile
import unittest
from pathlib import Path

import atelier_contenu as ac


def _lire_parcours(dossier: Path) -> dict:
    return json.loads((dossier / "parcours.json").read_text(encoding="utf-8"))


def _inserer_dans_ordre(dossier_parcours: Path, id_etape: str) -> None:
    donnees = _lire_parcours(dossier_parcours)
    donnees["ordre"].append(id_etape)
    (dossier_parcours / "parcours.json").write_text(
        json.dumps(donnees, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _creer_etape_manuelle(dossier_parcours: Path, id_etape: str, meta: dict,
                          fichiers: dict | None = None, inserer: bool = True) -> None:
    """Construit une étape à la main, sans passer par nouvelle-etape, pour forcer
    des modes ou des contenus que le squelette standard ne produit pas."""
    dossier_etape = dossier_parcours / id_etape
    dossier_etape.mkdir(parents=True)
    (dossier_etape / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
                                             encoding="utf-8")
    for nom_fichier, contenu in (fichiers or {}).items():
        (dossier_etape / nom_fichier).write_text(contenu, encoding="utf-8")
    if inserer:
        _inserer_dans_ordre(dossier_parcours, id_etape)


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


class TestRetirerEtape(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.racine = Path(self._tmp.name)
        ac.commande_nouveau_parcours("be_c", racine=self.racine)
        for id_etape in ("ex01", "ex02"):
            ac.commande_nouvelle_etape("be_c", id_etape, titre=f"Titre {id_etape}",
                                       racine=self.racine)

    def tearDown(self):
        self._tmp.cleanup()

    def test_retire_de_l_ordre(self):
        code = ac.commande_retirer_etape("be_c", "ex01", racine=self.racine)
        self.assertEqual(code, 0)
        donnees = _lire_parcours(self.racine / "be_c")
        self.assertEqual(donnees["ordre"], ["ex02"])

    def test_sans_effacer_le_dossier_reste(self):
        ac.commande_retirer_etape("be_c", "ex01", racine=self.racine)
        self.assertTrue((self.racine / "be_c" / "ex01").exists())

    def test_avec_effacer_le_dossier_disparait(self):
        ac.commande_retirer_etape("be_c", "ex01", effacer=True, racine=self.racine)
        self.assertFalse((self.racine / "be_c" / "ex01").exists())

    def test_refuse_etape_absente(self):
        avant = _lire_parcours(self.racine / "be_c")
        code = ac.commande_retirer_etape("be_c", "ex_fantome", racine=self.racine)
        self.assertNotEqual(code, 0)
        self.assertEqual(_lire_parcours(self.racine / "be_c"), avant)

    def test_refuse_parcours_inexistant(self):
        code = ac.commande_retirer_etape("inconnu", "ex01", racine=self.racine)
        self.assertNotEqual(code, 0)


class TestLister(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.racine = Path(self._tmp.name)
        ac.commande_nouveau_parcours("be_c", racine=self.racine)
        ac.commande_nouvelle_etape("be_c", "ex01", titre="Exercice 1", racine=self.racine)

    def tearDown(self):
        self._tmp.cleanup()

    def test_lister_les_parcours(self):
        parcours = ac.lister_parcours(racine=self.racine)
        self.assertEqual(parcours, [("be_c", 1, "isole")])

    def test_lister_les_etapes_d_un_parcours(self):
        etapes = ac.lister_etapes("be_c", racine=self.racine)
        self.assertEqual(etapes, [("ex01", "programme")])

    def test_lister_etapes_parcours_inexistant(self):
        with self.assertRaises(FileNotFoundError):
            ac.lister_etapes("inconnu", racine=self.racine)


class TestVerifierStructurel(unittest.TestCase):
    """Vérifications sans compilation : meta.json, cohérence des ids, modes non
    automatisables. Rapide, aucune de ces étapes n'appelle gcc."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.racine = Path(self._tmp.name)
        ac.commande_nouveau_parcours("be_c", racine=self.racine)

    def tearDown(self):
        self._tmp.cleanup()

    def test_meta_json_invalide(self):
        dossier = self.racine / "be_c" / "cassee"
        dossier.mkdir(parents=True)
        (dossier / "meta.json").write_text("{ceci n'est pas du json", encoding="utf-8")
        _inserer_dans_ordre(self.racine / "be_c", "cassee")
        code = ac.commande_verifier("be_c", racine=self.racine)
        self.assertNotEqual(code, 0)

    def test_cle_obligatoire_manquante(self):
        _creer_etape_manuelle(self.racine / "be_c", "incomplete",
                              {"id": "incomplete", "titre": "Incomplète"})
        code = ac.commande_verifier("be_c", racine=self.racine)
        self.assertNotEqual(code, 0)

    def test_id_du_meta_different_du_dossier(self):
        _creer_etape_manuelle(self.racine / "be_c", "dossier_x",
                              {"id": "autre_id", "titre": "T", "type": "programme",
                               "fichier_edite": "programme.c", "mode": "test_a_ecrire"})
        code = ac.commande_verifier("be_c", racine=self.racine)
        self.assertNotEqual(code, 0)

    def test_id_de_l_ordre_sans_dossier(self):
        _inserer_dans_ordre(self.racine / "be_c", "fantome")
        code = ac.commande_verifier("be_c", racine=self.racine)
        self.assertNotEqual(code, 0)

    def test_mode_test_a_ecrire_non_verifie_ne_fait_pas_echouer(self):
        _creer_etape_manuelle(self.racine / "be_c", "jalon1",
                              {"id": "jalon1", "titre": "Jalon 1", "type": "jalon",
                               "fichier_edite": "x.c", "mode": "test_a_ecrire"})
        code = ac.commande_verifier("be_c", racine=self.racine)
        self.assertEqual(code, 0)

    def test_sans_argument_ignore_les_parcours_non_isoles(self):
        # be_c reste vide et valide ; projet_x est en mode "projet" avec une étape
        # cassée, elle ne doit jamais être visitée par défaut.
        ac.commande_nouveau_parcours("projet_x", racine=self.racine)
        donnees = _lire_parcours(self.racine / "projet_x")
        donnees["mode"] = "projet"
        (self.racine / "projet_x" / "parcours.json").write_text(
            json.dumps(donnees, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        _creer_etape_manuelle(self.racine / "projet_x", "cassee", {"id": "cassee"})
        code = ac.commande_verifier(racine=self.racine)
        self.assertEqual(code, 0)

    def test_parcours_inexistant(self):
        code = ac.commande_verifier("inconnu", racine=self.racine)
        self.assertNotEqual(code, 0)


class TestVerifierPortes(unittest.TestCase):
    """Tests bout en bout : compilent réellement du C via gcc, donc lents.
    Ce sont eux qui prouvent la propriété centrale de l'outil : le squelette
    produit par nouvelle-etape est vert avant toute édition."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.racine = Path(self._tmp.name)
        ac.commande_nouveau_parcours("be_c", racine=self.racine)

    def tearDown(self):
        self._tmp.cleanup()

    def test_squelette_vert_sans_aucune_edition(self):
        ac.commande_nouvelle_etape("be_c", "ex01", titre="Exercice 1", racine=self.racine)
        code = ac.commande_verifier("be_c", racine=self.racine)
        self.assertEqual(code, 0)

    def test_detecte_un_corrige_casse(self):
        ac.commande_nouvelle_etape("be_c", "ex01", titre="Exercice 1", racine=self.racine)
        corrige = self.racine / "be_c" / "ex01" / "corrige.c"
        corrige.write_text("#include <stdio.h>\nint main(void){ return 1; }\n", encoding="utf-8")
        code = ac.commande_verifier("be_c", racine=self.racine)
        self.assertNotEqual(code, 0)

    def test_detecte_un_starter_qui_passe_a_tort(self):
        ac.commande_nouvelle_etape("be_c", "ex01", titre="Exercice 1", racine=self.racine)
        starter = self.racine / "be_c" / "ex01" / "starter.c"
        starter.write_text('#include <stdio.h>\nint main(void){ printf("etape ok\\n"); return 0; }\n',
                           encoding="utf-8")
        code = ac.commande_verifier("be_c", racine=self.racine)
        self.assertNotEqual(code, 0)

    def test_mode_test_fourni(self):
        meta = {"id": "s1", "titre": "S1", "type": "perso", "mode": "test_fourni",
                "fichier_edite": "soumission.c"}
        fichiers = {
            "corrige.c": '#include "s1.h"\nint f(void){ return 1; }\n',
            "starter.c": '#include "s1.h"\nint f(void){ return 0; }\n',
            "tests.c": '#include "s1.h"\n#include <stdio.h>\n'
                      'int main(void){ if (f() != 1) { printf("FAIL\\n"); return 1; } '
                      'printf("ok\\n"); return 0; }\n',
            "s1.h": "int f(void);\n",
        }
        _creer_etape_manuelle(self.racine / "be_c", "s1", meta, fichiers)
        code = ac.commande_verifier("be_c", racine=self.racine)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
