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

# Style imposé à tous les crans : réponses courtes et directes, pas de flatterie,
# pas de pluie de questions. L'étudiant veut être débloqué, pas coaché.
_STYLE = (
    "Style de réponse, à respecter strictement :\n"
    "- Va droit au but. Réponds en 2 à 5 phrases, pas un cours.\n"
    "- Aucune formule flatteuse ni de remplissage : jamais de « bonne question », "
    "« bon réflexe », « tu as raison », « c'est exactement le cœur de l'exercice », etc. "
    "Commence directement par le fond.\n"
    "- Nomme clairement ce qui ne va pas et le concept en jeu ; ne fais pas deviner "
    "l'évidence par une énigme.\n"
    "- Au plus UNE question à la fin, et seulement si elle est vraiment utile. Ne pose "
    "pas une liste de questions."
)

_CONSIGNE_CRAN = {
    0: "Cran N0. Explique directement le concept ou l'erreur en jeu, sans donner ni "
       "écrire la ligne de solution. Tu peux nommer précisément ce qui cloche (le type, "
       "le format, la syntaxe) ; l'étudiant écrit la correction lui-même.",
    1: "Cran N1. Tu peux donner un squelette vide ou une analogie, mais pas la solution "
       "écrite. Montre la forme, pas le contenu.",
    2: "Cran N2. Tu peux proposer une piste candidate, mais demande à l'étudiant de la "
       "justifier et de la vérifier lui-même, sans affirmer qu'elle est correcte.",
    3: "Cran N3. Tu es libre d'aider comme tu veux, mais reste concis et direct.",
}


def _bloc_historique(historique) -> str:
    """Rend les échanges précédents de l'exercice sous forme de texte injectable dans le
    prompt, pour que le tuteur suive le fil (mémoire gérée par l'appli, cf. approche B).
    historique est une liste de couples (question, réponse). Vide -> chaîne vide."""
    if not historique:
        return ""
    tours = "\n\n".join(f"Étudiant : {q}\nToi (tuteur) : {r}" for q, r in historique)
    return ("Échanges précédents dans cet exercice (garde le fil, ne te répète pas, "
            "tiens compte de ce que l'étudiant a déjà répondu) :\n" + tours + "\n\n")


def construire_prompt(etape: Etape, code_eleve: str, question: str, niveau: int,
                      historique=None, console: str = "") -> str:
    enonce = (etape.dossier / "enonce.md").read_text(encoding="utf-8")
    parties = [
        "Tu es un tuteur de programmation C pour un étudiant débutant. Tu n'es jamais "
        "celui qui résout à sa place.",
        _STYLE,
        _CONSIGNE_CRAN.get(niveau, _CONSIGNE_CRAN[0]),
        f"Énoncé de l'étape :\n{enonce}",
    ]
    # Le code et la console ne sont joints que si l'étudiant l'a demandé (cases du
    # dialogue d'aide). Par défaut le tuteur ne voit que l'énoncé et la question.
    if code_eleve and code_eleve.strip():
        parties.append(f"Code actuel de l'étudiant :\n{code_eleve}")
    if console and console.strip():
        parties.append(f"Ce que la console affiche (résultat de compilation ou de test) :\n{console}")
    bloc_hist = _bloc_historique(historique)
    if bloc_hist:
        parties.append(bloc_hist.rstrip())
    parties.append(f"Question de l'étudiant :\n{question}")
    return "\n\n".join(parties) + "\n"


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


# Marque insérée à la place d'une ligne de solution reproduite. Exposée pour que
# l'appli sache, après coup, si le filtre a réellement masqué quelque chose (signal
# de recherche : mesure si la bride sert face à un chercheur de solution).
MARQUE_MASQUE = "… (ligne masquée par le filtre anti-solution) …"


def filtre_solution(reponse: str, corrige: str) -> str:
    """Masque dans la réponse les lignes qui reproduisent une ligne du corrigé,
    laisse passer tout le reste."""
    cibles = _cles_significatives(corrige)
    sortie = []
    for ligne in reponse.splitlines():
        cle = _cle(ligne)
        if cle is not None and cle in cibles:
            sortie.append("    " + MARQUE_MASQUE)
        else:
            sortie.append(ligne)
    return "\n".join(sortie)


def filtre_a_masque(reponse: str) -> bool:
    """Vrai si `reponse` (déjà passée au filtre) contient au moins une ligne masquée."""
    return MARQUE_MASQUE in reponse


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


def _commande(moteur: str, prompt: str, modele: str = "") -> list[str]:
    """Commande d'un tour non interactif, propre à chaque moteur.
    claude : 'claude -p <prompt>'. codex : 'codex exec <prompt>' avec
    --skip-git-repo-check (l'atelier ne tourne pas dans un dépôt git) ; le bac à
    sable de codex reste en lecture seule, le tuteur ne fait que répondre.
    modele : optionnel, force un modèle (ex. 'sonnet', 'haiku' pour claude). Sert
    surtout au banc de tests, qui génère beaucoup et n'a pas besoin du plus gros modèle."""
    binaire = _binaire(moteur)
    if binaire == "codex":
        cmd = ["codex", "exec", "--skip-git-repo-check"]
        if modele:
            cmd += ["--model", modele]
        return cmd + [prompt]
    cmd = [binaire, "-p"]
    if modele:
        cmd += ["--model", modele]
    return cmd + [prompt]


def moteur_disponible() -> bool:
    return _moteur_choisi() is not None


# Messages renvoyés quand l'aide n'a pas pu être produite. Exposés pour que l'appelant
# (la fenêtre) sache ne pas les mémoriser dans l'historique de conversation.
ERR_INDISPONIBLE = "Moteur IA indisponible. Le reste de l'atelier marche, compiler, tester, lancer."
ERR_TIMEOUT = "Le moteur IA n'a pas répondu à temps."
ERR_RUNTIME = "Le moteur IA a renvoyé une erreur. Réessaie, ou demande à ton tuteur."
_ERREURS = {ERR_INDISPONIBLE, ERR_TIMEOUT, ERR_RUNTIME}


def reponse_est_erreur(reponse: str) -> bool:
    """Vrai si la réponse est un message d'échec du tuteur (à ne pas mémoriser)."""
    return reponse in _ERREURS


def demander_aide(etape: Etape, code_eleve: str, question: str, niveau: int,
                  historique=None, console: str = "", modele: str = "") -> str:
    moteur = _moteur_choisi()
    if moteur is None:
        return ERR_INDISPONIBLE
    prompt = construire_prompt(etape, code_eleve, question, niveau, historique, console)
    try:
        # stdin fermé : sinon 'codex exec' lit stdin et attend son EOF, ce qui bloque
        # quand le tuteur est lancé en sous-processus sans console (fenêtre PyQt).
        # encoding utf-8 : les moteurs répondent en UTF-8 ; sans ça la sortie serait
        # décodée dans l'encodage local (cp1252 sous Windows FR) et « cœur » deviendrait
        # « cÅ“ur ». creationflags : pas de fenêtre cmd qui clignote au clic.
        r = subprocess.run(_commande(moteur, prompt, modele),
                           stdin=subprocess.DEVNULL,
                           capture_output=True, encoding="utf-8", errors="replace",
                           creationflags=_SANS_FENETRE, timeout=120)
    except subprocess.TimeoutExpired:
        return ERR_TIMEOUT
    # moteur trouvé mais en échec au runtime (auth, quota), on ne renvoie pas son
    # erreur brute comme si c'était une aide, et on ne la passe pas au filtre.
    if r.returncode != 0 and not r.stdout.strip():
        return ERR_RUNTIME
    reponse = r.stdout.strip() or r.stderr.strip()
    corrige = _chemin_corrige(etape).read_text(encoding="utf-8")
    return filtre_solution(reponse, corrige)


# --- Mode démo : le tuteur écrit le programme lui-même -----------------------
# Réservé au mode démo (banc de tests, exploration du correcteur). Ici on NE passe
# PAS le filtre anti-solution : le but est justement d'obtenir un programme complet
# et de voir comment la porte réagit à différentes réponses.

_CONSIGNE_GENERATION = (
    "Tu es en MODE DÉMO, tu n'es pas un tuteur ici. Écris un programme C complet qui "
    "résout l'exercice ci-dessous et respecte la sortie attendue. Réponds UNIQUEMENT par "
    "le code, dans un seul bloc ```c ... ```, sans aucune explication avant ni après."
)


def construire_prompt_generation(etape: Etape, variante: str = "") -> str:
    enonce = (etape.dossier / "enonce.md").read_text(encoding="utf-8")
    parties = [_CONSIGNE_GENERATION, f"Énoncé :\n{enonce}"]
    if variante and variante.strip():
        parties.append("Contrainte supplémentaire imposée pour ce test :\n" + variante.strip())
    return "\n\n".join(parties) + "\n"


def _extraire_code(reponse: str) -> str:
    """Récupère le premier bloc ```c ... ``` de la réponse. À défaut de bloc, renvoie la
    réponse brute (certains moteurs répondent sans clôture markdown)."""
    m = re.search(r"```(?:[cC])?\s*\n?(.*?)```", reponse, re.DOTALL)
    code = m.group(1) if m else reponse
    return code.strip() + "\n"


def generer_solution(etape: Etape, variante: str = "", timeout: int = 120,
                     modele: str = "") -> str:
    """MODE DÉMO seulement. Demande au moteur d'écrire un programme complet pour l'étape
    et renvoie le code (sans filtre). `variante` est une contrainte optionnelle ('' pour
    une solution correcte, ou p. ex. 'introduis une erreur de format' pour tester le rejet
    par la porte). `modele` force un modèle (ex. 'sonnet', 'haiku'). Renvoie un des messages
    ERR_* si le moteur n'a pas répondu."""
    moteur = _moteur_choisi()
    if moteur is None:
        return ERR_INDISPONIBLE
    prompt = construire_prompt_generation(etape, variante)
    try:
        r = subprocess.run(_commande(moteur, prompt, modele),
                           stdin=subprocess.DEVNULL,
                           capture_output=True, encoding="utf-8", errors="replace",
                           creationflags=_SANS_FENETRE, timeout=timeout)
    except subprocess.TimeoutExpired:
        return ERR_TIMEOUT
    if r.returncode != 0 and not r.stdout.strip():
        return ERR_RUNTIME
    return _extraire_code(r.stdout.strip() or r.stderr.strip())
