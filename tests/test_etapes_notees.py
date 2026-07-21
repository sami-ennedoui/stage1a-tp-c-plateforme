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


def _tous_les_parcours(racine: Path) -> dict[str, list[str]]:
    """Chaque parcours de contenu/ et l'ordre de ses étapes."""
    return {d.name: json.loads((d / "parcours.json").read_text(encoding="utf-8"))["ordre"]
            for d in sorted(racine.iterdir())
            if d.is_dir() and (d / "parcours.json").exists()}


def _homonymes(parcours: dict[str, list[str]]) -> list[str]:
    """Les ids qui servent dans plus d'un parcours, décrits pour un humain."""
    proprietaire, doublons = {}, []
    for nom, ordre in parcours.items():
        for id_etape in ordre:
            if id_etape in proprietaire:
                doublons.append(f"{id_etape} sert dans {proprietaire[id_etape]} et {nom}")
            else:
                proprietaire[id_etape] = nom
    return doublons


class TestIdsUniquesEntreParcours(unittest.TestCase):
    """L'invariant dont dépend la justesse des notes, et que rien ne disait tout haut."""

    def test_aucun_id_ne_sert_dans_deux_parcours(self):
        """Le filtre `etapes_notees` trie des ids, pas des parcours : il ne protège la
        note que tant qu'aucun id ne se répète. `signaler_porte` n'envoie que l'id, donc
        deux homonymes sont le même exercice pour le compagnon. Une étape d'entraînement
        noterait à la place de sa jumelle de be_c, et `progression.fusionner` débloquerait
        son cran à l'appairage. C'est le bug du 16 juillet par une autre porte.

        S'il casse : renommer l'étape fautive. `atelier_contenu.py` refuse d'en créer,
        donc l'homonyme est entré à la main ou par une GUI qui ne vérifie pas.
        """
        doublons = _homonymes(_tous_les_parcours(RACINE / "contenu"))
        self.assertEqual(doublons, [], "des étapes homonymes rendent les notes fausses : "
                                       + " ; ".join(doublons))

    def test_l_invariant_ci_dessus_attrape_vraiment_un_homonyme(self):
        """Le test du dessus passe aujourd'hui, et passerait tout autant s'il ne
        regardait rien. Celui-ci est la seule preuve que le filet attrape."""
        doublons = _homonymes({"be_c": ["ex05_rectangle", "ex06_rectangle_sp"],
                               "perso": ["ex05_rectangle"]})
        self.assertEqual(len(doublons), 1)
        self.assertIn("ex05_rectangle", doublons[0])
        self.assertNotIn("ex06_rectangle_sp", doublons[0])


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
