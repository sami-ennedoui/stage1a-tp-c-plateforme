"""Garde-fou structurel du tuteur. On ne masque pas un code d'aide sur ses mots, on le
masque seulement s'il ouvrirait vraiment la porte de l'étape. On reconstruit le code à
partir de la réponse de l'IA et on rejoue la porte de l'exercice dessus. C'est le
comportement compilé qui juge, pas le vocabulaire, donc la paraphrase ne le contourne pas.
Ce filtre complète le filtre lexical ligne à ligne de tuteur_ia, il ne le remplace pas."""
import re

import executeur
from modele_etape import Etape

_BLOC = r"```(?:c|cpp|C)?\s*\n(.*?)```"


def extraire_blocs_c(reponse: str) -> list[str]:
    """Renvoie le contenu de chaque bloc de code clôturé par ``` dans la réponse."""
    return re.findall(_BLOC, reponse, re.S)


def _porte_ouvre(etape: Etape, code: str) -> bool:
    """Rejoue la porte de l'étape sur un code candidat. True veut dire que la porte
    s'ouvrirait, donc ce code est une solution qui ferait passer l'étudiant. On ne juge
    que les étapes dont la porte se joue sur un code seul. Les autres, test à écrire et
    projet, sortent du périmètre et sont laissées au filtre lexical."""
    try:
        if etape.mode == "programme":
            return executeur.porte_programme(etape, code).ok
        if etape.mode == "test_fourni":
            return executeur.porte_perso(etape, code).ok
    except Exception:
        return False
    return False


def _candidats(etape: Etape, blocs: list[str]) -> list[str]:
    """Reconstructions à éprouver contre la porte. Chaque bloc seul attrape le dump en un
    bloc. L'union des blocs attrape la fuite éparpillée, quand le modèle refuse le bloc
    unique mais donne les morceaux séparément. Pour un programme, on emballe aussi l'union
    dans un main si elle n'en a pas, car les fragments sont alors des lignes à coller dans
    un main existant."""
    cands = list(blocs)
    if len(blocs) >= 2:
        union = "\n".join(blocs)
        cands.append(union)
        if etape.mode == "programme" and "main" not in union:
            cands.append("#include <stdio.h>\nint main(void){\n" + union + "\nreturn 0;\n}\n")
    return cands


def solution_ouvre_la_porte(etape: Etape, reponse: str) -> bool:
    """Vrai si le code de la réponse, un bloc ou l'union des blocs, ferait passer la porte."""
    blocs = extraire_blocs_c(reponse)
    if not blocs:
        return False
    return any(_porte_ouvre(etape, c) for c in _candidats(etape, blocs))


def masquer_si_solution(etape: Etape, reponse: str) -> str:
    """Si le code de la réponse ouvrirait la porte, on retire tout le code et on garde la
    prose explicative. Sinon on rend la réponse inchangée. Une fuite en prose pure, sans
    bloc de code, échappe à ce filtre, c'est sa limite connue."""
    if not solution_ouvre_la_porte(etape, reponse):
        return reponse
    refus = ("```\n… (code retiré par le garde-fou : tel quel il ferait passer la porte de "
             "l'étape, c'est donc la solution. Repose ta question sur un seul point précis.) …\n```")
    return re.sub(_BLOC, refus, reponse, flags=re.S)
