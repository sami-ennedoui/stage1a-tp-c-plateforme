"""Compile et exécute du C, rend un résultat. Aucune UI ici.
Le code de sortie du programme fait foi, pas le texte affiché."""
from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile

import chemins
from modele_etape import Etape


@dataclass
class Resultat:
    ok: bool
    sortie: str


def _compiler_et_lancer(sources: list[Path], includes: list[Path],
                        cflags: list[str] = [], libs: list[str] = [],
                        timeout: int = 15) -> Resultat:
    with tempfile.TemporaryDirectory() as d:
        binaire = Path(d) / "prog"
        cmd = ["gcc", "-Wall", "-Wno-unused-parameter", "-Wno-unused-variable"]
        cmd += [f"-I{i}" for i in includes]
        cmd += cflags
        cmd += [str(s) for s in sources]
        cmd += libs
        cmd += ["-lm", "-o", str(binaire)]
        comp = subprocess.run(cmd, capture_output=True, text=True)
        if comp.returncode != 0:
            return Resultat(False, "Erreur de compilation :\n" + comp.stderr)
        try:
            run = subprocess.run([str(binaire)], capture_output=True, text=True,
                                 timeout=timeout)
        except subprocess.TimeoutExpired:
            return Resultat(False, "Le test a dépassé le délai, boucle infinie probable.")
        return Resultat(run.returncode == 0, run.stdout + run.stderr)


def porte_perso(etape: Etape, code_eleve: str) -> Resultat:
    """Compile le code de l'étudiant avec tests.c de l'étape, exécute, code 0 = porte ouverte."""
    with tempfile.TemporaryDirectory() as d:
        soumission = Path(d) / "soumission.c"
        soumission.write_text(code_eleve, encoding="utf-8")
        sources = [soumission, etape.dossier / "tests.c"]
        includes = [etape.dossier]
        return _compiler_et_lancer(sources, includes)
