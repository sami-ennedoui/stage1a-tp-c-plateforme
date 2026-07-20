"""Le garde-fou contre un bug d'accents qui est déjà revenu trois fois.

`subprocess.run(..., text=True)` sans `encoding` décode la sortie dans l'encodage
local. Sous Linux c'est UTF-8 et tout va bien, donc **le bug est invisible ici**.
Sous Windows français c'est cp1252, gcc écrit en UTF-8, et l'étudiant lit
« fenÃªtre » au lieu de « fenêtre ».

C'est ce qui le rend récurrent : le poste qui écrit le code ne peut pas le voir,
et le poste qui le voit ne l'a pas écrit. Corrigé en `344b0a9`, revenu dans du
code neuf de `compiler_et_executer`, signalé le 2026-07-20 par le poste Windows
dans `NOTE-WINDOWS-2026-07-20-clangd-et-fenetres.md`. Une revue humaine ne
l'attrapera pas la quatrième fois non plus, c'est pourquoi ce test existe.

Il lit le code source du dépôt, ne lance aucun processus, et tourne donc partout.
"""
import re
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# Dépendances installées et sorties de build : hors de notre responsabilité.
IGNORES = {".git", ".venv", "__pycache__", "site-packages", "w64devkit", "clangd",
           ".build", "_bundle", "espace_session"}

# Ce fichier se cite lui-même, en prose et dans son propre cas de test.
MOI = Path(__file__).name

# Dette connue, en cours de correction sur la branche `windows-clangd-embarque`.
# Ces fichiers appartiennent au poste Windows, qui les tient au moment où ce test
# est écrit ; les corriger d'ici créerait un conflit sur des lignes qu'il modifie.
# Ce n'est PAS une liste d'exceptions permanente : le test
# `test_la_dette_connue_a_fondu` ci-dessous casse dès qu'un de ces fichiers
# devient propre, pour forcer sa sortie de la liste.
DETTE = {"executeur.py", "dialogue_diagnostic.py"}

# Un appel subprocess avec ses arguments, y compris sur plusieurs lignes.
_APPEL = re.compile(r"subprocess\.(?:run|Popen|check_output|call)\("
                    r"(?:[^()]|\([^()]*\))*\)", re.S)


def _fichiers_python(racine: Path):
    for f in sorted(racine.rglob("*.py")):
        if IGNORES & set(f.parts) or f.name == MOI:
            continue
        yield f


def _appels_fautifs(racine: Path) -> list[str]:
    """Les `subprocess` qui décodent du texte sans dire dans quel encodage."""
    fautifs = []
    for f in _fichiers_python(racine):
        source = f.read_text(encoding="utf-8")
        for m in _APPEL.finditer(source):
            bloc = m.group(0)
            decode = "text=True" in bloc or "universal_newlines=True" in bloc
            if decode and "encoding=" not in bloc:
                ligne = source[: m.start()].count("\n") + 1
                fautifs.append(f"{f.relative_to(racine)}:{ligne}")
    return fautifs


class TestEncodageSubprocess(unittest.TestCase):

    def test_aucun_subprocess_ne_decode_sans_encodage(self):
        """S'il casse : ajoute `encoding="utf-8"` à l'appel signalé.

        N'agrandis pas `DETTE` pour le faire taire. Le seul cas légitime serait un
        programme dont la sortie n'est pas de l'UTF-8, et il faudrait alors nommer
        son encodage réel, ce qui satisfait aussi ce test.
        """
        fautifs = [x for x in _appels_fautifs(RACINE)
                   if Path(x.split(":")[0]).name not in DETTE]
        self.assertEqual(
            fautifs, [],
            "subprocess qui décodent sans encodage explicite, donc illisibles sous "
            "Windows français :\n  " + "\n  ".join(fautifs))

    def test_la_dette_connue_a_fondu(self):
        """Empêche `DETTE` de devenir une liste d'exceptions permanente.

        Il casse quand un fichier de la dette est devenu propre, et demande alors
        de le retirer de la liste. Sans lui, une exception temporaire survit pour
        toujours, et le garde-fou se vide de son sens sans que personne ne le voie.
        """
        sales = {Path(x.split(":")[0]).name for x in _appels_fautifs(RACINE)}
        gueris = sorted(DETTE - sales)
        self.assertEqual(
            gueris, [],
            "ces fichiers n'ont plus de subprocess fautif : retire-les de DETTE "
            "dans ce fichier, la dette doit finir vide. " + ", ".join(gueris))

    def test_le_filet_attrape_vraiment(self):
        """Le premier test passe une fois le dépôt propre, et passerait tout autant
        s'il ne regardait rien. Celui-ci prouve qu'il attrape."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            faux = Path(d)
            (faux / "coupable.py").write_text(
                "import subprocess\n"
                "r = subprocess.run(['gcc', '-v'],\n"
                "                   capture_output=True, text=True)\n",
                encoding="utf-8")
            (faux / "innocent.py").write_text(
                "import subprocess\n"
                "r = subprocess.run(['gcc'], capture_output=True, text=True,\n"
                "                   encoding='utf-8')\n"
                "b = subprocess.run(['gcc'], capture_output=True)\n",
                encoding="utf-8")
            trouves = _appels_fautifs(faux)
        self.assertEqual(len(trouves), 1, trouves)
        self.assertTrue(trouves[0].startswith("coupable.py:"), trouves)


if __name__ == "__main__":
    unittest.main()
