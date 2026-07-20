"""Garde-fou structurel du tuteur. On ne masque pas un code d'aide sur ses mots, on le
masque seulement s'il ouvrirait vraiment la porte de l'étape. On reconstruit le code à
partir de la réponse de l'IA et on rejoue la porte de l'exercice dessus. C'est le
comportement compilé qui juge, pas le vocabulaire, donc la paraphrase ne le contourne pas.
Ce filtre complète le filtre lexical ligne à ligne de tuteur_ia, il ne le remplace pas."""
import re

import executeur
from modele_etape import Etape

_BLOC = r"```(?:c|cpp|C)?\s*\n(.*?)```"


class PorteIndecidable(Exception):
    """Le verdict n'a pas pu être établi : compilateur absent, délai dépassé, etc.

    À distinguer d'une porte qui reste fermée. « Fermée » est un verdict, « indécidable »
    est une absence de verdict, et les deux ne doivent pas mener à la même décision."""


def extraire_blocs_c(reponse: str) -> list[str]:
    """Renvoie le contenu de chaque bloc de code clôturé par ``` dans la réponse."""
    return re.findall(_BLOC, reponse, re.S)


def _porte_ouvre(etape: Etape, code: str) -> bool:
    """Rejoue la porte de l'étape sur un code candidat. True veut dire que la porte
    s'ouvrirait, donc ce code est une solution qui ferait passer l'étudiant. On ne juge
    que les étapes dont la porte se joue sur un code seul. Les autres, test à écrire et
    projet, sortent du périmètre et sont laissées au filtre lexical.

    Lève PorteIndecidable si la porte n'a pas pu être rejouée. Ce cas rendait False
    auparavant, ce qui revenait à conclure « ce code n'ouvre pas la porte » à partir
    d'une compilation qui n'avait pas eu lieu : sans compilateur, le garde-fou laissait
    passer toutes les réponses en se croyant actif."""
    try:
        if etape.mode == "programme":
            return executeur.porte_programme(etape, code).ok
        if etape.mode == "test_fourni":
            return executeur.porte_perso(etape, code).ok
    except Exception as e:
        raise PorteIndecidable(str(e)) from e
    return False        # mode hors périmètre : verdict laissé au filtre lexical


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


def verdict(etape: Etape, reponse: str) -> str:
    """Rend 'ouvre', 'ferme' ou 'indecidable' pour le code contenu dans la réponse.

    On s'arrête au premier candidat qui ouvre, parce que chaque candidat coûte une
    compilation. Un candidat indécidable n'interrompt rien : un autre peut encore
    trancher, et c'est seulement si aucun n'a ouvert que l'indécision compte."""
    blocs = extraire_blocs_c(reponse)
    if not blocs:
        return "ferme"
    indecis = False
    for candidat in _candidats(etape, blocs):
        try:
            if _porte_ouvre(etape, candidat):
                return "ouvre"
        except PorteIndecidable:
            indecis = True
    return "indecidable" if indecis else "ferme"


def solution_ouvre_la_porte(etape: Etape, reponse: str) -> bool:
    """Vrai si le code de la réponse, un bloc ou l'union des blocs, ferait passer la porte.

    Un verdict indécidable rend False : cette fonction répond à « sait-on que c'est la
    solution ? ». Pour décider s'il faut masquer, c'est verdict() qu'il faut lire, pas
    celle-ci, car masquer relève de la prudence et pas de la certitude."""
    return verdict(etape, reponse) == "ouvre"


_REFUS_SOLUTION = (
    "```\n… (code retiré par le garde-fou : tel quel il ferait passer la porte de "
    "l'étape, c'est donc la solution. Repose ta question sur un seul point précis.) …\n```")

# Message distinct du précédent, et c'est délibéré : dire « c'est la solution » quand on
# n'a pas pu compiler serait une accusation que rien n'étaye, et l'étudiant qui suivrait
# le conseil de reformuler tournerait en rond puisque la cause est sur sa machine.
_REFUS_INDECIDABLE = (
    "```\n… (code retiré par le garde-fou : il n'a pas pu vérifier si ce code ouvrirait "
    "la porte, faute d'avoir pu le compiler. Il masque par prudence, lance l'atelier avec "
    "lancer.bat pour que le compilateur soit disponible.) …\n```")


def masquer_si_solution(etape: Etape, reponse: str) -> str:
    """Retire le code de la réponse s'il ouvrirait la porte, ou si on n'a pas pu le
    vérifier ; garde la prose explicative dans les deux cas. Une fuite en prose pure,
    sans bloc de code, échappe à ce filtre, c'est sa limite connue."""
    v = verdict(etape, reponse)
    if v == "ferme":
        return reponse
    refus = _REFUS_SOLUTION if v == "ouvre" else _REFUS_INDECIDABLE
    return re.sub(_BLOC, refus, reponse, flags=re.S)
