"""Tests du relevé de progression hors ligne : pourcentage, contenu, empreinte."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import chemins
import progression
import releve
from compagnon.base import score as score_compagnon


def _empreinte(texte: str) -> str:
    m = re.search(r"Empreinte : (\w+)", texte)
    return m.group(1)


class TestReleve(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.fichier_prog = Path(self.d.name) / "progression.json"

    def tearDown(self):
        self.d.cleanup()

    def test_pourcentage_meme_formule_que_le_compagnon(self):
        for validees, total in [(3, 14), (0, 14), (14, 14), (1, 3), (2, 7)]:
            self.assertEqual(releve.pourcentage(validees, total),
                             score_compagnon(validees, total))

    def test_texte_compte_juste_et_liste_dans_l_ordre_du_parcours(self):
        progression.sauver(progression.Progression(
            ["ex01_types", "ex02_operateurs", "ex03_menu"], 1), self.fichier_prog)
        contenu = releve.texte("be_c", fichier_progression=self.fichier_prog)
        self.assertIn("Étapes validées : 3 sur 14, soit 21.4 %", contenu)
        ordre = json.loads((chemins.contenu_racine("be_c") / "parcours.json")
                           .read_text(encoding="utf-8"))["ordre"]
        lignes_etapes = [l for l in contenu.splitlines() if l.startswith("  [")]
        self.assertEqual(len(lignes_etapes), len(ordre))
        for ligne, id_etape in zip(lignes_etapes, ordre):
            self.assertIn(id_etape, ligne)
        self.assertTrue(lignes_etapes[0].startswith("  [x]"))
        self.assertTrue(lignes_etapes[3].startswith("  [ ]"))   # ex04_devine, pas fait

    def test_empreinte_change_si_le_contenu_change(self):
        progression.sauver(progression.Progression(["ex01_types"], 1), self.fichier_prog)
        c1 = releve.texte("be_c", fichier_progression=self.fichier_prog)
        progression.sauver(progression.Progression(
            ["ex01_types", "ex02_operateurs"], 1), self.fichier_prog)
        c2 = releve.texte("be_c", fichier_progression=self.fichier_prog)
        self.assertNotEqual(_empreinte(c1), _empreinte(c2))

    def test_ecrire_ecrit_releve_txt_dans_le_dossier_donne(self):
        contenu = releve.texte("be_c", fichier_progression=self.fichier_prog)
        chemin = releve.ecrire(contenu, dossier=Path(self.d.name))
        self.assertEqual(chemin, Path(self.d.name) / "releve.txt")
        self.assertEqual(chemin.read_text(encoding="utf-8"), contenu)

    def test_cli_releve_ecrit_et_affiche_sans_qt(self):
        # --releve doit fonctionner sans écran, comme --selftest : on l'exécute
        # dans un sous-processus dont le dossier courant est jetable, la vraie
        # progression du dépôt n'est lue qu'en lecture seule.
        racine = chemins.RACINE
        r = subprocess.run(
            [sys.executable, str(racine / "atelier_snake.py"), "--releve", "--parcours", "be_c"],
            cwd=self.d.name, capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Relevé de progression", r.stdout)
        self.assertTrue((Path(self.d.name) / "releve.txt").exists())


if __name__ == "__main__":
    unittest.main()
