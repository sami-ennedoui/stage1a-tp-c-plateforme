"""Réglages locaux de l'appli, mémorisés d'un lancement à l'autre.

Pour l'instant, un seul réglage : le dernier parcours choisi, pour qu'au prochain
lancement l'appli s'ouvre dessus sans qu'on ait à taper --parcours. Stocké dans
`reglages.json` à la racine, git-ignoré (local à chaque poste). Aucune dépendance PyQt.
"""
import json

import chemins

# parcours d'ouverture tant qu'aucun choix n'a été mémorisé : le vrai parcours du BE
PARCOURS_DEFAUT = "be_c"


def charger() -> dict:
    if chemins.REGLAGES_FICHIER.exists():
        try:
            return json.loads(chemins.REGLAGES_FICHIER.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _sauver(donnees: dict) -> None:
    chemins.REGLAGES_FICHIER.write_text(
        json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dernier_parcours(defaut: str = PARCOURS_DEFAUT) -> str:
    """Renvoie le dernier parcours retenu, ou `defaut` si rien n'a été mémorisé."""
    return charger().get("parcours", defaut)


def definir_parcours(nom: str) -> None:
    """Mémorise le parcours choisi pour les prochains lancements."""
    donnees = charger()
    donnees["parcours"] = nom
    _sauver(donnees)
