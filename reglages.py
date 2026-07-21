"""Réglages locaux de l'appli, mémorisés d'un lancement à l'autre.

Trois réglages : le dernier parcours choisi, pour qu'au prochain lancement l'appli
s'ouvre dessus sans qu'on ait à taper --parcours ; l'activation du tuteur IA ; et la
commande qui l'invoque. Stocké dans `reglages.json` à la racine, git-ignoré (local à
chaque poste). Aucune dépendance PyQt.
"""
import json

import chemins

# parcours d'ouverture tant qu'aucun choix n'a été mémorisé : le vrai parcours du BE
PARCOURS_DEFAUT = "be_c"

# Le tuteur est actif par défaut : c'est le comportement historique, et le désactiver
# doit rester un geste délibéré de l'enseignant (séance notée, poste sans réseau).
TUTEUR_ACTIF_DEFAUT = True


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


def tuteur_actif(defaut: bool = TUTEUR_ACTIF_DEFAUT) -> bool:
    """Vrai si le tuteur IA doit être proposé à l'étudiant.

    Désactivé, l'atelier fonctionne entièrement : seules l'aide et la génération de
    code disparaissent. Sert aux séances notées et aux salles sans accès réseau, où
    laisser des boutons qui répondent « moteur indisponible » n'apprend rien."""
    return bool(charger().get("tuteur_actif", defaut))


def definir_tuteur_actif(actif: bool) -> None:
    donnees = charger()
    donnees["tuteur_actif"] = bool(actif)
    _sauver(donnees)


def commande_ia(defaut: str = "") -> str:
    """Ligne de commande qui invoque le moteur IA, vide si on laisse l'auto-détection.

    Permet de brancher un moteur que l'atelier ne connaît pas, ou un binaire installé
    hors du PATH, sans toucher au code. Le prompt est passé à la place de {prompt}
    s'il figure dans la commande, sinon ajouté en dernier argument."""
    return str(charger().get("commande_ia", defaut))


def definir_commande_ia(commande: str) -> None:
    """Mémorise la commande du tuteur. Une chaîne vide rend l'auto-détection."""
    donnees = charger()
    donnees["commande_ia"] = str(commande or "")
    _sauver(donnees)


# Mode « tout débloqué » (enseignant/démo) : quand vrai, toutes les étapes sont ouvertes
# et les quatre crans du tuteur disponibles, sans qu'il faille les gagner. L'activation
# est protégée par le mot de passe auteur (voir fenetre). Faux = parcours progressif.
TOUT_DEBLOQUE_DEFAUT = False


def tout_debloque(defaut: bool = TOUT_DEBLOQUE_DEFAUT) -> bool:
    """Vrai si l'atelier doit tout ouvrir d'emblée, comme en mode démo.

    Réglé par l'enseignant depuis le menu Paramètres (activation protégée par le mot de
    passe auteur). N'efface pas la progression réelle de l'étudiant : il ne fait que lever
    le verrouillage à l'affichage et ouvrir les crans du tuteur. Le décocher rend le
    parcours progressif exactement tel qu'il était."""
    return bool(charger().get("tout_debloque", defaut))


def definir_tout_debloque(actif: bool) -> None:
    donnees = charger()
    donnees["tout_debloque"] = bool(actif)
    _sauver(donnees)
