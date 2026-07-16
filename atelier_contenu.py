"""Édite le contenu pédagogique sans toucher au code : crée, vérifie et retire
des parcours et des étapes. Bibliothèque standard uniquement."""
import argparse
import json
import sys
from pathlib import Path

import chemins

RACINE_CONTENU = chemins.RACINE / "contenu"


def _erreur(message: str) -> None:
    print(f"Erreur : {message}", file=sys.stderr)


def _ecrire_json(fichier: Path, donnees: dict) -> None:
    fichier.write_text(json.dumps(donnees, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")


def commande_nouveau_parcours(nom: str, racine: Path = RACINE_CONTENU) -> int:
    """Crée contenu/<nom>/parcours.json vide, en mode isole."""
    dossier = racine / nom
    if dossier.exists():
        _erreur(f"un parcours nommé {nom} existe déjà")
        return 1
    dossier.mkdir(parents=True)
    _ecrire_json(dossier / "parcours.json", {"ordre": [], "mode": "isole"})
    print(f"Parcours {nom} créé.")
    return 0


def main(argv=None) -> int:
    analyseur = argparse.ArgumentParser(
        description="Édite le contenu pédagogique : parcours et étapes.")
    sous = analyseur.add_subparsers(dest="commande", required=True)

    p_nouveau_parcours = sous.add_parser("nouveau-parcours", help="Crée un parcours vide.")
    p_nouveau_parcours.add_argument("nom")

    args = analyseur.parse_args(argv)
    if args.commande == "nouveau-parcours":
        return commande_nouveau_parcours(args.nom)
    return 1


if __name__ == "__main__":
    sys.exit(main())
