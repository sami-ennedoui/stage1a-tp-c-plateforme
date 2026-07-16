"""Tests de la fabrication des clés de l'outil LTI.

Le vrai risque n'est pas de mal afficher une clé, c'est d'en fabriquer deux qui ne
vont pas ensemble : le service démarre, la page d'accueil s'affiche, et seul un vrai
lancement LTI échoue à la signature. D'où le test d'appariement.
"""
import subprocess
import sys
import unittest

from cryptography.hazmat.primitives import serialization

from compagnon import cles


def publique_deduite(privee_pem: str) -> str:
    cle = serialization.load_pem_private_key(privee_pem.encode(), password=None)
    return cle.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo).decode()


class TestPaire(unittest.TestCase):
    def test_la_paire_generee_va_ensemble(self):
        privee, publique = cles.generer_paire()
        self.assertEqual(publique_deduite(privee), publique)


class TestSortieEnv(unittest.TestCase):
    """--env doit être avalable par le shell sans découpage à la main."""

    def lancer(self, *args) -> str:
        r = subprocess.run([sys.executable, "-m", "compagnon.cles", *args],
                           capture_output=True, text=True, check=True)
        return r.stdout

    def test_env_donne_les_deux_cles_en_un_seul_appel(self):
        sortie = self.lancer("--env")
        self.assertIn("TOOL_PRIVATE_KEY='", sortie)
        self.assertIn("TOOL_PUBLIC_KEY='", sortie)

    def test_le_shell_relit_la_sortie_et_les_cles_vont_ensemble(self):
        """Le test qui compte : on source vraiment, comme le guide le demande."""
        sortie = self.lancer("--env")
        lu = subprocess.run(
            ["bash", "-c", 'set -a; eval "$1"; set +a; '
                           'printf "%s" "$TOOL_PRIVATE_KEY"; '
                           'printf "\\0"; printf "%s" "$TOOL_PUBLIC_KEY"',
             "_", sortie],
            capture_output=True, text=True, check=True)
        privee, publique = lu.stdout.split("\0")
        self.assertTrue(privee.startswith("-----BEGIN"), privee[:40])
        self.assertEqual(publique_deduite(privee), publique)

    def test_sans_option_la_sortie_reste_lisible_pour_un_humain(self):
        sortie = self.lancer()
        self.assertIn("TOOL_PRIVATE_KEY :", sortie)
        self.assertIn("TOOL_PUBLIC_KEY :", sortie)


if __name__ == "__main__":
    unittest.main()
