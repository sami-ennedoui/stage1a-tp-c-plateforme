"""Diagnostic système : où sont les choses, quels outils sont présents.

Version en logique pure du vieux diagnostic.bat. La fenêtre (dialogue_diagnostic.py)
n'affiche que ce que ces fonctions renvoient. Aucune dépendance PyQt.
"""
import os
import shutil
from pathlib import Path

import chemins

# outils attendus par l'appli. gcc compile, clangd donne les diagnostics live,
# claude fait tourner le tuteur. Tous sont optionnels sauf gcc pour les portes.
OUTILS = ("gcc", "clangd", "claude")

# emplacement du compilateur portable embarqué à côté de l'appli, voir Atelier.bat
W64DEVKIT_BIN = chemins.RACINE / "w64devkit" / "bin"


def _trouver(nom: str) -> Path | None:
    """Cherche un exécutable dans le PATH, puis dans w64devkit\\bin embarqué."""
    trouve = shutil.which(nom)
    if trouve:
        return Path(trouve)
    local = W64DEVKIT_BIN / (nom + (".exe" if os.name == "nt" else ""))
    return local if local.exists() else None


def outils() -> list[tuple[str, Path | None]]:
    """Pour chaque outil attendu, son chemin s'il est présent, sinon None."""
    return [(nom, _trouver(nom)) for nom in OUTILS]


def parcours_disponibles(dossier_contenu: Path | None = None) -> list[str]:
    """Noms des sous-dossiers de contenu/ qui contiennent un parcours.json."""
    base = dossier_contenu or (chemins.RACINE / "contenu")
    if not base.exists():
        return []
    noms = [e.name for e in base.iterdir() if e.is_dir() and (e / "parcours.json").exists()]
    return sorted(noms)


def chemins_cles(parcours_nom: str) -> list[tuple[str, Path]]:
    """Libellé et chemin des emplacements utiles, dossier du contenu en premier."""
    return [
        ("Dossier de l'appli", chemins.RACINE),
        ("Contenu du parcours", chemins.contenu_racine(parcours_nom)),
        ("Progression", chemins.PROGRESSION_FICHIER),
        ("Compilateur w64devkit", chemins.RACINE / "w64devkit"),
    ]


def ouvrir_dossier(chemin: Path) -> None:
    """Ouvre l'Explorateur sur un dossier, ou sur le dossier parent d'un fichier."""
    cible = chemin if chemin.is_dir() else chemin.parent
    os.startfile(str(cible))  # Windows : ouvre l'Explorateur
