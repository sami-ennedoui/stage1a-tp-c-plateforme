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


def etape_deverrouillee(etape: Etape, parcours: list[Etape], prog: Progression) -> bool:
    """Déverrouillée si toutes les étapes qui la précèdent dans le parcours sont faites."""
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
