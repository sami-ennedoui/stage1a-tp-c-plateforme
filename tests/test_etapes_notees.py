"""Le compagnon note un parcours qu'il ne voit pas.

Son image Docker ne copie que `compagnon/`, jamais `contenu/`. `compagnon/etapes_notees.json`
est donc tout ce qu'il sait du parcours qu'il note, et ce fichier redit ce que
`contenu/be_c/parcours.json` dit déjà. Deux copies d'un même fait finissent toujours par
diverger.

Ce test est le seul endroit du dépôt d'où l'on voit les deux à la fois, donc le seul qui
puisse le leur interdire. S'il casse, ce n'est pas lui qu'il faut réparer : c'est que le
contenu a changé sans que la notation suive, et que les notes de tous les étudiants sont
sur le point de devenir fausses. `python3 atelier_contenu.py notation` le remet d'aplomb.
"""
import json
import unittest
from pathlib import Path

import chemins
from compagnon import notation

RACINE = Path(__file__).resolve().parent.parent


def _ordre_du_contenu(nom_parcours: str) -> list[str]:
    fichier = chemins.contenu_racine(nom_parcours) / "parcours.json"
    return json.loads(fichier.read_text(encoding="utf-8"))["ordre"]


class TestEtapesNotees(unittest.TestCase):

    def test_la_liste_notee_est_exactement_le_parcours_du_contenu(self):
        """Le test qui compte. Mêmes étapes, même ordre, ni oubli ni surplus."""
        notees = notation.charger()
        reel = _ordre_du_contenu(notation.parcours_note())
        self.assertEqual(notees, reel,
                         "compagnon/etapes_notees.json a pris du retard sur contenu/. "
                         "Lance : python3 atelier_contenu.py notation")

    def test_le_parcours_note_existe_vraiment(self):
        nom = notation.parcours_note()
        self.assertTrue((chemins.contenu_racine(nom) / "parcours.json").exists(),
                        f"le compagnon prétend noter {nom}, qui n'est pas dans contenu/")


class TestNotationRefuseLIncoherent(unittest.TestCase):
    """Un fichier abîmé doit se plaindre au démarrage, pas produire une note fausse."""

    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.fichier = Path(self._tmp.name) / "etapes_notees.json"

    def tearDown(self):
        self._tmp.cleanup()

    def test_refuse_une_liste_vide(self):
        notation.ecrire("be_c", [], self.fichier)
        with self.assertRaises(ValueError):
            notation.charger(self.fichier)

    def test_refuse_un_doublon(self):
        # Un doublon gonflerait le dénominateur, donc écraserait la note de chacun.
        notation.ecrire("be_c", ["a", "b", "a"], self.fichier)
        with self.assertRaises(ValueError):
            notation.charger(self.fichier)


if __name__ == "__main__":
    unittest.main()
