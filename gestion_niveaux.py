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


# fichiers texte d'un niveau, éditables depuis la GUI
FICHIERS_TEXTE = ("enonce.md", "starter.c", "corrige.c")


def dossier_niveau(dossier_parcours: Path, ident: str) -> Path:
    """Chemin du dossier d'un niveau existant. Lève ValueError s'il n'existe pas."""
    d = dossier_parcours / ident
    if not (d / "meta.json").exists():
        raise ValueError(f"Aucun niveau « {ident} » ici.")
    return d


def lire_fichier_niveau(dossier_parcours: Path, ident: str, nom: str) -> str:
    """Contenu d'un fichier texte du niveau, chaîne vide s'il n'existe pas encore."""
    f = dossier_niveau(dossier_parcours, ident) / nom
    return f.read_text(encoding="utf-8") if f.exists() else ""


def ecrire_fichier_niveau(dossier_parcours: Path, ident: str, nom: str, contenu: str) -> None:
    """Écrit un fichier texte du niveau (enonce.md, starter.c, corrige.c)."""
    (dossier_niveau(dossier_parcours, ident) / nom).write_text(contenu, encoding="utf-8")


def lire_meta(dossier_parcours: Path, ident: str) -> dict:
    return json.loads((dossier_niveau(dossier_parcours, ident) / "meta.json")
                      .read_text(encoding="utf-8"))


def ecrire_meta(dossier_parcours: Path, ident: str, meta: dict) -> None:
    """Réécrit meta.json en conservant sa forme (indent 2, accents, saut final)."""
    (dossier_niveau(dossier_parcours, ident) / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def synchroniser_notation(dossier_parcours: Path,
                          fichier_notation: Path | None = None) -> str | None:
    """Réaligne la liste des étapes notées du compagnon sur `ordre`, si ce parcours
    est celui qu'il note. Renvoie un rappel à montrer à l'enseignant (il faut
    redéployer le compagnon) quand la liste a bougé, sinon None.

    Le compagnon note un parcours dont son image Docker ne voit jamais le contenu :
    sa liste vit dans compagnon/etapes_notees.json et doit suivre `ordre` à la main.
    Sans ce câblage, retirer un niveau de be_c plafonnerait la note de toute la promo,
    en silence. Même rôle que atelier_contenu._suivre_notation côté ligne de commande,
    mais rend le message au lieu de l'imprimer pour que la GUI l'affiche.
    """
    import atelier_contenu  # tardif : évite de tirer executeur au chargement du module
    if fichier_notation is None:
        fichier_notation = atelier_contenu.FICHIER_NOTATION
    racine = dossier_parcours.parent
    nom = dossier_parcours.name
    # Ne jamais écrire la vraie notation depuis une racine de test : un parcours
    # temporaire peut porter le nom du parcours noté (piège vécu côté ligne de commande).
    if (fichier_notation == atelier_contenu.FICHIER_NOTATION
            and racine != atelier_contenu.RACINE_CONTENU):
        return None
    if not fichier_notation.exists():
        return None                    # pas de compagnon ici : bundle étudiant, clone partiel
    from compagnon import notation     # tardif : le bundle étudiant n'a pas compagnon/
    if notation.parcours_note(fichier_notation) != nom:
        return None                    # le compagnon note un autre parcours
    try:
        actuelles = notation.charger(fichier_notation)
    except ValueError:
        actuelles = None               # fichier déjà incohérent : on le réécrit d'aplomb
    ordre = lister_niveaux(dossier_parcours)
    if actuelles == ordre:
        return None                    # déjà d'aplomb, rien à signaler
    notation.ecrire(nom, ordre, fichier_notation)
    return (f"« {nom} » est le parcours noté par le compagnon.\n"
            f"Sa liste d'étapes notées a été réalignée sur {len(ordre)} étape(s).\n\n"
            "Le compagnon doit être redéployé pour que les notes en tiennent compte.")
