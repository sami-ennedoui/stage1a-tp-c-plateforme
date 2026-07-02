"""Journal de session de l'atelier : trace des evenements pour l'analyse pedagogique.

Ecrit un fichier JSONL, une ligne JSON par evenement, dans le dossier journaux/ a
cote de l'application. Aucune dependance Qt : l'appli cree un Journal au demarrage
et appelle .event(...) aux points d'accroche (ouverture d'exo, compilation, test de
porte, demande au tuteur, reponse du tuteur, inactivite, generation en mode demo).

Un identifiant de session aleatoire, pas de nom : c'est une demo, on veut des
donnees anonymes. Chaque ligne :
    {"t": <iso8601>, "session": <id>, "evt": <type>, ...champs}

L'ecriture est volontairement en append ligne par ligne (ouvre/ecrit/ferme) : si
l'appli est tuee, tout ce qui precede est deja sur le disque, rien a vider.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _maintenant() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Journal:
    """Journal d'une session. Instancier une fois au lancement de la fenetre.

    dossier : ou ecrire (defaut : journaux/ a cote de ce fichier).
    session : identifiant impose (defaut : aleatoire, 12 hexa).
    meta    : champs joints a l'evenement session_debut (parcours, mode, moteur...).
    """

    def __init__(self, dossier: Path | None = None, session: str | None = None,
                 meta: dict | None = None):
        base = dossier if dossier is not None else Path(__file__).resolve().parent / "journaux"
        base.mkdir(parents=True, exist_ok=True)
        self.session = session or uuid.uuid4().hex[:12]
        horodate = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        self.fichier = base / f"session-{horodate}-{self.session}.jsonl"
        self.event("session_debut", **(meta or {}))

    def event(self, evt: str, **champs) -> None:
        """Ajoute un evenement. `evt` est le type (voir la liste dans REPARTITION) ;
        les champs libres qualifient l'evenement (exo, ok, cran, longueur...)."""
        ligne = {"t": _maintenant(), "session": self.session, "evt": evt}
        ligne.update(champs)
        with self.fichier.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ligne, ensure_ascii=False) + "\n")

    def fin(self) -> None:
        self.event("session_fin")


class JournalMuet:
    """Journal factice : memes methodes, n'ecrit rien. Sert quand on ne veut pas de
    trace (tests, mode demo) sans avoir a semer des `if journal:` partout."""

    session = ""
    fichier = None

    def event(self, evt: str, **champs) -> None:  # noqa: D401 - meme signature
        pass

    def fin(self) -> None:
        pass
