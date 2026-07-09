"""Génère la paire RSA de l'outil LTI, à mettre en variables d'environnement.
Usage : python -m compagnon.cles"""
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


if __name__ == "__main__":
    privee, publique = generer_paire()
    print("TOOL_PRIVATE_KEY :\n" + privee)
    print("TOOL_PUBLIC_KEY :\n" + publique)
