"""Tests de la base du compagnon : appairage, événements, score."""
import sqlite3
import time
import unittest

from compagnon import base

AGS = {"lineitem": "https://moodle.example/ligne/42", "scope": []}


def cx_memoire():
    cx = base.ouvrir(":memory:")
    return cx


class TestAppairage(unittest.TestCase):
    def test_lancement_rend_un_code_lisible(self):
        cx = cx_memoire()
        code = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS)
        self.assertEqual(len(code), 6)
        for c in code:
            self.assertIn(c, base.ALPHABET_CODE)

    def test_echange_du_code_rend_un_jeton_une_seule_fois(self):
        cx = cx_memoire()
        code = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS)
        jeton = base.echanger_code(cx, code)
        self.assertIsNotNone(jeton)
        self.assertEqual(base.sub_du_jeton(cx, jeton), "u12")
        self.assertIsNone(base.echanger_code(cx, code))  # usage unique

    def test_echange_tolere_tirets_espaces_et_casse(self):
        cx = cx_memoire()
        code = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS)
        brouillon = f" {code[:3].lower()}-{code[3:]} "
        self.assertIsNotNone(base.echanger_code(cx, brouillon))

    def test_code_expire_refuse(self):
        cx = cx_memoire()
        code = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS,
                                          duree=-1)
        self.assertIsNone(base.echanger_code(cx, code))

    def test_nouveau_lancement_remplace_l_ancien_appairage(self):
        cx = cx_memoire()
        code1 = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS)
        jeton1 = base.echanger_code(cx, code1)
        code2 = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS)
        jeton2 = base.echanger_code(cx, code2)
        self.assertIsNone(base.sub_du_jeton(cx, jeton1))
        self.assertEqual(base.sub_du_jeton(cx, jeton2), "u12")

    def test_jeton_inconnu_rend_none(self):
        cx = cx_memoire()
        self.assertIsNone(base.sub_du_jeton(cx, "n_existe_pas"))


class TestEvenementsEtScore(unittest.TestCase):
    def test_evenements_journalises_et_etapes_distinctes(self):
        cx = cx_memoire()
        n = base.ajouter_evenements(cx, "u12", [
            {"etape": "perso_P1", "reussite": True, "horodatage": "2026-07-07T10:00:00"},
            {"etape": "perso_P1", "reussite": True, "horodatage": "2026-07-07T11:00:00"},
            {"etape": "jalon1_parametrage", "reussite": True, "horodatage": "2026-07-07T12:00:00"},
            {"etape": "jalon2", "reussite": False, "horodatage": "2026-07-07T13:00:00"},
        ])
        self.assertEqual(n, 4)
        self.assertEqual(base.etapes_validees(cx, "u12"),
                         {"perso_P1", "jalon1_parametrage"})

    def test_score_en_pourcentage(self):
        self.assertEqual(base.score(3, 6), 50.0)
        self.assertEqual(base.score(0, 6), 0.0)
        self.assertEqual(base.score(7, 6), 100.0)  # jamais au dessus de 100

    def test_file_des_notes_a_pousser(self):
        cx = cx_memoire()
        code = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS)
        base.echanger_code(cx, code)
        base.marquer_a_pousser(cx, "u12", 50.0)
        base.marquer_a_pousser(cx, "u12", 66.7)  # remplace, ne s'empile pas
        attente = base.notes_en_attente(cx)
        self.assertEqual(len(attente), 1)
        sub, sc, ags = attente[0]
        self.assertEqual((sub, sc), ("u12", 66.7))
        self.assertEqual(ags["lineitem"], AGS["lineitem"])
        base.marquer_poussee(cx, "u12")
        self.assertEqual(base.notes_en_attente(cx), [])


if __name__ == "__main__":
    unittest.main()
