"""Porte d'accès au mode auteur. Un mot de passe protège l'édition du contenu.

Le mot de passe n'est jamais stocké en clair. On garde son empreinte SHA-256 dans
`auteur.json` (git-ignoré, local à chaque poste). Ordre de résolution de l'empreinte
attendue :
  1. `auteur.json` s'il existe (empreinte définie depuis l'appli) ;
  2. sinon la variable d'environnement `ATELIER_AUTEUR_MDP` (mot de passe en clair,
     haché à la volée), pratique pour un poste enseignant ;
  3. sinon le mot de passe par défaut ci-dessous, documenté dans DOC-gestion-niveaux.md.

Aucune dépendance PyQt ici : la logique est testable sans écran.
"""
import hashlib
import json
import os

import chemins

# Défaut volontairement simple : ce n'est pas un secret de sécurité, juste un garde
# qui empêche un étudiant de modifier le contenu par curiosité. À changer depuis le menu.
MDP_DEFAUT = "auteur"


def _hacher(mot_de_passe: str) -> str:
    return hashlib.sha256(mot_de_passe.encode("utf-8")).hexdigest()


def _hash_attendu() -> str:
    if chemins.AUTEUR_FICHIER.exists():
        donnees = json.loads(chemins.AUTEUR_FICHIER.read_text(encoding="utf-8"))
        empreinte = donnees.get("hash_mdp")
        if empreinte:
            return empreinte
    en_env = os.environ.get("ATELIER_AUTEUR_MDP")
    if en_env:
        return _hacher(en_env)
    return _hacher(MDP_DEFAUT)


def verifier(saisi: str) -> bool:
    """Vrai si le mot de passe saisi correspond à l'empreinte attendue."""
    return _hacher(saisi) == _hash_attendu()


def definir(nouveau: str) -> None:
    """Enregistre l'empreinte d'un nouveau mot de passe dans auteur.json."""
    if not nouveau:
        raise ValueError("Le mot de passe ne peut pas être vide.")
    chemins.AUTEUR_FICHIER.write_text(
        json.dumps({"hash_mdp": _hacher(nouveau)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
