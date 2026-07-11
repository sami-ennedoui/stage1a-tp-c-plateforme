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

# Protège le fichier JSON partagé entre le fil UI (signaler_porte) et les fils
# d'envoi (rejouer) : lecture-modification-écriture toujours sous ce verrou.
_VERROU = threading.Lock()

# Un seul envoi en vol à la fois ; seuls les fils d'envoi s'y disputent, jamais l'UI.
_VERROU_ENVOI = threading.Lock()

# Dernier score renvoyé par le compagnon (pourcentage sur 100), ou None si aucun
# envoi n'a encore été acquitté. L'UI le lit pour afficher la progression Moodle.
dernier_score = None


def _charger(fichier: Path) -> dict:
    if not Path(fichier).exists():
        return {"url": "", "jeton": "", "file": []}
    try:
        return json.loads(Path(fichier).read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # Fichier corrompu (ex. lecture en plein milieu d'une écriture) : on repart propre.
        return {"url": "", "jeton": "", "file": []}


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
    with _VERROU:
        d = _charger(fichier)
        if not d.get("jeton"):
            return
        d["file"].append({"etape": id_etape, "reussite": True,
                          "horodatage": datetime.now(timezone.utc).isoformat()})
        _sauver(d, fichier)
    rejouer(fichier=fichier, attendre=attendre)


def signaler_deja_faits(ids, fichier: Path = chemins.MOODLE_SYNC_FICHIER,
                        attendre: bool = False) -> None:
    """Met en file toutes les étapes déjà validées, puis envoie. À appeler juste
    après l'appairage : sinon la progression faite avant la connexion est perdue,
    car signaler_porte jette les événements tant qu'il n'y a pas de jeton."""
    with _VERROU:
        d = _charger(fichier)
        if not d.get("jeton"):
            return
        horodatage = datetime.now(timezone.utc).isoformat()
        deja_en_file = {e["etape"] for e in d["file"]}
        for id_etape in ids:
            if id_etape not in deja_en_file:
                d["file"].append({"etape": id_etape, "reussite": True,
                                  "horodatage": horodatage})
        _sauver(d, fichier)
    rejouer(fichier=fichier, attendre=attendre)


def rejouer(fichier: Path = chemins.MOODLE_SYNC_FICHIER, attendre: bool = False) -> None:
    """Vide la file locale vers le compagnon dans un fil discret.
    attendre=True rend l'envoi synchrone, pour les tests et la fin de session."""
    def envoi():
        with _VERROU_ENVOI:
            with _VERROU:
                d = _charger(fichier)
                if not d.get("jeton") or not d["file"]:
                    return
                url, jeton, envoyes = d["url"], d["jeton"], list(d["file"])
            # Pas de verrou pendant la requête réseau (jusqu'à DELAI secondes) : un
            # signaler_porte concurrent doit pouvoir ajouter un événement pendant ce temps.
            try:
                reponse = _poster(url + "/api/evenements", {"evenements": envoyes},
                                  {"Authorization": "Bearer " + jeton})
            except OSError:
                return  # la file reste, on rejouera
            if isinstance(reponse, dict) and "score" in reponse:
                global dernier_score
                dernier_score = reponse["score"]
            with _VERROU:
                d = _charger(fichier)
                # Les ajouts se font toujours en fin de liste (signaler_porte), et un
                # seul envoi est en vol : la tranche envoyée est donc un préfixe de la
                # file au moment de la mise à jour. On ne retire que ce préfixe, pas les
                # événements arrivés pendant l'envoi.
                d["file"] = d["file"][len(envoyes):]
                _sauver(d, fichier)

    if attendre:
        envoi()
    else:
        threading.Thread(target=envoi, daemon=True).start()
