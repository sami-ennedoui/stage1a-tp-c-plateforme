"""Tuteur IA bridé. Prompt selon le cran, filtre déterministe qui masque la solution,
appel du moteur en sous-processus. Aucune UI."""
import os
import re
import shutil
import subprocess
from pathlib import Path

import chemins
from modele_etape import Etape

# Supprime la fenêtre cmd qui clignoterait au lancement du moteur (appli packagée
# sans console sous Windows). Vaut 0 hors Windows, sans objet.
_SANS_FENETRE = getattr(subprocess, "CREATE_NO_WINDOW", 0)

_CONSIGNE_CRAN = {
    0: "Cran N0. Explique seulement le concept en jeu, avec tes mots, sans donner ni "
       "écrire la moindre ligne de la solution. Pose une question qui fait réfléchir.",
    1: "Cran N1. Tu peux donner un squelette vide ou une analogie, mais pas la solution "
       "écrite. Montre la forme, pas le contenu.",
    2: "Cran N2. Tu peux proposer une piste candidate, mais demande à l'étudiant de la "
       "justifier et de la vérifier lui-même, sans affirmer qu'elle est correcte.",
    3: "Cran N3. Tu es libre d'aider comme tu veux.",
}


def construire_prompt(etape: Etape, code_eleve: str, question: str, niveau: int) -> str:
    enonce = (etape.dossier / "enonce.md").read_text(encoding="utf-8")
    return (
        "Tu es un tuteur de programmation C pour un étudiant débutant. Tu n'es jamais "
        "celui qui résout à sa place.\n\n"
        f"{_CONSIGNE_CRAN.get(niveau, _CONSIGNE_CRAN[0])}\n\n"
        f"Énoncé de l'étape :\n{enonce}\n\n"
        f"Code actuel de l'étudiant :\n{code_eleve}\n\n"
        f"Question de l'étudiant :\n{question}\n"
    )


def _cle(ligne: str) -> str | None:
    """Clé de comparaison d'une ligne : le code seul, sans le commentaire de fin de
    ligne et sans aucune espace. Renvoie None si la ligne n'est pas une ligne de
    solution à masquer (trop courte, #include, accolade seule, commentaire seul).
    On compare sur cette clé pour qu'un corrigé commenté masque quand même une
    solution propre, et pour ignorer les différences d'espacement."""
    code = ligne.split("//", 1)[0].split("/*", 1)[0].strip()
    if len(code) < 6:              # ignore {, }, lignes trop courtes
        return None
    if code.startswith("#include"):
        return None
    # continuations de commentaire bloc (« * texte » ou « */ ») mais pas les déréférencements
    if code == "*" or code.startswith("* ") or code.startswith("*/"):
        return None
    return re.sub(r"\s+", "", code)


def _cles_significatives(code: str) -> set[str]:
    return {c for c in (_cle(l) for l in code.splitlines()) if c is not None}


def _chemin_corrige(etape: Etape) -> Path:
    """Le corrigé d'une étape isolée vit dans son dossier sous corrige.c. Celui d'une
    étape projet vit dans projet-corrige, au même chemin relatif que le fichier édité."""
    if etape.type == "projet":
        return chemins.PROJET_CORRIGE / etape.fichier_edite
    return etape.dossier / "corrige.c"


def filtre_solution(reponse: str, corrige: str) -> str:
    """Masque dans la réponse les lignes qui reproduisent une ligne du corrigé,
    laisse passer tout le reste."""
    cibles = _cles_significatives(corrige)
    sortie = []
    for ligne in reponse.splitlines():
        cle = _cle(ligne)
        if cle is not None and cle in cibles:
            sortie.append("    … (ligne masquée par le filtre anti-solution) …")
        else:
            sortie.append(ligne)
    return "\n".join(sortie)


# Moteurs IA supportés, dans l'ordre d'essai de l'auto-détection.
_MOTEURS = ("claude", "codex")


def _binaire(moteur: str) -> str:
    """Nom de l'exécutable d'un moteur ('claude:opus' -> 'claude')."""
    return moteur.split(":", 1)[0]


def _moteur_choisi() -> str | None:
    """Moteur IA à utiliser. La variable ATELIER_AI le force (si l'exécutable est
    présent) ; sinon on prend le premier moteur connu trouvé sur le PATH. Renvoie
    None si aucun moteur n'est disponible : l'atelier marche alors sans tuteur."""
    force = os.environ.get("ATELIER_AI")
    if force:
        return force if shutil.which(_binaire(force)) else None
    for m in _MOTEURS:
        if shutil.which(m):
            return m
    return None


def _commande(moteur: str, prompt: str) -> list[str]:
    """Commande d'un tour non interactif, propre à chaque moteur.
    claude : 'claude -p <prompt>'. codex : 'codex exec <prompt>' avec
    --skip-git-repo-check (l'atelier ne tourne pas dans un dépôt git) ; le bac à
    sable de codex reste en lecture seule, le tuteur ne fait que répondre."""
    binaire = _binaire(moteur)
    if binaire == "codex":
        return ["codex", "exec", "--skip-git-repo-check", prompt]
    return [binaire, "-p", prompt]


def moteur_disponible() -> bool:
    return _moteur_choisi() is not None


def demander_aide(etape: Etape, code_eleve: str, question: str, niveau: int) -> str:
    moteur = _moteur_choisi()
    if moteur is None:
        return "Moteur IA indisponible. Le reste de l'atelier marche, compiler, tester, lancer."
    prompt = construire_prompt(etape, code_eleve, question, niveau)
    try:
        # stdin fermé : sinon 'codex exec' lit stdin et attend son EOF, ce qui bloque
        # quand le tuteur est lancé en sous-processus sans console (fenêtre PyQt).
        # encoding utf-8 : les moteurs répondent en UTF-8 ; sans ça la sortie serait
        # décodée dans l'encodage local (cp1252 sous Windows FR) et « cœur » deviendrait
        # « cÅ“ur ». creationflags : pas de fenêtre cmd qui clignote au clic.
        r = subprocess.run(_commande(moteur, prompt),
                           stdin=subprocess.DEVNULL,
                           capture_output=True, encoding="utf-8", errors="replace",
                           creationflags=_SANS_FENETRE, timeout=120)
    except subprocess.TimeoutExpired:
        return "Le moteur IA n'a pas répondu à temps."
    # moteur trouvé mais en échec au runtime (auth, quota), on ne renvoie pas son
    # erreur brute comme si c'était une aide, et on ne la passe pas au filtre.
    if r.returncode != 0 and not r.stdout.strip():
        return "Le moteur IA a renvoyé une erreur. Réessaie, ou demande à ton tuteur."
    reponse = r.stdout.strip() or r.stderr.strip()
    corrige = _chemin_corrige(etape).read_text(encoding="utf-8")
    return filtre_solution(reponse, corrige)
