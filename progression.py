"""État persistant de l'étudiant et règles de déverrouillage. Aucune UI."""
from dataclasses import dataclass, asdict
from pathlib import Path
import json

import chemins
from modele_etape import Etape


@dataclass
class Progression:
    etapes_faites: list[str]
    cran_max: int


def charger(fichier: Path = chemins.PROGRESSION_FICHIER) -> Progression:
    if not Path(fichier).exists():
        return Progression(etapes_faites=[], cran_max=0)
    d = json.loads(Path(fichier).read_text(encoding="utf-8"))
    return Progression(etapes_faites=d.get("etapes_faites", []), cran_max=d.get("cran_max", 0))


def sauver(p: Progression, fichier: Path = chemins.PROGRESSION_FICHIER) -> None:
    Path(fichier).write_text(json.dumps(asdict(p), ensure_ascii=False, indent=2),
                             encoding="utf-8")


def etape_deverrouillee(etape: Etape, parcours: list[Etape], prog: Progression,
                        libre: bool = False) -> bool:
    """Déverrouillée si toutes les étapes qui la précèdent dans le parcours sont faites.

    Dans un parcours libre, tout est ouvert d'emblée : on révise un point précis sans
    refaire la file. Le déverrouillage reste porté par le parcours et non par le nom du
    parcours, pour que le même contenu puisse servir aux deux usages."""
    if libre:
        return True
    for e in parcours:
        if e.id == etape.id:
            return True
        if e.id not in prog.etapes_faites:
            return False
    return False


def valider(etape: Etape, prog: Progression) -> Progression:
    faites = list(prog.etapes_faites)
    if etape.id not in faites:
        faites.append(etape.id)
    return Progression(faites, max(prog.cran_max, etape.cran_debloque))


def cran_disponible(prog: Progression) -> int:
    return prog.cran_max


def fusionner(prog: Progression, ids, parcours: list[Etape]) -> Progression:
    """Ajoute à la progression des étapes validées venues d'ailleurs (le compagnon,
    à l'appairage) et remonte le cran débloqué en conséquence.

    Sert la reprise multi-poste : un étudiant qui a fait des étapes sur une machine
    les retrouve déverrouillées après connexion sur une autre. Un id inconnu du
    parcours courant est conservé mais ne change pas le cran : il vient d'un autre
    parcours et ne déverrouille rien ici (les ids ne se recoupent pas entre parcours).
    """
    faites = list(prog.etapes_faites)
    cran = prog.cran_max
    par_id = {e.id: e for e in parcours}
    for i in ids:
        if i not in faites:
            faites.append(i)
        e = par_id.get(i)
        if e is not None:
            cran = max(cran, e.cran_debloque)
    return Progression(faites, cran)
