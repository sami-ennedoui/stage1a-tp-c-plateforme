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
    mode: str = ""               # "test_fourni" | "test_a_ecrire"
    recette: str = ""            # "perso" | "jalon_test"
    cran_debloque: int = 0
    noeud_cours: str = ""
    # champs des étapes projet, optionnels pour les parcours isolés
    harnais: list | None = None  # harnais logiques, chemins relatifs au dépôt
    sources: list | None = None  # sources .c à compiler avec le harnais, relatives à l'espace
    porte: str = ""              # "logique" pour un harnais, "build" pour le capstone


@dataclass
class Parcours:
    """Représente un parcours complet avec sa liste d'étapes et son mode d'exécution."""
    etapes: list[Etape]
    mode: str            # "isole" | "projet"


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
    )


def charger_parcours(dossier_contenu: Path = chemins.CONTENU) -> list[Etape]:
    """Renvoie la liste des étapes dans l'ordre du parcours. Rétrocompatible."""
    donnees = json.loads((dossier_contenu / "parcours.json").read_text(encoding="utf-8"))
    return [charger_etape(dossier_contenu / i) for i in donnees["ordre"]]


def charger_parcours_complet(dossier_contenu: Path = chemins.CONTENU) -> Parcours:
    """Renvoie un objet Parcours avec les étapes et le mode ('isole' par défaut si absent)."""
    donnees = json.loads((dossier_contenu / "parcours.json").read_text(encoding="utf-8"))
    mode = donnees.get("mode", "isole")
    etapes = [charger_etape(dossier_contenu / i) for i in donnees["ordre"]]
    return Parcours(etapes=etapes, mode=mode)
