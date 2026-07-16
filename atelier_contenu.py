"""Édite le contenu pédagogique sans toucher au code : crée, vérifie et retire
des parcours et des étapes. Bibliothèque standard uniquement."""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

import chemins
import executeur
from modele_etape import charger_etape

RACINE_CONTENU = chemins.RACINE / "contenu"

# Nom de dossier valide sous contenu/ : lettres minuscules, chiffres, underscore.
_ID_VALIDE = re.compile(r"^[a-z0-9_]+$")

_STARTER_C = """#include <stdio.h>

int main(void)
{
    /* À toi d'écrire le programme. Remplace ce squelette une fois
       l'énoncé rédigé dans enonce.md, puis mets à jour sortie_attendue
       dans meta.json pour qu'il corresponde à ta vraie sortie. */

    return 0;
}
"""

_CORRIGE_C = """#include <stdio.h>

/* Squelette de départ, à remplacer par la vraie solution. sortie_attendue dans
   meta.json doit rester une ligne que ce fichier affiche et que starter.c
   n'affiche pas : c'est ce qui prouve que la porte distingue les deux. */

int main(void)
{
    printf("etape ok\\n");
    return 0;
}
"""

_ENONCE_MD = """# {titre}

À COMPLÉTER : décris ici l'énoncé pour l'étudiant.

La porte vérifie que le programme affiche la ligne indiquée dans sortie_attendue
de meta.json. Adapte cette ligne en même temps que starter.c et corrige.c.
"""


def _erreur(message: str) -> None:
    print(f"Erreur : {message}", file=sys.stderr)


def _ecrire_json(fichier: Path, donnees: dict) -> None:
    fichier.write_text(json.dumps(donnees, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")


def _lire_json(fichier: Path) -> dict:
    return json.loads(fichier.read_text(encoding="utf-8"))


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


def _ecrire_squelette_etape(dossier_etape: Path, id_etape: str, titre: str, cran: int) -> None:
    """Squelette du mode programme : trivial mais déjà vert, corrige.c affiche une
    ligne que starter.c n'affiche pas, exactement ce que sortie_attendue réclame."""
    meta = {
        "id": id_etape,
        "titre": titre,
        "type": "programme",
        "mode": "programme",
        "cran_debloque": cran,
        "noeud_cours": "",
        "fichier_edite": "programme.c",
        "sortie_attendue": ["etape ok"],
    }
    _ecrire_json(dossier_etape / "meta.json", meta)
    (dossier_etape / "enonce.md").write_text(_ENONCE_MD.format(titre=titre), encoding="utf-8")
    (dossier_etape / "starter.c").write_text(_STARTER_C, encoding="utf-8")
    (dossier_etape / "corrige.c").write_text(_CORRIGE_C, encoding="utf-8")


def commande_nouvelle_etape(nom_parcours: str, id_etape: str, titre: str,
                            apres: str = None, cran: int = 1,
                            racine: Path = RACINE_CONTENU) -> int:
    """Crée une étape squelette, immédiatement valide, et l'insère dans parcours.json."""
    if not _ID_VALIDE.match(id_etape):
        _erreur(f"id d'étape invalide : {id_etape!r} (autorisé : lettres minuscules, "
                "chiffres, underscore)")
        return 1
    dossier_parcours = racine / nom_parcours
    if not dossier_parcours.exists():
        _erreur(f"parcours introuvable : {nom_parcours}")
        return 1
    donnees = _lire_json(dossier_parcours / "parcours.json")
    ordre = donnees.get("ordre", [])
    dossier_etape = dossier_parcours / id_etape
    if id_etape in ordre or dossier_etape.exists():
        _erreur(f"l'id {id_etape} existe déjà dans {nom_parcours}")
        return 1
    if apres is not None:
        if apres not in ordre:
            _erreur(f"--apres désigne une étape absente de {nom_parcours} : {apres}")
            return 1
        position = ordre.index(apres) + 1
    else:
        position = len(ordre)

    dossier_etape.mkdir(parents=True)
    _ecrire_squelette_etape(dossier_etape, id_etape, titre, cran)
    ordre.insert(position, id_etape)
    donnees["ordre"] = ordre
    _ecrire_json(dossier_parcours / "parcours.json", donnees)
    print(f"Étape {id_etape} créée dans {nom_parcours}.")
    return 0


def commande_retirer_etape(nom_parcours: str, id_etape: str, effacer: bool = False,
                           racine: Path = RACINE_CONTENU) -> int:
    """Retire l'id de parcours.json. Avec effacer, supprime aussi le dossier."""
    dossier_parcours = racine / nom_parcours
    if not dossier_parcours.exists():
        _erreur(f"parcours introuvable : {nom_parcours}")
        return 1
    donnees = _lire_json(dossier_parcours / "parcours.json")
    ordre = donnees.get("ordre", [])
    if id_etape not in ordre:
        _erreur(f"étape absente de {nom_parcours} : {id_etape}")
        return 1
    ordre.remove(id_etape)
    donnees["ordre"] = ordre
    _ecrire_json(dossier_parcours / "parcours.json", donnees)
    if effacer:
        shutil.rmtree(dossier_parcours / id_etape, ignore_errors=True)
    print(f"Étape {id_etape} retirée de {nom_parcours}.")
    return 0


def _parcours_isoles(racine: Path) -> list[str]:
    """Noms des dossiers de contenu/ dont le parcours.json est en mode isole."""
    noms = []
    for dossier in sorted(p for p in racine.iterdir() if p.is_dir()):
        fichier = dossier / "parcours.json"
        if not fichier.exists():
            continue
        try:
            donnees = _lire_json(fichier)
        except json.JSONDecodeError:
            continue
        if donnees.get("mode", "isole") == "isole":
            noms.append(dossier.name)
    return noms


def _verifier_porte(dossier_etape: Path, fichiers_requis: tuple, porte) -> tuple[bool, str]:
    manquants = [f for f in fichiers_requis if not (dossier_etape / f).exists()]
    if manquants:
        return False, "fichier manquant : " + ", ".join(manquants)
    etape = charger_etape(dossier_etape)
    corrige = (dossier_etape / "corrige.c").read_text(encoding="utf-8")
    starter = (dossier_etape / "starter.c").read_text(encoding="utf-8")
    r_corrige = porte(etape, corrige)
    if not r_corrige.ok:
        return False, "le corrigé ne passe pas la porte :\n" + r_corrige.sortie
    r_starter = porte(etape, starter)
    if r_starter.ok:
        return False, "le starter passe la porte alors qu'il ne devrait pas"
    return True, "ok"


def _verifier_etape(dossier_parcours: Path, id_etape: str) -> tuple[bool, str]:
    dossier_etape = dossier_parcours / id_etape
    if not dossier_etape.is_dir():
        return False, "dossier introuvable"
    fichier_meta = dossier_etape / "meta.json"
    if not fichier_meta.exists():
        return False, "meta.json introuvable"
    try:
        meta = _lire_json(fichier_meta)
    except json.JSONDecodeError as e:
        return False, f"meta.json invalide : {e}"
    try:
        id_meta = meta["id"]
        meta["titre"]
        meta["type"]
        meta["fichier_edite"]
    except KeyError as e:
        return False, f"meta.json incomplet, clé manquante : {e}"
    if id_meta != id_etape:
        return False, f"id du meta ({id_meta}) différent du nom de dossier ({id_etape})"

    mode = meta.get("mode", "")
    if mode == "programme":
        return _verifier_porte(dossier_etape, ("corrige.c", "starter.c"), executeur.porte_programme)
    if mode == "test_fourni":
        return _verifier_porte(dossier_etape, ("corrige.c", "starter.c", "tests.c"),
                               executeur.porte_perso)
    return True, f"non vérifié automatiquement (mode {mode or 'aucun'})"


def commande_verifier(nom_parcours: str = None, racine: Path = RACINE_CONTENU) -> int:
    """Vérifie un parcours donné, ou tous les parcours isole si aucun n'est précisé.
    Compile du C pour chaque étape programme ou test_fourni : c'est lent, la
    progression s'affiche donc au fur et à mesure."""
    if nom_parcours is not None:
        if not (racine / nom_parcours).exists():
            _erreur(f"parcours introuvable : {nom_parcours}")
            return 1
        noms = [nom_parcours]
    else:
        noms = _parcours_isoles(racine)

    tout_ok = True
    for nom in noms:
        dossier_parcours = racine / nom
        donnees = _lire_json(dossier_parcours / "parcours.json")
        for id_etape in donnees.get("ordre", []):
            print(f"{nom}/{id_etape} ... ", end="", flush=True)
            ok, message = _verifier_etape(dossier_parcours, id_etape)
            print(message)
            tout_ok = tout_ok and ok
    return 0 if tout_ok else 1


def main(argv=None) -> int:
    analyseur = argparse.ArgumentParser(
        description="Édite le contenu pédagogique : parcours et étapes.")
    sous = analyseur.add_subparsers(dest="commande", required=True)

    p_nouveau_parcours = sous.add_parser("nouveau-parcours", help="Crée un parcours vide.")
    p_nouveau_parcours.add_argument("nom")

    p_nouvelle_etape = sous.add_parser("nouvelle-etape", help="Crée une étape squelette.")
    p_nouvelle_etape.add_argument("parcours")
    p_nouvelle_etape.add_argument("id")
    p_nouvelle_etape.add_argument("--titre", required=True)
    p_nouvelle_etape.add_argument("--apres", default=None)
    p_nouvelle_etape.add_argument("--cran", type=int, default=1)

    p_retirer_etape = sous.add_parser("retirer-etape", help="Retire une étape d'un parcours.")
    p_retirer_etape.add_argument("parcours")
    p_retirer_etape.add_argument("id")
    p_retirer_etape.add_argument("--effacer", action="store_true")

    p_verifier = sous.add_parser(
        "verifier", help="Vérifie qu'un parcours, ou tous les parcours isole, fonctionnent.")
    p_verifier.add_argument("parcours", nargs="?", default=None)

    args = analyseur.parse_args(argv)
    if args.commande == "nouveau-parcours":
        return commande_nouveau_parcours(args.nom)
    if args.commande == "nouvelle-etape":
        return commande_nouvelle_etape(args.parcours, args.id, args.titre,
                                       args.apres, args.cran)
    if args.commande == "retirer-etape":
        return commande_retirer_etape(args.parcours, args.id, args.effacer)
    if args.commande == "verifier":
        return commande_verifier(args.parcours)
    return 1


if __name__ == "__main__":
    sys.exit(main())
