"""Pont optionnel vers le compagnon Moodle. Aucune UI, bibliothèque standard seulement.
Sans appairage, tout est inerte. Chaque porte passée est d'abord écrite dans la file
locale, puis envoyée ; un envoi raté attend le prochain rejeu. Spec compagnon LTI."""
import json
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import chemins

DELAI = 8  # secondes ; le réveil du serveur gratuit se fait absorber par la file


def _charger(fichier: Path) -> dict:
    if not Path(fichier).exists():
        return {"url": "", "jeton": "", "file": []}
    return json.loads(Path(fichier).read_text(encoding="utf-8"))


def _sauver(d: dict, fichier: Path) -> None:
    Path(fichier).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def actif(fichier: Path = chemins.MOODLE_SYNC_FICHIER) -> bool:
    return bool(_charger(fichier).get("jeton"))


def _poster(url: str, corps: dict, entetes: dict) -> dict:
    requete = urllib.request.Request(url, data=json.dumps(corps).encode(),
                                     headers={"Content-Type": "application/json", **entetes})
    with urllib.request.urlopen(requete, timeout=DELAI) as r:
        return json.loads(r.read().decode())


def appairer(code: str, fichier: Path = chemins.MOODLE_SYNC_FICHIER,
             url: str = None) -> tuple[bool, str]:
    """Échange le code court contre le jeton permanent et le range dans le fichier."""
    url = (url or chemins.COMPAGNON_URL).rstrip("/")
    try:
        reponse = _poster(url + "/api/appairage", {"code": code}, {})
    except urllib.error.HTTPError:
        return False, "Code refusé : expiré ou déjà utilisé. Reclique l'activité dans Moodle."
    except OSError:
        return False, "Serveur injoignable. Réessaie dans une minute."
    d = _charger(fichier)
    d.update(url=url, jeton=reponse["jeton"])
    _sauver(d, fichier)
    return True, "Connecté à Moodle. Ta progression remontera automatiquement."


def signaler_porte(id_etape: str, fichier: Path = chemins.MOODLE_SYNC_FICHIER,
                   attendre: bool = False) -> None:
    """Ajoute l'événement à la file puis tente l'envoi en arrière-plan.
    Sans appairage, ne fait rien. Ne lève jamais, ne bloque jamais l'UI.
    attendre=True rend l'envoi synchrone, pour les tests."""
    d = _charger(fichier)
    if not d.get("jeton"):
        return
    d["file"].append({"etape": id_etape, "reussite": True,
                      "horodatage": datetime.now(timezone.utc).isoformat()})
    _sauver(d, fichier)
    rejouer(fichier=fichier, attendre=attendre)


def rejouer(fichier: Path = chemins.MOODLE_SYNC_FICHIER, attendre: bool = False) -> None:
    """Vide la file locale vers le compagnon dans un fil discret.
    attendre=True rend l'envoi synchrone, pour les tests et la fin de session."""
    def envoi():
        d = _charger(fichier)
        if not d.get("jeton") or not d["file"]:
            return
        try:
            _poster(d["url"] + "/api/evenements", {"evenements": d["file"]},
                    {"Authorization": "Bearer " + d["jeton"]})
        except OSError:
            return  # la file reste, on rejouera
        d = _charger(fichier)
        d["file"] = []
        _sauver(d, fichier)

    if attendre:
        envoi()
    else:
        threading.Thread(target=envoi, daemon=True).start()
