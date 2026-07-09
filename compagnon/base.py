"""Base SQLite du compagnon : appairages, événements, config LTI. Aucune UI, aucune route.
Spec sections 6.2, 4, 5. Le journal des événements n'est jamais écrasé, le score se
recalcule toujours depuis lui."""
import json
import secrets
import sqlite3
import time

# alphabet sans caractères ambigus, ni O ni 0 ni I ni L ni 1
ALPHABET_CODE = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
DUREE_CODE = 600  # dix minutes, spec section 4

SCHEMA = """
CREATE TABLE IF NOT EXISTS config_lti (
    iss TEXT NOT NULL, client_id TEXT NOT NULL, deployment_id TEXT NOT NULL,
    auth_login_url TEXT NOT NULL, auth_token_url TEXT NOT NULL, key_set_url TEXT NOT NULL,
    PRIMARY KEY (iss, client_id));
CREATE TABLE IF NOT EXISTS appairages (
    sub TEXT PRIMARY KEY, nom TEXT NOT NULL, contexte TEXT NOT NULL,
    jeton TEXT UNIQUE, code TEXT, code_expire REAL,
    ags_claim TEXT NOT NULL, score_a_pousser REAL, cree REAL NOT NULL);
CREATE TABLE IF NOT EXISTS evenements (
    id INTEGER PRIMARY KEY AUTOINCREMENT, sub TEXT NOT NULL, etape TEXT NOT NULL,
    reussite INTEGER NOT NULL, horodatage TEXT NOT NULL, recu REAL NOT NULL);
"""


def ouvrir(chemin) -> sqlite3.Connection:
    cx = sqlite3.connect(chemin, check_same_thread=False)
    cx.row_factory = sqlite3.Row
    cx.executescript(SCHEMA)
    return cx


def enregistrer_lancement(cx, sub: str, nom: str, contexte: str, ags_claim: dict,
                          duree: float = DUREE_CODE) -> str:
    """Un lancement LTI remplace l'appairage existant du même étudiant et rend
    un nouveau code court à usage unique."""
    code = "".join(secrets.choice(ALPHABET_CODE) for _ in range(6))
    cx.execute("INSERT INTO appairages (sub, nom, contexte, code, code_expire, ags_claim, cree)"
               " VALUES (?, ?, ?, ?, ?, ?, ?)"
               " ON CONFLICT(sub) DO UPDATE SET nom=excluded.nom, contexte=excluded.contexte,"
               " jeton=NULL, code=excluded.code, code_expire=excluded.code_expire,"
               " ags_claim=excluded.ags_claim",
               (sub, nom, contexte, code, time.time() + duree, json.dumps(ags_claim), time.time()))
    cx.commit()
    return code


def _normaliser(code: str) -> str:
    return "".join(c for c in code.upper() if c in ALPHABET_CODE)


def echanger_code(cx, code: str):
    """Rend le jeton permanent, ou None si le code est inconnu, expiré ou déjà servi."""
    ligne = cx.execute("SELECT sub, code_expire FROM appairages WHERE code = ?",
                       (_normaliser(code),)).fetchone()
    if ligne is None or ligne["code_expire"] < time.time():
        return None
    jeton = secrets.token_urlsafe(32)
    cx.execute("UPDATE appairages SET jeton = ?, code = NULL, code_expire = NULL WHERE sub = ?",
               (jeton, ligne["sub"]))
    cx.commit()
    return jeton


def sub_du_jeton(cx, jeton: str):
    ligne = cx.execute("SELECT sub FROM appairages WHERE jeton = ?", (jeton,)).fetchone()
    return ligne["sub"] if ligne else None


def ajouter_evenements(cx, sub: str, evenements: list) -> int:
    for e in evenements:
        cx.execute("INSERT INTO evenements (sub, etape, reussite, horodatage, recu)"
                   " VALUES (?, ?, ?, ?, ?)",
                   (sub, e["etape"], 1 if e["reussite"] else 0, e["horodatage"], time.time()))
    cx.commit()
    return len(evenements)


def etapes_validees(cx, sub: str) -> set:
    lignes = cx.execute("SELECT DISTINCT etape FROM evenements WHERE sub = ? AND reussite = 1",
                        (sub,)).fetchall()
    return {l["etape"] for l in lignes}


def score(nb_validees: int, total: int) -> float:
    return min(100.0, round(100.0 * nb_validees / total, 1))


def marquer_a_pousser(cx, sub: str, valeur: float) -> None:
    cx.execute("UPDATE appairages SET score_a_pousser = ? WHERE sub = ?", (valeur, sub))
    cx.commit()


def notes_en_attente(cx) -> list:
    lignes = cx.execute("SELECT sub, score_a_pousser, ags_claim FROM appairages"
                        " WHERE score_a_pousser IS NOT NULL").fetchall()
    return [(l["sub"], l["score_a_pousser"], json.loads(l["ags_claim"])) for l in lignes]


def marquer_poussee(cx, sub: str) -> None:
    cx.execute("UPDATE appairages SET score_a_pousser = NULL WHERE sub = ?", (sub,))
    cx.commit()
