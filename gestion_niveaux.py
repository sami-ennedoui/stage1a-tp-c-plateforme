"""Outil d'auteur : ajouter, retirer et réordonner les niveaux d'un parcours.

Un niveau est un sous-dossier de `contenu/<parcours>/` (meta.json, enonce.md,
starter.c, corrige.c) référencé dans la liste `ordre` de `parcours.json`. Ce module
ne fait que de la manipulation de fichiers, sans PyQt ni compilation : il est
testable sans écran. La fenêtre (dialogue_niveaux.py) n'est qu'une couche au-dessus.

Choix retenus avec l'utilisateur :
  - « Retirer » DÉTACHE seulement : l'id sort de `ordre`, le dossier reste sur le
    disque (désactivé). Rien n'est effacé, le geste est réversible.
"""
import json
import re
from pathlib import Path

# modes reconnus par modele_etape / executeur pour un parcours isolé
MODES = ("programme", "test_fourni", "test_a_ecrire")
_ID_VALIDE = re.compile(r"^[a-z][a-z0-9_]*$")

GABARIT_ENONCE = """# {titre}

<Écris ici l'énoncé de l'exercice, en Markdown.>

La porte vérifie que ton programme produit la sortie attendue.
"""

GABARIT_STARTER = """#include <stdio.h>

int main(void)
{
    /* À toi d'écrire le programme. */

    return 0;
}
"""

GABARIT_CORRIGE = """#include <stdio.h>

int main(void)
{
    /* Corrigé de référence. La porte le rejoue pour valider le niveau. */

    return 0;
}
"""


def _fichier_parcours(dossier_parcours: Path) -> Path:
    return dossier_parcours / "parcours.json"


def _lire_json(dossier_parcours: Path) -> dict:
    return json.loads(_fichier_parcours(dossier_parcours).read_text(encoding="utf-8"))


def _ecrire_json(dossier_parcours: Path, donnees: dict) -> None:
    # même forme que les parcours.json du dépôt : indent 2, accents gardés, saut final
    _fichier_parcours(dossier_parcours).write_text(
        json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def lister_niveaux(dossier_parcours: Path) -> list[str]:
    """Renvoie la liste ordonnée des ids de niveaux actifs du parcours."""
    return list(_lire_json(dossier_parcours).get("ordre", []))


def dossiers_detaches(dossier_parcours: Path) -> list[str]:
    """Sous-dossiers de niveau présents sur le disque mais absents de `ordre`.

    Ce sont les niveaux détachés (retirés du parcours mais conservés)."""
    actifs = set(lister_niveaux(dossier_parcours))
    detaches = []
    for enfant in sorted(dossier_parcours.iterdir()):
        if enfant.is_dir() and (enfant / "meta.json").exists() and enfant.name not in actifs:
            detaches.append(enfant.name)
    return detaches


def ajouter_niveau(
    dossier_parcours: Path,
    ident: str,
    titre: str,
    *,
    mode: str = "programme",
    type_niveau: str = "programme",
    cran_debloque: int = 1,
    noeud_cours: str = "",
    fichier_edite: str = "programme.c",
    sortie_attendue: list | None = None,
    position: int | None = None,
) -> Path:
    """Crée le dossier du niveau, ses gabarits, et l'insère dans `ordre`.

    `position` est l'indice d'insertion (None = à la fin). Lève ValueError si l'id est
    invalide, déjà présent dans `ordre`, ou si un dossier du même nom existe déjà.
    Renvoie le chemin du dossier créé.
    """
    ident = ident.strip()
    titre = titre.strip()
    if not _ID_VALIDE.match(ident):
        raise ValueError(
            "Identifiant invalide. Minuscules, chiffres et « _ » seulement, "
            "il doit commencer par une lettre (ex : ex14_boucles)."
        )
    if not titre:
        raise ValueError("Le titre ne peut pas être vide.")
    if mode not in MODES:
        raise ValueError(f"Mode inconnu « {mode} ». Attendu : {', '.join(MODES)}.")

    donnees = _lire_json(dossier_parcours)
    ordre = donnees.setdefault("ordre", [])
    if ident in ordre:
        raise ValueError(f"Le niveau « {ident} » est déjà dans le parcours.")

    dossier = dossier_parcours / ident
    if dossier.exists():
        raise ValueError(
            f"Un dossier « {ident} » existe déjà (peut-être un niveau détaché). "
            "Choisis un autre identifiant."
        )

    dossier.mkdir(parents=True)
    meta = {
        "id": ident,
        "titre": titre,
        "type": type_niveau,
        "mode": mode,
        "cran_debloque": cran_debloque,
        "noeud_cours": noeud_cours,
        "fichier_edite": fichier_edite,
        "sortie_attendue": sortie_attendue if sortie_attendue is not None else [],
    }
    (dossier / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (dossier / "enonce.md").write_text(GABARIT_ENONCE.format(titre=titre), encoding="utf-8")
    (dossier / "starter.c").write_text(GABARIT_STARTER, encoding="utf-8")
    (dossier / "corrige.c").write_text(GABARIT_CORRIGE, encoding="utf-8")

    if position is None or position >= len(ordre):
        ordre.append(ident)
    else:
        ordre.insert(max(0, position), ident)
    _ecrire_json(dossier_parcours, donnees)
    return dossier


def retirer_niveau(dossier_parcours: Path, ident: str) -> None:
    """Détache un niveau : le retire de `ordre`, laisse son dossier sur le disque.

    Lève ValueError si l'id n'est pas dans le parcours."""
    donnees = _lire_json(dossier_parcours)
    ordre = donnees.get("ordre", [])
    if ident not in ordre:
        raise ValueError(f"Le niveau « {ident} » n'est pas dans le parcours.")
    ordre.remove(ident)
    _ecrire_json(dossier_parcours, donnees)


def reattacher_niveau(dossier_parcours: Path, ident: str, position: int | None = None) -> None:
    """Remet dans `ordre` un niveau détaché dont le dossier existe encore."""
    dossier = dossier_parcours / ident
    if not (dossier / "meta.json").exists():
        raise ValueError(f"Aucun dossier de niveau « {ident} » à réattacher.")
    donnees = _lire_json(dossier_parcours)
    ordre = donnees.setdefault("ordre", [])
    if ident in ordre:
        raise ValueError(f"Le niveau « {ident} » est déjà dans le parcours.")
    if position is None or position >= len(ordre):
        ordre.append(ident)
    else:
        ordre.insert(max(0, position), ident)
    _ecrire_json(dossier_parcours, donnees)


def deplacer_niveau(dossier_parcours: Path, ident: str, delta: int) -> None:
    """Décale un niveau dans `ordre` de `delta` places (-1 = monter, +1 = descendre)."""
    donnees = _lire_json(dossier_parcours)
    ordre = donnees.get("ordre", [])
    if ident not in ordre:
        raise ValueError(f"Le niveau « {ident} » n'est pas dans le parcours.")
    i = ordre.index(ident)
    j = max(0, min(len(ordre) - 1, i + delta))
    if i == j:
        return
    ordre.insert(j, ordre.pop(i))
    _ecrire_json(dossier_parcours, donnees)
