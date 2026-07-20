# Compagnon LTI Moodle — Plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Un service web qui reçoit les lancements LTI 1.3 de Moodle, appaire l'app bureau par un code court, et pousse la progression dans le carnet de notes, plus le module `moodle_sync.py` côté app.

**Architecture:** Trois acteurs, spec `SPEC-compagnon-lti-moodle.md`. Le compagnon vit dans `compagnon/`, service Flask autonome avec sa base SQLite, déployé sur Render. L'app bureau gagne un seul module `moodle_sync.py` en bibliothèque standard, avec une file locale rejouée, branché sur `fenetre.py`.

**Tech Stack:** Python, Flask, pylti1p3, flask-caching, gunicorn, SQLite. Côté app : urllib et unittest seulement.

## Global Constraints

- Suivre la spec `SPEC-compagnon-lti-moodle.md`, sections numérotées citées dans les tâches.
- Code, commentaires, docstrings et messages de commit en français, style des modules existants : docstring d'en-tête, « Aucune UI » pour les modules de logique.
- Côté app bureau : aucune dépendance nouvelle, bibliothèque standard seulement.
- Côté compagnon : dépendances dans `compagnon/requirements.txt` seulement, jamais dans l'environnement de l'app.
- Tests en unittest comme la suite existante, lancés avec `python3 -m pytest tests/ -v` depuis la racine, et `python3 -m pytest compagnon/tests/ -v` pour le compagnon.
- Commits fréquents sur la branche `version-projet`, un par tâche au moins, sans ligne Co-Authored-By.
- Le suivi Moodle ne doit jamais bloquer l'app : sans appairage, tout est inerte ; réseau en panne, file locale.
- Les clés RSA et identifiants LTI ne vont jamais dans le dépôt, uniquement en variables d'environnement.

---

## Vue des fichiers

| Fichier | Rôle |
|---|---|
| `compagnon/base.py` | SQLite : appairages, événements, config LTI, codes courts, score. Aucune logique web. |
| `compagnon/lti.py` | Pont pylti1p3 : config de l'outil, JWKS, poussée AGS d'un score. Aucune route. |
| `compagnon/app.py` | Routes Flask : pages LTI, API de l'app, page d'aide, rejeu périodique. |
| `compagnon/cles.py` | Script : génère la paire RSA à mettre en variables d'environnement. |
| `compagnon/pousse_test.py` | Script : pousse une note en dur, validation manuelle du canal AGS. |
| `compagnon/requirements.txt`, `compagnon/Dockerfile`, `compagnon/README.md` | Déploiement. |
| `compagnon/tests/test_base.py`, `compagnon/tests/test_app.py` | Tests du compagnon. |
| `moodle_sync.py` | Côté app : appairage, file locale, envoi. Aucune UI. |
| `tests/test_moodle_sync.py` | Tests côté app. |
| `chemins.py` | Ajout de `MOODLE_SYNC_FICHIER` et `COMPAGNON_URL`. |
| `fenetre.py` | Bouton « Connecter à Moodle » et appel `signaler_porte`. |

---

### Task 1: Base SQLite du compagnon

**Files:**
- Create: `compagnon/__init__.py` (vide), `compagnon/base.py`
- Test: `compagnon/tests/__init__.py` (vide), `compagnon/tests/test_base.py`

**Interfaces:**
- Consumes: rien.
- Produces: `ouvrir(chemin: Path) -> sqlite3.Connection`, `enregistrer_lancement(cx, sub: str, nom: str, contexte: str, ags_claim: dict) -> str` (rend le code court), `echanger_code(cx, code: str) -> str | None` (rend le jeton, None si inconnu ou expiré), `sub_du_jeton(cx, jeton: str) -> str | None`, `ajouter_evenements(cx, sub: str, evenements: list[dict]) -> int`, `etapes_validees(cx, sub: str) -> set[str]`, `score(nb_validees: int, total: int) -> float`, `marquer_a_pousser(cx, sub: str, score: float) -> None`, `notes_en_attente(cx) -> list[tuple[str, float, dict]]` (sub, score, ags_claim), `marquer_poussee(cx, sub: str) -> None`.

- [ ] **Step 1: Écrire les tests qui échouent**

```python
# compagnon/tests/test_base.py
"""Tests de la base du compagnon : appairage, événements, score."""
import sqlite3
import time
import unittest

from compagnon import base

AGS = {"lineitem": "https://moodle.example/ligne/42", "scope": []}


def cx_memoire():
    cx = base.ouvrir(":memory:")
    return cx


class TestAppairage(unittest.TestCase):
    def test_lancement_rend_un_code_lisible(self):
        cx = cx_memoire()
        code = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS)
        self.assertEqual(len(code), 6)
        for c in code:
            self.assertIn(c, base.ALPHABET_CODE)

    def test_echange_du_code_rend_un_jeton_une_seule_fois(self):
        cx = cx_memoire()
        code = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS)
        jeton = base.echanger_code(cx, code)
        self.assertIsNotNone(jeton)
        self.assertEqual(base.sub_du_jeton(cx, jeton), "u12")
        self.assertIsNone(base.echanger_code(cx, code))  # usage unique

    def test_echange_tolere_tirets_espaces_et_casse(self):
        cx = cx_memoire()
        code = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS)
        brouillon = f" {code[:3].lower()}-{code[3:]} "
        self.assertIsNotNone(base.echanger_code(cx, brouillon))

    def test_code_expire_refuse(self):
        cx = cx_memoire()
        code = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS,
                                          duree=-1)
        self.assertIsNone(base.echanger_code(cx, code))

    def test_nouveau_lancement_remplace_l_ancien_appairage(self):
        cx = cx_memoire()
        code1 = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS)
        jeton1 = base.echanger_code(cx, code1)
        code2 = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS)
        jeton2 = base.echanger_code(cx, code2)
        self.assertIsNone(base.sub_du_jeton(cx, jeton1))
        self.assertEqual(base.sub_du_jeton(cx, jeton2), "u12")

    def test_jeton_inconnu_rend_none(self):
        cx = cx_memoire()
        self.assertIsNone(base.sub_du_jeton(cx, "n_existe_pas"))


class TestEvenementsEtScore(unittest.TestCase):
    def test_evenements_journalises_et_etapes_distinctes(self):
        cx = cx_memoire()
        n = base.ajouter_evenements(cx, "u12", [
            {"etape": "perso_P1", "reussite": True, "horodatage": "2026-07-07T10:00:00"},
            {"etape": "perso_P1", "reussite": True, "horodatage": "2026-07-07T11:00:00"},
            {"etape": "jalon1_parametrage", "reussite": True, "horodatage": "2026-07-07T12:00:00"},
            {"etape": "jalon2", "reussite": False, "horodatage": "2026-07-07T13:00:00"},
        ])
        self.assertEqual(n, 4)
        self.assertEqual(base.etapes_validees(cx, "u12"),
                         {"perso_P1", "jalon1_parametrage"})

    def test_score_en_pourcentage(self):
        self.assertEqual(base.score(3, 6), 50.0)
        self.assertEqual(base.score(0, 6), 0.0)
        self.assertEqual(base.score(7, 6), 100.0)  # jamais au dessus de 100

    def test_file_des_notes_a_pousser(self):
        cx = cx_memoire()
        code = base.enregistrer_lancement(cx, "u12", "Sami", "c4665", AGS)
        base.echanger_code(cx, code)
        base.marquer_a_pousser(cx, "u12", 50.0)
        base.marquer_a_pousser(cx, "u12", 66.7)  # remplace, ne s'empile pas
        attente = base.notes_en_attente(cx)
        self.assertEqual(len(attente), 1)
        sub, sc, ags = attente[0]
        self.assertEqual((sub, sc), ("u12", 66.7))
        self.assertEqual(ags["lineitem"], AGS["lineitem"])
        base.marquer_poussee(cx, "u12")
        self.assertEqual(base.notes_en_attente(cx), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Vérifier qu'ils échouent**

Run: `cd /home/samiennedoui/scratch-stage1a/snake-sdl/plateforme && python3 -m pytest compagnon/tests/test_base.py -v`
Expected: erreurs `ModuleNotFoundError` ou `AttributeError`, aucune réussite.

- [ ] **Step 3: Implémenter `compagnon/base.py`**

```python
# compagnon/base.py
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
```

- [ ] **Step 4: Vérifier que les tests passent**

Run: `python3 -m pytest compagnon/tests/test_base.py -v`
Expected: 10 PASS.

- [ ] **Step 5: Commit**

```bash
git add compagnon/__init__.py compagnon/base.py compagnon/tests/
git commit -m "Compagnon : base SQLite, appairage par code court et journal des événements"
```

---

### Task 2: Squelette LTI, config, JWKS, lancement

**Files:**
- Create: `compagnon/lti.py`, `compagnon/cles.py`, `compagnon/app.py`, `compagnon/requirements.txt`
- Test: `compagnon/tests/test_app.py`

**Interfaces:**
- Consumes: `base.ouvrir`, `base.enregistrer_lancement` (Task 1).
- Produces: `lti.conf_outil() -> ToolConfDict`, `lti.jwks() -> dict`, `app.creer_app(chemin_base) -> Flask`, `app.traiter_lancement(cx, donnees: dict) -> tuple[str, str]` (nom affiché, code). Variables d'environnement lues : `MOODLE_ISS`, `MOODLE_CLIENT_ID`, `MOODLE_DEPLOYMENT_ID`, `MOODLE_AUTH_LOGIN_URL`, `MOODLE_AUTH_TOKEN_URL`, `MOODLE_KEY_SET_URL`, `TOOL_PRIVATE_KEY`, `TOOL_PUBLIC_KEY`, `TOTAL_ETAPES`, `COMPAGNON_BASE` (chemin SQLite, défaut `compagnon.sqlite3`).

Le lancement LTI lui-même, signatures et jetons OIDC, est du ressort de pylti1p3 et ne se teste unitairement pas sans Moodle. On isole donc une couture : la route `/lti/launch` appelle `traiter_lancement(cx, donnees)` avec les claims déjà validés, et c'est cette fonction qu'on teste. Le protocole réel se valide en Task 3 dans le bac à sable, spec section 13.

- [ ] **Step 1: `compagnon/requirements.txt`**

```
Flask>=3.0
flask-caching>=2.0
PyLTI1p3>=2.0.0
gunicorn>=21.0
```

Run: `python3 -m venv compagnon/.venv && compagnon/.venv/bin/pip install -r compagnon/requirements.txt`
Expected: installation sans erreur. Ajouter `compagnon/.venv/`, `compagnon/*.sqlite3` et `moodle_sync.json` au `.gitignore`.

- [ ] **Step 2: Écrire les tests qui échouent**

```python
# compagnon/tests/test_app.py
"""Tests des routes testables du compagnon : page d'aide, JWKS, couture de lancement,
API d'appairage et d'événements (Task 5 complètera)."""
import os
import unittest

CLES_TEST = None  # paire RSA générée une fois pour toute la classe


def _env_test():
    from compagnon import cles
    global CLES_TEST
    if CLES_TEST is None:
        CLES_TEST = cles.generer_paire()
    privee, publique = CLES_TEST
    os.environ.update({
        "MOODLE_ISS": "https://moodle.example",
        "MOODLE_CLIENT_ID": "client_test",
        "MOODLE_DEPLOYMENT_ID": "1",
        "MOODLE_AUTH_LOGIN_URL": "https://moodle.example/mod/lti/auth.php",
        "MOODLE_AUTH_TOKEN_URL": "https://moodle.example/mod/lti/token.php",
        "MOODLE_KEY_SET_URL": "https://moodle.example/mod/lti/certs.php",
        "TOOL_PRIVATE_KEY": privee,
        "TOOL_PUBLIC_KEY": publique,
        "TOTAL_ETAPES": "6",
    })


class TestApp(unittest.TestCase):
    def setUp(self):
        _env_test()
        from compagnon import app as module_app
        self.app = module_app.creer_app(":memory:")
        self.client = self.app.test_client()

    def test_page_d_aide_a_la_racine(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("lti/login", r.get_data(as_text=True))

    def test_jwks_expose_une_cle(self):
        r = self.client.get("/.well-known/jwks.json")
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.get_json()["keys"]), 1)

    def test_traiter_lancement_cree_l_appairage_et_rend_le_code(self):
        from compagnon import app as module_app, base
        donnees = {
            "sub": "u12",
            "name": "Sami Ennedoui",
            "https://purl.imsglobal.org/spec/lti/claim/context": {"id": "c4665"},
            "https://purl.imsglobal.org/spec/lti-ags/claim/endpoint": {
                "lineitem": "https://moodle.example/ligne/1", "scope": []},
        }
        nom, code = module_app.traiter_lancement(self.app.cx, donnees)
        self.assertEqual(nom, "Sami Ennedoui")
        self.assertIsNotNone(base.echanger_code(self.app.cx, code))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Vérifier qu'ils échouent**

Run: `compagnon/.venv/bin/python -m pytest compagnon/tests/test_app.py -v`
Expected: échec à l'import de `compagnon.app` ou `compagnon.cles`.

- [ ] **Step 4: Implémenter `compagnon/cles.py`**

```python
# compagnon/cles.py
"""Génère la paire RSA de l'outil LTI, à mettre en variables d'environnement.
Usage : python -m compagnon.cles"""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generer_paire() -> tuple[str, str]:
    cle = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    privee = cle.private_bytes(serialization.Encoding.PEM,
                               serialization.PrivateFormat.TraditionalOpenSSL,
                               serialization.NoEncryption()).decode()
    publique = cle.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    return privee, publique


if __name__ == "__main__":
    privee, publique = generer_paire()
    print("TOOL_PRIVATE_KEY :\n" + privee)
    print("TOOL_PUBLIC_KEY :\n" + publique)
```

`cryptography` arrive avec PyLTI1p3, pas besoin de l'ajouter aux requirements.

- [ ] **Step 5: Implémenter `compagnon/lti.py`**

```python
# compagnon/lti.py
"""Pont vers pylti1p3 : configuration de l'outil, JWKS, poussée AGS. Aucune route ici.
Toute la configuration vient des variables d'environnement, spec section 11."""
import os
from datetime import datetime, timezone

from pylti1p3.tool_config import ToolConfDict


def conf_outil() -> ToolConfDict:
    iss = os.environ["MOODLE_ISS"]
    client_id = os.environ["MOODLE_CLIENT_ID"]
    conf = ToolConfDict({iss: [{
        "default": True,
        "client_id": client_id,
        "auth_login_url": os.environ["MOODLE_AUTH_LOGIN_URL"],
        "auth_token_url": os.environ["MOODLE_AUTH_TOKEN_URL"],
        "key_set_url": os.environ["MOODLE_KEY_SET_URL"],
        "deployment_ids": [os.environ["MOODLE_DEPLOYMENT_ID"]],
    }]})
    conf.set_private_key(iss, os.environ["TOOL_PRIVATE_KEY"], client_id=client_id)
    conf.set_public_key(iss, os.environ["TOOL_PUBLIC_KEY"], client_id=client_id)
    return conf


def jwks() -> dict:
    return conf_outil().get_jwks()


def pousser_score(sub: str, valeur: float, ags_claim: dict) -> None:
    """Écrit un score au carnet par AGS, hors de tout lancement, spec section 5.
    Lève une exception réseau ou pylti1p3 si Moodle ne répond pas, l'appelant décide."""
    from pylti1p3.assignments_grades import AssignmentsGradesService
    from pylti1p3.grade import Grade
    from pylti1p3.service_connector import ServiceConnector

    conf = conf_outil()
    registration = conf.find_registration_by_issuer(os.environ["MOODLE_ISS"])
    service = AssignmentsGradesService(ServiceConnector(registration), ags_claim)
    note = (Grade()
            .set_score_given(valeur)
            .set_score_maximum(100)
            .set_activity_progress("Completed")
            .set_grading_progress("FullyGraded")
            .set_timestamp(datetime.now(timezone.utc).isoformat())
            .set_user_id(sub))
    service.put_grade(note)
```

Si une signature pylti1p3 diffère à l'exécution, la référence est l'exemple officiel
`https://github.com/dmitry-viskov/pylti1.3-flask-example`, l'adapter sans changer
les interfaces produites.

- [ ] **Step 6: Implémenter `compagnon/app.py`**

```python
# compagnon/app.py
"""Routes du compagnon : lancement LTI, appairage, événements, page d'aide.
Spec section 6.1. La logique vit dans base.py et lti.py, ici on câble."""
import os

from flask import Flask, jsonify, request
from flask_caching import Cache
from pylti1p3.contrib.flask import (FlaskCacheDataStorage, FlaskMessageLaunch,
                                    FlaskOIDCLogin, FlaskRequest)

from compagnon import base, lti

PAGE_CODE = """<!doctype html><meta charset="utf-8"><title>TP C</title>
<body style="font-family:sans-serif;max-width:36em;margin:4em auto">
<h1>Bonjour {nom}</h1>
<p>Ton code de connexion, à coller dans l'atelier, bouton
« Connecter à Moodle » :</p>
<p style="font-size:2.5em;letter-spacing:.2em;font-weight:bold">{code}</p>
<p>Il est valable dix minutes et ne sert qu'une fois. Pour en obtenir un
autre, reviens simplement ici depuis le cours.</p></body>"""

PAGE_AIDE = """<!doctype html><meta charset="utf-8"><title>Compagnon TP C</title>
<body style="font-family:sans-serif;max-width:36em;margin:4em auto">
<h1>Compagnon Moodle du TP C</h1>
<p>Service d'appairage et de remontée de progression. Valeurs pour
« Ajouter outil » dans Moodle :</p>
<ul>
<li>URL de l'outil : <code>{racine}lti/launch</code></li>
<li>URL d'initiation de connexion : <code>{racine}lti/login</code></li>
<li>URI de redirection : <code>{racine}lti/launch</code></li>
<li>URL du jeu de clés publiques : <code>{racine}.well-known/jwks.json</code></li>
</ul>
<p>Services à activer : notes AGS avec envoi au carnet, partage du nom.</p></body>"""


def traiter_lancement(cx, donnees: dict) -> tuple[str, str]:
    """Couture testable : claims LTI déjà validés vers appairage et code court."""
    sub = donnees["sub"]
    nom = donnees.get("name", sub)
    contexte = donnees["https://purl.imsglobal.org/spec/lti/claim/context"]["id"]
    ags = donnees.get("https://purl.imsglobal.org/spec/lti-ags/claim/endpoint", {})
    code = base.enregistrer_lancement(cx, sub, nom, contexte, ags)
    return nom, code


def creer_app(chemin_base=None) -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET", "dev")
    app.config["SESSION_COOKIE_SAMESITE"] = "None"   # lancement depuis l'iframe Moodle
    app.config["SESSION_COOKIE_SECURE"] = True
    cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})
    app.cx = base.ouvrir(chemin_base or os.environ.get("COMPAGNON_BASE", "compagnon.sqlite3"))
    # la table config_lti reflète le déploiement courant, spec section 6.2
    app.cx.execute("INSERT OR REPLACE INTO config_lti VALUES (?, ?, ?, ?, ?, ?)",
                   (os.environ["MOODLE_ISS"], os.environ["MOODLE_CLIENT_ID"],
                    os.environ["MOODLE_DEPLOYMENT_ID"], os.environ["MOODLE_AUTH_LOGIN_URL"],
                    os.environ["MOODLE_AUTH_TOKEN_URL"], os.environ["MOODLE_KEY_SET_URL"]))
    app.cx.commit()

    def stockage():
        return FlaskCacheDataStorage(cache)

    @app.get("/")
    def aide():
        return PAGE_AIDE.format(racine=request.url_root)

    @app.get("/.well-known/jwks.json")
    def jwks():
        return jsonify(lti.jwks())

    @app.route("/lti/login", methods=["GET", "POST"])
    def login():
        requete = FlaskRequest()
        oidc = FlaskOIDCLogin(requete, lti.conf_outil(), launch_data_storage=stockage())
        return oidc.enable_check_cookies().redirect(requete.get_param("target_link_uri"))

    @app.post("/lti/launch")
    def launch():
        lancement = FlaskMessageLaunch(FlaskRequest(), lti.conf_outil(),
                                       launch_data_storage=stockage())
        nom, code = traiter_lancement(app.cx, lancement.get_launch_data())
        return PAGE_CODE.format(nom=nom, code=f"{code[:3]}-{code[3:]}")

    return app


application = creer_app()  # point d'entrée gunicorn
```

Note : `creer_app()` au niveau module exige les variables d'environnement. Pour que
les tests puissent importer le module sans elles, protéger la dernière ligne :
`if os.environ.get("MOODLE_ISS"): application = creer_app()`.

- [ ] **Step 7: Vérifier que les tests passent**

Run: `compagnon/.venv/bin/python -m pytest compagnon/tests/ -v`
Expected: tous PASS, dont les trois de `test_app.py`.

- [ ] **Step 8: Commit**

```bash
git add compagnon/ .gitignore
git commit -m "Compagnon : squelette Flask, config LTI, JWKS et page du code d'appairage"
```

---

### Task 3: Validation manuelle, lancement LTI réel dans le bac à sable

Tâche manuelle, spec section 14 point 1 : le chemin risqué d'abord. Rien à coder,
tout à vérifier. Prérequis : compte Render gratuit, le repo GitHub est public.

- [ ] **Step 1: Générer les clés**

Run: `compagnon/.venv/bin/python -m compagnon.cles`
Garder les deux blocs PEM pour l'étape suivante. Ne jamais les committer.

- [ ] **Step 2: Créer le service Render**

Sur render.com : New, Web Service, connecter le repo `stage1a-tp-c-plateforme`,
branche `version-projet`. Root Directory : vide, racine du repo. Runtime Python.
Build : `pip install -r compagnon/requirements.txt`. Start :
`gunicorn compagnon.app:application`. Retenir l'URL, par exemple
`https://compagnon-tp-c.onrender.com`.

Variables d'environnement Render, première salve : `TOOL_PRIVATE_KEY`,
`TOOL_PUBLIC_KEY` (les PEM du Step 1), `FLASK_SECRET` (une chaîne aléatoire),
`TOTAL_ETAPES=6`, et des valeurs provisoires pour les `MOODLE_*` : `MOODLE_ISS=https://moodle.inp-toulouse.fr`,
`MOODLE_AUTH_LOGIN_URL=https://moodle.inp-toulouse.fr/mod/lti/auth.php`,
`MOODLE_AUTH_TOKEN_URL=https://moodle.inp-toulouse.fr/mod/lti/token.php`,
`MOODLE_KEY_SET_URL=https://moodle.inp-toulouse.fr/mod/lti/certs.php`,
`MOODLE_CLIENT_ID=provisoire`, `MOODLE_DEPLOYMENT_ID=provisoire`.

Vérifier : `https://<url>/` affiche la page d'aide, `https://<url>/.well-known/jwks.json`
rend une clé.

- [ ] **Step 3: Enregistrer l'outil dans Moodle**

Dans le cours bac à sable id 4665 : Plus, Outils externes LTI, Ajouter outil.
Configuration manuelle, version LTI 1.3. Renseigner avec les URL de la page d'aide
du compagnon. Type de clé publique : URL du jeu de clés, keyset. Services : IMS LTI
Assignment and Grade Services, choisir l'option de synchronisation des notes.
Confidentialité : partager le nom. Cocher « Afficher dans le sélecteur d'activités ».

Après l'enregistrement, ouvrir les détails de configuration de l'outil, menu de la
ligne dans la liste. Copier « ID client » et « ID de déploiement » dans les
variables Render `MOODLE_CLIENT_ID` et `MOODLE_DEPLOYMENT_ID`, redéployer.

- [ ] **Step 4: Créer l'activité et cliquer**

Dans le cours, activer le mode édition, Ajouter une activité, choisir l'outil.
Dans les réglages de l'activité, note maximale 100, et dans la description, la
limite voulue par la spec section 9 : « Suivi de progression de l'atelier TP C.
Ce score reflète l'avancement, ce n'est pas une note d'examen. » Enregistrer,
puis cliquer sur l'activité.

Expected : la page « Bonjour Ennedoui Sami » avec un code au format `KX7-3PF`.
Compter le réveil de Render, jusqu'à une minute au premier clic. En cas d'erreur
pylti1p3, lire les logs Render : c'est ici que les surprises du protocole se
montrent, les corriger avant de continuer.

- [ ] **Step 5: Consigner**

Noter dans `compagnon/README.md`, section « Journal des validations », la date, ce
qui a marché, les surprises corrigées. Commit :

```bash
git add compagnon/README.md
git commit -m "Compagnon : lancement LTI validé dans le bac à sable"
```

---

### Task 4: Poussée AGS d'une note en dur

**Files:**
- Create: `compagnon/pousse_test.py`

**Interfaces:**
- Consumes: `lti.pousser_score`, `base.ouvrir`, `base.notes_en_attente` (Tasks 1, 2).
- Produces: rien de nouveau, valide le canal AGS, spec section 14 point 2.

- [ ] **Step 1: Écrire le script**

```python
# compagnon/pousse_test.py
"""Pousse une note d'essai au carnet Moodle pour l'appairage le plus récent.
Usage : python -m compagnon.pousse_test 42.0
À lancer dans le shell Render, où vivent la base et les variables d'environnement."""
import json
import sys

from compagnon import base, lti

if __name__ == "__main__":
    valeur = float(sys.argv[1])
    cx = base.ouvrir("compagnon.sqlite3")
    ligne = cx.execute("SELECT sub, ags_claim FROM appairages ORDER BY cree DESC LIMIT 1").fetchone()
    if ligne is None:
        sys.exit("aucun appairage : cliquer d'abord l'activité dans Moodle")
    lti.pousser_score(ligne["sub"], valeur, json.loads(ligne["ags_claim"]))
    print(f"note {valeur} poussée pour {ligne['sub']}")
```

- [ ] **Step 2: Valider contre le vrai Moodle**

Cliquer l'activité dans le bac à sable pour créer un appairage frais, puis dans le
shell Render : `python -m compagnon.pousse_test 42.0`.

Expected : dans Moodle, Notes du cours, la colonne de l'activité affiche 42 pour
ton compte. Si erreur de scope ou de lineitem, vérifier que le service AGS est bien
activé dans l'outil et que l'activité a une note maximale, corriger, recommencer.

- [ ] **Step 3: Commit**

```bash
git add compagnon/pousse_test.py compagnon/README.md
git commit -m "Compagnon : canal AGS validé, note d'essai visible au carnet"
```

---

### Task 5: API de l'app, appairage, événements, score et rejeu

**Files:**
- Modify: `compagnon/app.py`
- Test: `compagnon/tests/test_app.py`

**Interfaces:**
- Consumes: tout Task 1, `lti.pousser_score`.
- Produces: `POST /api/appairage` corps `{"code": str}`, rend 200 `{"jeton": str}` ou 404 `{"erreur": "code inconnu ou expiré"}` ; `POST /api/evenements` en-tête `Authorization: Bearer <jeton>`, corps `{"evenements": [{"etape": str, "reussite": bool, "horodatage": str}]}`, rend 200 `{"recu": int, "score": float}` ou 401 ; `demarrer_rejeu(app, periode=300)` qui repousse les notes en attente.

- [ ] **Step 1: Ajouter les tests qui échouent**

Ajouter à `compagnon/tests/test_app.py` :

```python
class TestApi(unittest.TestCase):
    def setUp(self):
        _env_test()
        from compagnon import app as module_app
        self.module_app = module_app
        self.app = module_app.creer_app(":memory:")
        self.client = self.app.test_client()
        self.pousses = []
        # on ne pousse jamais vers un vrai Moodle en test
        module_app.lti.pousser_score = lambda sub, v, ags: self.pousses.append((sub, v))

    def _appairer(self):
        from compagnon import base
        code = base.enregistrer_lancement(
            self.app.cx, "u12", "Sami", "c4665",
            {"lineitem": "https://moodle.example/ligne/1", "scope": []})
        r = self.client.post("/api/appairage", json={"code": code})
        self.assertEqual(r.status_code, 200)
        return r.get_json()["jeton"]

    def test_appairage_code_valide_puis_rejoue(self):
        jeton = self._appairer()
        self.assertTrue(jeton)
        r = self.client.post("/api/appairage", json={"code": "XXXXXX"})
        self.assertEqual(r.status_code, 404)

    def test_evenements_score_et_poussee(self):
        jeton = self._appairer()
        r = self.client.post("/api/evenements",
                             headers={"Authorization": f"Bearer {jeton}"},
                             json={"evenements": [
                                 {"etape": "perso_P1", "reussite": True,
                                  "horodatage": "2026-07-07T10:00:00"},
                                 {"etape": "jalon1_parametrage", "reussite": True,
                                  "horodatage": "2026-07-07T10:05:00"}]})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json(), {"recu": 2, "score": 33.3})  # 2 sur TOTAL_ETAPES=6
        self.assertEqual(self.pousses, [("u12", 33.3)])

    def test_evenements_sans_jeton_refuses(self):
        r = self.client.post("/api/evenements", json={"evenements": []})
        self.assertEqual(r.status_code, 401)
        r = self.client.post("/api/evenements",
                             headers={"Authorization": "Bearer faux"},
                             json={"evenements": []})
        self.assertEqual(r.status_code, 401)

    def test_moodle_en_panne_la_note_reste_en_attente(self):
        from compagnon import base
        jeton = self._appairer()
        def echoue(sub, v, ags):
            raise OSError("moodle injoignable")
        self.module_app.lti.pousser_score = echoue
        r = self.client.post("/api/evenements",
                             headers={"Authorization": f"Bearer {jeton}"},
                             json={"evenements": [
                                 {"etape": "perso_P1", "reussite": True,
                                  "horodatage": "2026-07-07T10:00:00"}]})
        self.assertEqual(r.status_code, 200)  # l'app n'attend pas Moodle
        attente = base.notes_en_attente(self.app.cx)
        self.assertEqual(len(attente), 1)
        # le rejeu la pousse quand Moodle revit
        self.module_app.lti.pousser_score = lambda sub, v, ags: self.pousses.append((sub, v))
        self.module_app.repousser_notes(self.app)
        self.assertEqual(self.pousses, [("u12", 16.7)])
        self.assertEqual(base.notes_en_attente(self.app.cx), [])
```

- [ ] **Step 2: Vérifier qu'ils échouent**

Run: `compagnon/.venv/bin/python -m pytest compagnon/tests/test_app.py -v`
Expected: les nouveaux tests échouent en 404 ou `AttributeError: repousser_notes`.

- [ ] **Step 3: Implémenter dans `compagnon/app.py`**

Ajouter dans `creer_app`, avant `return app` :

```python
    @app.post("/api/appairage")
    def appairage():
        jeton = base.echanger_code(app.cx, (request.get_json() or {}).get("code", ""))
        if jeton is None:
            return jsonify({"erreur": "code inconnu ou expiré"}), 404
        return jsonify({"jeton": jeton})

    @app.post("/api/evenements")
    def evenements():
        entete = request.headers.get("Authorization", "")
        sub = base.sub_du_jeton(app.cx, entete.removeprefix("Bearer ").strip())
        if sub is None:
            return jsonify({"erreur": "jeton inconnu"}), 401
        evts = (request.get_json() or {}).get("evenements", [])
        n = base.ajouter_evenements(app.cx, sub, evts)
        valeur = base.score(len(base.etapes_validees(app.cx, sub)),
                            int(os.environ["TOTAL_ETAPES"]))
        base.marquer_a_pousser(app.cx, sub, valeur)
        _pousser_sans_bloquer(app, sub)
        return jsonify({"recu": n, "score": valeur})
```

Et au niveau module :

```python
def _pousser_sans_bloquer(app, sub):
    """Tente la poussée tout de suite ; si Moodle ne répond pas, la note reste
    marquée à pousser et le rejeu s'en chargera, spec section 8."""
    for s, valeur, ags in base.notes_en_attente(app.cx):
        if s != sub:
            continue
        try:
            lti.pousser_score(s, valeur, ags)
            base.marquer_poussee(app.cx, s)
        except Exception:
            pass


def repousser_notes(app) -> None:
    """Un tour de rejeu : repousse toutes les notes en attente."""
    for sub, valeur, ags in base.notes_en_attente(app.cx):
        try:
            lti.pousser_score(sub, valeur, ags)
            base.marquer_poussee(app.cx, sub)
        except Exception:
            pass


def demarrer_rejeu(app, periode: int = 300) -> None:
    """Boucle de rejeu périodique dans un fil discret, spec section 8."""
    import threading

    def boucle():
        while True:
            time.sleep(periode)
            repousser_notes(app)

    threading.Thread(target=boucle, daemon=True).start()
```

Ajouter `import time` en tête, et après la création de `application` sous garde
d'environnement, appeler `demarrer_rejeu(application)`.

- [ ] **Step 4: Vérifier que tout passe**

Run: `compagnon/.venv/bin/python -m pytest compagnon/tests/ -v`
Expected: tous PASS. Pousser sur GitHub pour redéployer Render.

- [ ] **Step 5: Commit**

```bash
git add compagnon/app.py compagnon/tests/test_app.py
git commit -m "Compagnon : API d'appairage et d'événements, score et rejeu des notes"
```

---

### Task 6: Module moodle_sync.py côté app

**Files:**
- Create: `moodle_sync.py`
- Modify: `chemins.py` (deux constantes)
- Test: `tests/test_moodle_sync.py`

**Interfaces:**
- Consumes: `POST /api/appairage` et `POST /api/evenements` (Task 5), `chemins.MOODLE_SYNC_FICHIER`, `chemins.COMPAGNON_URL`.
- Produces: `appairer(code: str, fichier=chemins.MOODLE_SYNC_FICHIER, url=None) -> tuple[bool, str]`, `signaler_porte(id_etape: str, fichier=chemins.MOODLE_SYNC_FICHIER, attendre=False) -> None`, `rejouer(fichier=chemins.MOODLE_SYNC_FICHIER, attendre=False) -> None`, `actif(fichier=...) -> bool`.

- [ ] **Step 1: Ajouter les constantes dans `chemins.py`**

Après la ligne `PROGRESSION_FICHIER = RACINE / "progression.json"` :

```python
# appairage et file d'attente Moodle, à côté de la progression, spec compagnon LTI
MOODLE_SYNC_FICHIER = RACINE / "moodle_sync.json"
COMPAGNON_URL = os.environ.get("ATELIER_COMPAGNON_URL",
                               "https://compagnon-tp-c.onrender.com")
```

Ajouter `import os` en tête de `chemins.py`. Remplacer l'URL par celle du service
Render réel de la Task 3.

- [ ] **Step 2: Écrire les tests qui échouent**

```python
# tests/test_moodle_sync.py
"""Tests du pont vers le compagnon : file locale, appairage, inertie sans appairage."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import moodle_sync


def reponse_http(corps: dict):
    """Fabrique le double d'une réponse urllib utilisable en with."""
    r = mock.MagicMock()
    r.read.return_value = json.dumps(corps).encode()
    r.__enter__ = lambda s: s
    r.__exit__ = mock.MagicMock(return_value=False)
    return r


class TestMoodleSync(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.fichier = Path(self.d.name) / "moodle_sync.json"

    def tearDown(self):
        self.d.cleanup()

    def test_sans_appairage_signaler_ne_fait_rien(self):
        self.assertFalse(moodle_sync.actif(self.fichier))
        with mock.patch("moodle_sync.urllib.request.urlopen") as u:
            moodle_sync.signaler_porte("perso_P1", fichier=self.fichier)
            u.assert_not_called()
        self.assertFalse(self.fichier.exists())

    def test_appairer_range_le_jeton(self):
        with mock.patch("moodle_sync.urllib.request.urlopen",
                        return_value=reponse_http({"jeton": "J123"})):
            ok, message = moodle_sync.appairer("KX7-3PF", fichier=self.fichier,
                                               url="https://compagnon.example")
        self.assertTrue(ok)
        d = json.loads(self.fichier.read_text(encoding="utf-8"))
        self.assertEqual(d["jeton"], "J123")
        self.assertTrue(moodle_sync.actif(self.fichier))

    def test_appairer_code_refuse(self):
        import urllib.error
        with mock.patch("moodle_sync.urllib.request.urlopen",
                        side_effect=urllib.error.HTTPError("u", 404, "non", {}, None)):
            ok, message = moodle_sync.appairer("XXXXXX", fichier=self.fichier,
                                               url="https://compagnon.example")
        self.assertFalse(ok)
        self.assertIn("code", message.lower())

    def test_porte_passee_envoyee_et_file_videe(self):
        self.fichier.write_text(json.dumps(
            {"url": "https://compagnon.example", "jeton": "J123", "file": []}),
            encoding="utf-8")
        with mock.patch("moodle_sync.urllib.request.urlopen",
                        return_value=reponse_http({"recu": 1, "score": 16.7})):
            moodle_sync.signaler_porte("perso_P1", fichier=self.fichier, attendre=True)
        d = json.loads(self.fichier.read_text(encoding="utf-8"))
        self.assertEqual(d["file"], [])

    def test_compagnon_muet_l_evenement_reste_en_file(self):
        self.fichier.write_text(json.dumps(
            {"url": "https://compagnon.example", "jeton": "J123", "file": []}),
            encoding="utf-8")
        with mock.patch("moodle_sync.urllib.request.urlopen", side_effect=OSError("rien")):
            moodle_sync.signaler_porte("perso_P1", fichier=self.fichier, attendre=True)
        d = json.loads(self.fichier.read_text(encoding="utf-8"))
        self.assertEqual(len(d["file"]), 1)
        self.assertEqual(d["file"][0]["etape"], "perso_P1")
        # le compagnon revit, la file se vide au rejeu suivant
        with mock.patch("moodle_sync.urllib.request.urlopen",
                        return_value=reponse_http({"recu": 1, "score": 16.7})):
            moodle_sync.rejouer(fichier=self.fichier, attendre=True)
        d = json.loads(self.fichier.read_text(encoding="utf-8"))
        self.assertEqual(d["file"], [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Vérifier qu'ils échouent**

Run: `python3 -m pytest tests/test_moodle_sync.py -v`
Expected: `ModuleNotFoundError: No module named 'moodle_sync'`.

- [ ] **Step 4: Implémenter `moodle_sync.py`**

```python
# moodle_sync.py
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
```

- [ ] **Step 5: Vérifier que tout passe**

Run: `python3 -m pytest tests/ -v`
Expected: la suite entière PASS, anciens tests compris.

- [ ] **Step 6: Commit**

```bash
git add moodle_sync.py chemins.py tests/test_moodle_sync.py
git commit -m "App : moodle_sync, appairage et file locale vers le compagnon"
```

---

### Task 7: Branchement dans la fenêtre

**Files:**
- Modify: `fenetre.py` (import, bouton colonne gauche, hook dans `_afficher_porte`)

**Interfaces:**
- Consumes: `moodle_sync.appairer`, `moodle_sync.signaler_porte`, `moodle_sync.rejouer`, `moodle_sync.actif`.
- Produces: rien, dernier maillon UI.

- [ ] **Step 1: Ajouter l'import et le bouton**

Dans `fenetre.py`, ajouter `import moodle_sync` après `import lsp_clangd`. Dans la
construction de la colonne gauche, après `gauche.addWidget(self.liste)` :

```python
        self.b_moodle = QPushButton("Connecté à Moodle" if moodle_sync.actif()
                                    else "Connecter à Moodle")
        self.b_moodle.clicked.connect(self._connecter_moodle)
        gauche.addWidget(self.b_moodle)
```

- [ ] **Step 2: La méthode d'appairage**

Ajouter à la classe, près de `_maj_cran` :

```python
    def _connecter_moodle(self):
        code, ok = QInputDialog.getText(
            self, "Connecter à Moodle",
            "Colle le code affiché par l'activité Moodle du TP :")
        if not ok or not code.strip():
            return
        reussi, message = moodle_sync.appairer(code.strip())
        self.console.setPlainText(message)
        if reussi:
            self.b_moodle.setText("Connecté à Moodle")
            moodle_sync.rejouer()
```

- [ ] **Step 3: Le hook de porte et le rejeu au lancement**

Dans `_afficher_porte`, juste après `self.prog = progression.valider(self.etape, self.prog)` :

```python
            if not self.demo:
                moodle_sync.signaler_porte(self.etape.id)
```

À la fin de `__init__`, un rejeu au lancement pour vider ce qui attend :

```python
        moodle_sync.rejouer()
```

- [ ] **Step 4: Vérifier**

Run: `python3 -m pytest tests/ -v` puis lancement manuel `python3 atelier_snake.py`.
Expected: suite verte ; le bouton apparaît sous la liste ; sans appairage, passer
une porte ne déclenche aucun appel réseau, vérifiable en coupant le réseau.

- [ ] **Step 5: Commit**

```bash
git add fenetre.py
git commit -m "Fenêtre : bouton Connecter à Moodle et signalement des portes passées"
```

---

### Task 8: Empaquetage, documentation, bout en bout

**Files:**
- Create: `compagnon/Dockerfile`
- Modify: `compagnon/README.md`

- [ ] **Step 1: Dockerfile**

```dockerfile
FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./compagnon/
ENV PYTHONPATH=/srv
CMD ["gunicorn", "-b", "0.0.0.0:8000", "compagnon.app:application"]
```

Vérifier localement : `docker build -t compagnon compagnon/` puis lancer avec les
variables d'environnement de test et visiter `http://localhost:8000/`.

- [ ] **Step 2: README du compagnon**

Compléter `compagnon/README.md` : rôle du service, les neuf variables
d'environnement et d'où vient chacune, la procédure d'enregistrement Moodle de la
Task 3 condensée, la règle données personnelles de la spec section 10, la limite
disque éphémère de Render, et la procédure de migration école, conteneur plus
variables, spec section 11.

- [ ] **Step 3: Bout en bout dans le bac à sable**

Le test réel de la spec section 13 point 3, dans l'ordre : cliquer l'activité,
coller le code dans une app lancée localement, passer la porte `perso_P1`, ouvrir
le carnet de notes du cours.

Expected : la colonne passe à 16.7 sur 100 sans action manuelle. Puis couper le
réseau, passer une autre porte, le relancer, relancer l'app : la note rattrape.

- [ ] **Step 4: Consigner et committer**

```bash
git add compagnon/Dockerfile compagnon/README.md
git commit -m "Compagnon : conteneur, documentation de déploiement, bout en bout validé"
```
