"""Lecture des étapes du TP depuis les dossiers de données. Aucune compilation ici."""
from dataclasses import dataclass
from pathlib import Path
import json

import chemins


@dataclass
class Etape:
    id: str
    titre: str
    type: str                    # "perso" | "jalon" | "projet"
    fichier_edite: str
    dossier: Path
    # champs des parcours isolés, optionnels pour les étapes projet
    mode: str = ""               # "test_fourni" | "test_a_ecrire" | "programme"
    recette: str = ""            # "perso" | "jalon_test"
    cran_debloque: int = 0
    noeud_cours: str = ""
    # champs du mode "programme" : l'étudiant écrit un programme complet
    entree: str = ""             # entrée standard envoyée au programme
    sortie_attendue: list | None = None  # fragments littéraux qui doivent figurer dans la sortie
    # motifs tolérants (valeurs libres) : liste de {"motif": <regex>, "attendu": <texte lisible>}
    # chaque regex doit se retrouver dans la sortie (re.search). Sert quand l'énoncé
    # n'impose pas de valeur précise, seulement un libellé et un format (ex. ex01).
    sortie_motifs: list | None = None
    # Porte étanche : plusieurs jeux d'entrées au lieu d'un seul. Chaque cas est un
    # {"entree": str, "sortie_attendue": list, "sortie_motifs": list} et TOUS doivent
    # passer. Une seule exécution laisse la porte ouverte à un programme qui se contente
    # de réimprimer la sortie attendue en dur, sans rien calculer ; plusieurs entrées
    # obligent à produire la réponse, pas à la réciter. Absent, on retombe sur le cas
    # unique décrit par entree/sortie_attendue/sortie_motifs ci-dessus.
    cas: list | None = None
    # champs des étapes projet, optionnels pour les parcours isolés
    harnais: list | None = None  # harnais logiques, chemins relatifs au dépôt
    sources: list | None = None  # sources .c à compiler avec le harnais, relatives à l'espace
    porte: str = ""              # "logique" pour un harnais, "build" pour le capstone


@dataclass
class Parcours:
    """Représente un parcours complet avec sa liste d'étapes et son mode d'exécution."""
    etapes: list[Etape]
    mode: str            # "isole" | "projet"
    # Parcours libre : toutes les étapes sont accessibles d'emblée, sans passer les
    # portes précédentes. C'est un champ du parcours, pas un test sur son nom : deux
    # parcours peuvent coexister sur le même contenu, l'un étanche pour l'évaluation,
    # l'autre libre pour réviser un point précis.
    libre: bool = False


def charger_etape(dossier: Path) -> Etape:
    meta = json.loads((dossier / "meta.json").read_text(encoding="utf-8"))
    return Etape(
        id=meta["id"],
        titre=meta["titre"],
        type=meta["type"],
        fichier_edite=meta["fichier_edite"],
        dossier=dossier,
        mode=meta.get("mode", ""),
        recette=meta.get("recette", ""),
        cran_debloque=meta.get("cran_debloque", 0),
        noeud_cours=meta.get("noeud_cours", ""),
        harnais=meta.get("harnais"),
        sources=meta.get("sources"),
        porte=meta.get("porte", ""),
        entree=meta.get("entree", ""),
        sortie_attendue=meta.get("sortie_attendue"),
        sortie_motifs=meta.get("sortie_motifs"),
        cas=meta.get("cas"),
    )


class ParcoursIntrouvable(Exception):
    """Le dossier de contenu demandé n'existe pas, ou ne contient pas de parcours.json."""


def _lire_parcours_json(dossier_contenu: Path) -> dict:
    """Lit parcours.json en disant clairement ce qui manque et ce qui est disponible.

    Le paquet portable ne livre pas forcément tous les parcours du dépôt. Sans ce contrôle,
    un parcours absent remonte un FileNotFoundError sur un chemin interne, que personne ne
    peut interpréter."""
    fichier = dossier_contenu / "parcours.json"
    if fichier.exists():
        return json.loads(fichier.read_text(encoding="utf-8"))

    racine = dossier_contenu.parent
    dispos = sorted(d.name for d in racine.iterdir()
                    if (d / "parcours.json").exists()) if racine.is_dir() else []
    message = f"Parcours « {dossier_contenu.name} » introuvable dans {racine}."
    if dispos:
        message += ("\nParcours disponibles ici : " + ", ".join(dispos) +
                    f"\nRelance avec :  --parcours {dispos[0]}   (ou double-clique lancer.bat)")
    else:
        message += "\nAucun parcours n'est installé à côté de la plateforme."
    raise ParcoursIntrouvable(message)


def charger_parcours(dossier_contenu: Path = chemins.CONTENU) -> list[Etape]:
    """Renvoie la liste des étapes dans l'ordre du parcours. Rétrocompatible."""
    donnees = _lire_parcours_json(dossier_contenu)
    return [charger_etape(dossier_contenu / i) for i in donnees["ordre"]]


def charger_parcours_complet(dossier_contenu: Path = chemins.CONTENU) -> Parcours:
    """Renvoie un objet Parcours avec les étapes et le mode ('isole' par défaut si absent)."""
    donnees = _lire_parcours_json(dossier_contenu)
    mode = donnees.get("mode", "isole")
    etapes = [charger_etape(dossier_contenu / i) for i in donnees["ordre"]]
    return Parcours(etapes=etapes, mode=mode, libre=bool(donnees.get("libre", False)))
