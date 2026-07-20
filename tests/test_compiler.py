import tempfile
import unittest
from pathlib import Path

import executeur
from modele_etape import Etape


def _etape(mode="programme", dossier=None):
    return Etape(id="t", titre="T", type="programme", fichier_edite="programme.c",
                 dossier=dossier or Path(tempfile.gettempdir()), mode=mode,
                 sortie_attendue=["peu importe"])


class TestCompilerEtExecuter(unittest.TestCase):
    """Nécessite gcc au PATH (Atelier.bat l'ajoute via w64devkit)."""

    def test_programme_affiche_sa_sortie_sans_juger(self):
        code = '#include <stdio.h>\nint main(void){ printf("bonjour"); return 0; }\n'
        r = executeur.compiler_et_executer(_etape(), code)
        self.assertTrue(r.ok)
        self.assertIn("bonjour", r.sortie)
        # meme si sortie_attendue ne matche pas, on ne parle pas de porte
        self.assertNotIn("manque", r.sortie.lower())
        self.assertNotIn("porte", r.sortie.lower())

    def test_erreur_de_compilation_remontee(self):
        r = executeur.compiler_et_executer(_etape(), "int main(void){ return }\n")
        self.assertFalse(r.ok)
        self.assertIn("compilation", r.sortie.lower())

    def test_programme_sans_sortie_le_dit(self):
        r = executeur.compiler_et_executer(_etape(), "int main(void){ return 0; }\n")
        self.assertTrue(r.ok)
        self.assertIn("aucune sortie", r.sortie.lower())


if __name__ == "__main__":
    unittest.main()
