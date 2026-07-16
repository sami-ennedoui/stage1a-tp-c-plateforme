"""Génère la paire RSA de l'outil LTI, à mettre en variables d'environnement.

    python3 -m compagnon.cles          affiche les deux clés, pour un humain
    python3 -m compagnon.cles --env    écrit du shell, à relire avec « . »

Les deux clés d'un même appel vont ensemble. Deux appels donnent deux paires
dépareillées : le service démarrerait quand même et seul un vrai lancement LTI
échouerait, sans rien dire d'utile. C'est la raison d'être de --env, qui met les
deux clés d'un seul appel dans un fichier que le shell relit sans découpage.
"""
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generer_paire() -> tuple[str, str]:
    cle = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    privee = cle.private_bytes(serialization.Encoding.PEM,
                               serialization.PrivateFormat.TraditionalOpenSSL,
                               serialization.NoEncryption()).decode()
    publique = cle.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    return privee, publique


def en_shell(nom: str, valeur: str) -> str:
    """Une affectation shell que « . » relit telle quelle.

    Les guillemets simples suffisent : du PEM n'est que du base64, des tirets et des
    retours à la ligne. On le vérifie quand même plutôt que de le supposer.
    """
    if "'" in valeur:
        raise ValueError(f"{nom} contient une apostrophe, le guillemet simple ne suffit plus")
    return f"{nom}='{valeur}'"


if __name__ == "__main__":
    privee, publique = generer_paire()
    if "--env" in sys.argv[1:]:
        print("# Paire pour l'outil LTI. À relire avec :  set -a; . ./cles.env; set +a")
        print(en_shell("TOOL_PRIVATE_KEY", privee))
        print(en_shell("TOOL_PUBLIC_KEY", publique))
    else:
        print("TOOL_PRIVATE_KEY :\n" + privee)
        print("TOOL_PUBLIC_KEY :\n" + publique)
