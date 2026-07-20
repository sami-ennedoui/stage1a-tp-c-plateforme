"""Chemins et drapeaux de compilation. Aucune logique métier ici."""
from functools import lru_cache
from pathlib import Path
import os
import subprocess

# Sous Windows, un sous-processus console lancé depuis une application graphique ouvre
# une fenêtre cmd le temps de son exécution. L'atelier en lance un à chaque compilation,
# à chaque test et au démarrage : sans ce drapeau, la fenêtre clignote sans arrêt.
# Vaut 0 hors Windows, où l'attribut n'existe pas : le passer est alors sans effet.
# Défini ici parce que chemins.py est importé par tous les modules qui lancent un
# processus, et qu'un seul endroit vaut mieux que la même ligne répétée cinq fois.
SANS_FENETRE = getattr(subprocess, "CREATE_NO_WINDOW", 0)

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

# hache du mot de passe du mode auteur, local et git-ignore, voir auteur.py
AUTEUR_FICHIER = RACINE / "auteur.json"
# reglages locaux memorises d'un lancement a l'autre (dernier parcours), git-ignore
REGLAGES_FICHIER = RACINE / "reglages.json"

# "local" (défaut) : aucun réseau, jamais ; la progression ne vit que sur ce poste.
# "moodle" : la progression remonte au compagnon LTI, qui n'est plus qu'une démo.
# Le défaut est local depuis le 2026-07-16 : le compagnon tourne sur un compte
# Render personnel, l'école ne peut pas en dépendre, donc un bundle distribué ne
# doit parler à aucun serveur tant que personne ne l'a demandé.
ATELIER_SUIVI = os.environ.get("ATELIER_SUIVI", "local")
if ATELIER_SUIVI not in ("moodle", "local"):
    raise SystemExit(
        f"ATELIER_SUIVI={ATELIER_SUIVI!r} invalide, valeurs acceptées : moodle, local.")


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


@lru_cache(maxsize=1)
def flags_toolchain_clangd() -> tuple[str, ...]:
    """Drapeaux à donner à clangd pour qu'il voie la même toolchain que gcc.

    Sous Windows, clangd vise x86_64-pc-windows-msvc par défaut et cherche les en-têtes de
    Visual Studio, absent d'une machine étudiante : tout fichier qui inclut <stdio.h> se
    couvrirait de fausses erreurs. On aligne donc clangd sur le gcc embarqué (MinGW, fourni
    par w64devkit) en lui donnant son triplet et ses chemins d'en-têtes système.

    Les chemins sont demandés à gcc, jamais écrits en dur : ils contiennent son numéro de
    version, qui changera à la prochaine mise à jour de w64devkit.

    Sous Linux, clangd trouve seul les en-têtes système : on ne renvoie rien.
    """
    if os.name != "nt":
        return ()
    try:
        triplet = subprocess.run(["gcc", "-dumpmachine"], capture_output=True, text=True,
                                 encoding="utf-8", errors="replace",
                                 creationflags=SANS_FENETRE).stdout.strip()
        sonde = subprocess.run(["gcc", "-E", "-v", "-x", "c", os.devnull],
                               capture_output=True, text=True,
                               encoding="utf-8", errors="replace",
                               creationflags=SANS_FENETRE)
    except OSError:
        return ()          # gcc introuvable : clangd se taira, l'atelier marche quand même
    if not triplet:
        return ()

    flags = [f"--target={triplet}"]
    dedans = False
    for ligne in sonde.stderr.splitlines():
        if "#include <...> search starts here" in ligne:
            dedans = True
            continue
        if "End of search list" in ligne:
            break
        if dedans:
            chemin = Path(ligne.strip())
            if chemin.is_dir():
                flags.append(f"-isystem{chemin.resolve()}")
    return tuple(flags)


def _module_existe(nom: str) -> bool:
    return subprocess.run(["pkg-config", "--exists", nom],
                          stderr=subprocess.DEVNULL,
                          creationflags=SANS_FENETRE).returncode == 0


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
    r = subprocess.run(["pkg-config", champ, *mods], capture_output=True, text=True,
                       creationflags=SANS_FENETRE)
    return r.stdout.split()


def cflags_sdl(avec_ttf_image: bool = True) -> list[str]:
    return _pkg("--cflags", modules_sdl(avec_ttf_image))


def libs_sdl(avec_ttf_image: bool = True) -> list[str]:
    return _pkg("--libs", modules_sdl(avec_ttf_image))
