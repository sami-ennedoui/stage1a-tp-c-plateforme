"""Tuteur IA bridé. Prompt selon le cran, filtre déterministe qui masque la solution,
appel du moteur en sous-processus. Aucune UI."""
import os
import shutil
import subprocess
from pathlib import Path

import chemins
from modele_etape import Etape

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


def _lignes_significatives(code: str) -> list[str]:
    lignes = []
    for ligne in code.splitlines():
        nu = ligne.strip()
        if len(nu) < 6:            # ignore {, }, lignes trop courtes
            continue
        if nu.startswith("//") or nu.startswith("/*"):
            continue
        # continuations de commentaires bloc (« * texte » ou « */ ») mais pas les déréférencements
        if nu == "*" or nu.startswith("* ") or nu.startswith("*/"):
            continue
        if nu.startswith("#include"):
            continue
        lignes.append(nu)
    return lignes


def _chemin_corrige(etape: Etape) -> Path:
    """Le corrigé d'une étape isolée vit dans son dossier sous corrige.c. Celui d'une
    étape projet vit dans projet-corrige, au même chemin relatif que le fichier édité."""
    if etape.type == "projet":
        return chemins.PROJET_CORRIGE / etape.fichier_edite
    return etape.dossier / "corrige.c"


def filtre_solution(reponse: str, corrige: str) -> str:
    """Masque dans la réponse les lignes qui reproduisent une ligne du corrigé,
    laisse passer tout le reste."""
    cibles = set(_lignes_significatives(corrige))
    sortie = []
    for ligne in reponse.splitlines():
        if ligne.strip() in cibles:
            sortie.append("    … (ligne masquée par le filtre anti-solution) …")
        else:
            sortie.append(ligne)
    return "\n".join(sortie)


def moteur_disponible() -> bool:
    moteur = os.environ.get("ATELIER_AI", "claude")
    binaire = moteur.split(":", 1)[0]
    return shutil.which(binaire) is not None


def demander_aide(etape: Etape, code_eleve: str, question: str, niveau: int) -> str:
    if not moteur_disponible():
        return "Moteur IA indisponible. Le reste de l'atelier marche, compiler, tester, lancer."
    prompt = construire_prompt(etape, code_eleve, question, niveau)
    moteur = os.environ.get("ATELIER_AI", "claude")
    try:
        r = subprocess.run([moteur.split(":", 1)[0], "-p", prompt],
                           capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return "Le moteur IA n'a pas répondu à temps."
    # moteur trouvé mais en échec au runtime (auth, quota), on ne renvoie pas son
    # erreur brute comme si c'était une aide, et on ne la passe pas au filtre.
    if r.returncode != 0 and not r.stdout.strip():
        return "Le moteur IA a renvoyé une erreur. Réessaie, ou demande à ton tuteur."
    reponse = r.stdout.strip() or r.stderr.strip()
    corrige = _chemin_corrige(etape).read_text(encoding="utf-8")
    return filtre_solution(reponse, corrige)
