"""Chemins et drapeaux de compilation. Aucune logique métier ici."""
from pathlib import Path
import os
import subprocess

RACINE = Path(__file__).resolve().parent
# CONTENU pointe sur le parcours hybride ; tout le code existant continue de fonctionner.
CONTENU = RACINE / "contenu" / "hybride"
PROGRESSION_FICHIER = RACINE / "progression.json"
# appairage et file d'attente Moodle, à côté de la progression, spec compagnon LTI
MOODLE_SYNC_FICHIER = RACINE / "moodle_sync.json"
COMPAGNON_URL = os.environ.get("ATELIER_COMPAGNON_URL",
                               "https://compagnon-tp-c.onrender.com")

PROJET_CORRIGE = RACINE / "projet-corrige"
PROJET_SNAKE = RACINE / "projet-corrige" / "SNAKE"
# squelette à trous, point de départ de l'étudiant en parcours projet
PROJET_SQUELETTE = RACINE / "projet-squelette"
PROJET_SQUELETTE_SNAKE = RACINE / "projet-squelette" / "SNAKE"
# copie de travail vivante du parcours projet : l'étudiant la remplit étape par étape
ESPACE_SESSION = RACINE / "espace_session"


def contenu_racine(nom: str) -> Path:
    """Renvoie le chemin d'un sous-dossier de contenu/, par exemple contenu_racine('hybride')."""
    return RACINE / "contenu" / nom

SNAKE_ROOT = Path.home() / "scratch-stage1a" / "snake-sdl" / "extracted" / "SNAKE_STAGE"
ARCH = SNAKE_ROOT / "SNAKE_ARCHIVE_SDL_DEPART"
BUILD_COPY = Path.home() / "scratch-stage1a" / "snake-sdl" / "linux-build" / "SNAKE"

SDL_INCLUDES = [
    SNAKE_ROOT / "SDL3" / "include",
    SNAKE_ROOT / "SDL3_ttf" / "include",
    SNAKE_ROOT / "SDL3_image" / "include",
]


def _module_existe(nom: str) -> bool:
    return subprocess.run(["pkg-config", "--exists", nom],
                          stderr=subprocess.DEVNULL).returncode == 0


def modules_sdl(avec_ttf_image: bool = True) -> list[str]:
    mods = ["sdl3"]
    if avec_ttf_image:
        for c in ("sdl3-ttf", "SDL3_ttf"):
            if _module_existe(c):
                mods.append(c)
                break
        for c in ("sdl3-image", "SDL3_image"):
            if _module_existe(c):
                mods.append(c)
                break
    return mods


def _pkg(champ: str, mods: list[str]) -> list[str]:
    r = subprocess.run(["pkg-config", champ, *mods], capture_output=True, text=True)
    return r.stdout.split()


def cflags_sdl(avec_ttf_image: bool = True) -> list[str]:
    return _pkg("--cflags", modules_sdl(avec_ttf_image))


def libs_sdl(avec_ttf_image: bool = True) -> list[str]:
    return _pkg("--libs", modules_sdl(avec_ttf_image))
