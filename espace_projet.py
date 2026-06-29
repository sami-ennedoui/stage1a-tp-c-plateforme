"""Gestion de la copie de travail projet de l'étudiant. Aucune compilation ici."""
from pathlib import Path
import shutil


class EspaceProjet:
    """Représente une copie de travail d'un projet source, persistante entre les séances.

    Paramètres
    ----------
    source : Path
        Le dossier projet de référence, par exemple chemins.PROJET_CORRIGE.
    dossier_session : Path
        Le dossier où vivra la copie de l'étudiant. Il peut ne pas encore exister.
    """

    def __init__(self, source: Path, dossier_session: Path) -> None:
        self._source = Path(source)
        self._racine = Path(dossier_session)

    # ------------------------------------------------------------------
    # Propriétés publiques
    # ------------------------------------------------------------------

    @property
    def chemin_racine(self) -> Path:
        """Chemin racine de la copie de travail."""
        return self._racine

    @property
    def build_sh(self) -> Path:
        """Chemin du script build.sh dans la copie de travail."""
        return self._racine / "build.sh"

    @property
    def dossier_snake(self) -> Path:
        """Chemin du dossier SNAKE dans la copie de travail."""
        return self._racine / "SNAKE"

    # ------------------------------------------------------------------
    # Opérations sur la copie
    # ------------------------------------------------------------------

    def initialiser(self) -> None:
        """Copie source vers dossier_session si le dossier n'existe pas encore.
        Si la copie est déjà présente, ne fait rien."""
        if not self._racine.exists():
            shutil.copytree(self._source, self._racine)

    def reinitialiser(self) -> None:
        """Efface la copie existante et recopie depuis la source."""
        if self._racine.exists():
            shutil.rmtree(self._racine)
        shutil.copytree(self._source, self._racine)

    def lire_fichier(self, chemin_relatif: str) -> str:
        """Lit un fichier de la copie de travail. Le chemin est relatif à la racine du projet,
        par exemple 'SNAKE/GestionJeu.c'."""
        return (self._racine / chemin_relatif).read_text(encoding="utf-8")

    def ecrire_fichier(self, chemin_relatif: str, contenu: str) -> None:
        """Écrit un fichier dans la copie de travail. Le chemin est relatif à la racine du projet,
        par exemple 'SNAKE/GestionJeu.c'."""
        (self._racine / chemin_relatif).write_text(contenu, encoding="utf-8")
