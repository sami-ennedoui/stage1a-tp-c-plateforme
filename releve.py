"""Relevé de progression lisible sans écran ni serveur, pour le mode local.
L'empreinte détecte une modification accidentelle du fichier, elle ne protège
en rien contre une falsification volontaire : l'algorithme est ici même, dans
le code que l'étudiant possède."""
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import chemins
import progression
from modele_etape import charger_parcours


def pourcentage(validees: int, total: int) -> float:
    """Même formule que le compagnon, compagnon/base.py:score, pour que les
    deux modes affichent le même chiffre."""
    return min(100, round(100 * validees / total, 1))


def texte(parcours_nom: str,
         fichier_progression: Path = chemins.PROGRESSION_FICHIER) -> str:
    etapes = charger_parcours(chemins.contenu_racine(parcours_nom))
    prog = progression.charger(fichier_progression)
    total = len(etapes)
    validees = sum(1 for e in etapes if e.id in prog.etapes_faites)
    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lignes = [
        "Relevé de progression, Atelier TP C",
        f"Parcours : {parcours_nom}",
        f"Établi le : {horodatage}",
        "",
        f"Étapes validées : {validees} sur {total}, soit {pourcentage(validees, total)} %",
        "",
    ]
    for e in etapes:
        marque = "x" if e.id in prog.etapes_faites else " "
        lignes.append(f"  [{marque}] {e.id:<22}{e.titre}")
    corps = "\n".join(lignes)
    empreinte = hashlib.sha256(corps.encode("utf-8")).hexdigest()[:8]
    return corps + f"\n\nEmpreinte : {empreinte}\n"


def ecrire(contenu: str, dossier: Path = Path(".")) -> Path:
    chemin = Path(dossier) / "releve.txt"
    chemin.write_text(contenu, encoding="utf-8")
    return chemin
