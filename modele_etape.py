"""Lecture des étapes du TP depuis les dossiers de données. Aucune compilation ici."""
from dataclasses import dataclass
from pathlib import Path
import json

import chemins


@dataclass
class Etape:
    id: str
    titre: str
    type: str            # "perso" | "jalon"
    mode: str            # "test_fourni" | "test_a_ecrire"
    recette: str         # "perso" | "jalon_test"
    cran_debloque: int
    noeud_cours: str
    fichier_edite: str
    dossier: Path


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
        mode=meta["mode"],
        recette=meta["recette"],
        cran_debloque=meta["cran_debloque"],
        noeud_cours=meta["noeud_cours"],
        fichier_edite=meta["fichier_edite"],
        dossier=dossier,
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
