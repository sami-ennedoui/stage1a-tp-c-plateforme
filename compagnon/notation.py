"""Les étapes notées : le dénominateur du score, et le filtre des événements reçus.

L'image Docker du compagnon ne copie que `compagnon/`, jamais `contenu/`. Le compagnon
ne voit donc pas le parcours qu'il note, et ce fichier est tout ce qu'il en sait.

Deux choses en découlent, et ce sont les deux raisons d'être de ce module.

D'abord le compagnon ne peut pas deviner le parcours d'où vient un événement :
`moodle_sync.signaler_porte` n'envoie que l'id de l'étape, et les ids sont uniques d'un
parcours à l'autre. Sans filtre, les étapes d'un parcours d'entraînement s'ajoutaient à
celles du parcours noté et poussaient la note à 100.

Ensuite le dénominateur se déduit de la liste. Il ne peut plus être tapé à la main ni
prendre du retard, ce que l'ancienne variable d'environnement TOTAL_ETAPES ne garantissait
d'aucune façon.

Le fichier peut toujours retarder sur `contenu/`, mais plus en silence :
`tests/test_etapes_notees.py` est le seul endroit du dépôt d'où l'on voit les deux à la
fois, et il refuse qu'ils divergent. `atelier_contenu.py` le tient à jour tout seul.
"""
import json
from pathlib import Path

FICHIER = Path(__file__).resolve().parent / "etapes_notees.json"


def _lire(fichier: Path) -> dict:
    return json.loads(fichier.read_text(encoding="utf-8"))


def charger(fichier: Path = FICHIER) -> list[str]:
    """Les ids des étapes notées, dans l'ordre du parcours."""
    etapes = _lire(fichier)["etapes"]
    if not etapes:
        raise ValueError(f"{fichier} ne liste aucune étape notée : le score serait "
                         "une division par zéro")
    if len(set(etapes)) != len(etapes):
        raise ValueError(f"{fichier} liste deux fois la même étape : le dénominateur "
                         "serait faux")
    return etapes


def parcours_note(fichier: Path = FICHIER) -> str:
    """Le nom du parcours que ce compagnon note, tel que le connaît contenu/."""
    return _lire(fichier)["parcours"]


def ecrire(parcours: str, etapes: list[str], fichier: Path = FICHIER) -> None:
    """Réécrit la liste. Appelé par atelier_contenu.py quand le parcours noté change."""
    fichier.write_text(
        json.dumps({"parcours": parcours, "etapes": list(etapes)},
                   indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
