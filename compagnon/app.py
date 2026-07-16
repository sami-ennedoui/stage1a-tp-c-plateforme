"""Routes du compagnon : lancement LTI, appairage, événements, page d'aide.
Spec section 6.1. La logique vit dans base.py et lti.py, ici on câble."""
import logging
import os
import threading
import time
from pathlib import Path

JOURNAL = logging.getLogger("compagnon")

from flask import Flask, jsonify, request
from flask_caching import Cache
from pylti1p3.contrib.flask import (FlaskCacheDataStorage, FlaskMessageLaunch,
                                    FlaskOIDCLogin, FlaskRequest)

from compagnon import base, lti, notation

# La base par défaut reste dans compagnon/, couverte par le .gitignore.
BASE_DEFAUT = Path(__file__).resolve().parent / "compagnon.sqlite3"

PAGE_CODE = """<!doctype html><meta charset="utf-8"><title>TP C</title>
<body style="font-family:sans-serif;max-width:36em;margin:4em auto">
<h1>Bonjour {nom}</h1>
<p>Ton code de connexion, à coller dans l'atelier, bouton
« Connecter à Moodle » :</p>
<p style="font-size:2.5em;letter-spacing:.2em;font-weight:bold">{code}</p>
<p>Il est valable dix minutes et ne sert qu'une fois. Pour en obtenir un
autre, reviens simplement ici depuis le cours.</p></body>"""

PAGE_REVEIL = """<!doctype html><meta charset="utf-8"><title>Atelier TP C</title>
<body style="font-family:sans-serif;max-width:36em;margin:4em auto">
<h1>L'atelier était en train de démarrer</h1>
<p>Le service se réveillait au moment où tu as ouvert l'activité. Il est prêt
maintenant.</p>
<p><strong>Rafraîchis la page avec la touche F5, ou reviens au cours et
relance l'activité « Atelier TP C ».</strong> Cette fois le code s'affichera
du premier coup.</p></body>"""

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
            JOURNAL.exception("poussée AGS échouée pour %s", sub)


def pousser_en_arriere_plan(app, sub):
    """Lance la poussée dans un fil démon : la réponse à l'app ne doit jamais
    attendre Moodle, spec section 8."""
    fil = threading.Thread(target=_pousser_sans_bloquer, args=(app, sub), daemon=True)
    fil.start()
    app.fil_poussee = fil
    return fil


def repousser_notes(app) -> None:
    """Un tour de rejeu : repousse toutes les notes en attente."""
    for sub, valeur, ags in base.notes_en_attente(app.cx):
        try:
            lti.pousser_score(sub, valeur, ags)
            base.marquer_poussee(app.cx, sub)
        except Exception:
            JOURNAL.exception("poussée AGS échouée pour %s", sub)


def demarrer_rejeu(app, periode: int = 300) -> None:
    """Boucle de rejeu périodique dans un fil discret, spec section 8."""

    def boucle():
        while True:
            time.sleep(periode)
            repousser_notes(app)

    threading.Thread(target=boucle, daemon=True).start()


def traiter_lancement(cx, donnees: dict) -> tuple[str, str]:
    """Couture testable : claims LTI déjà validés vers appairage et code court."""
    sub = donnees["sub"]
    nom = donnees.get("name", sub)
    contexte = donnees["https://purl.imsglobal.org/spec/lti/claim/context"]["id"]
    ags = donnees.get("https://purl.imsglobal.org/spec/lti-ags/claim/endpoint", {})
    code = base.enregistrer_lancement(cx, sub, nom, contexte, ags)
    return nom, code


def creer_app(chemin_base=None, notees=None) -> Flask:
    # les échecs de poussée doivent se voir dans les logs du serveur
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)
    # Le parcours noté, seule chose que le compagnon sache du contenu. Voir notation.py.
    app.etapes_notees = list(notees) if notees is not None else notation.charger()
    if "TOTAL_ETAPES" in os.environ:
        JOURNAL.warning(
            "TOTAL_ETAPES=%s est ignorée : le dénominateur vient maintenant de "
            "etapes_notees.json, qui liste %d étapes. La variable peut être retirée "
            "du déploiement.", os.environ["TOTAL_ETAPES"], len(app.etapes_notees))
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET", "dev")
    app.config["SESSION_COOKIE_SAMESITE"] = "None"   # lancement depuis l'iframe Moodle
    app.config["SESSION_COOKIE_SECURE"] = True
    cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})
    app.cx = base.ouvrir(chemin_base or os.environ.get("COMPAGNON_BASE", str(BASE_DEFAUT)))
    # la table config_lti est une trace du déploiement courant pour inspection ; la source de vérité de la configuration est l'environnement, lu par lti.conf_outil
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
        cible = requete.get_param("target_link_uri")
        # Réveil à froid de Render : la page d'attente recharge le POST de
        # lancement en GET sans son corps, donc les paramètres LTI disparaissent
        # et pylti1p3 lèverait « No launch URL configured ». Le service est chaud
        # à présent, on invite simplement à relancer plutôt que d'afficher un 500.
        if not cible:
            return PAGE_REVEIL, 200
        oidc = FlaskOIDCLogin(requete, lti.conf_outil(), launch_data_storage=stockage())
        return oidc.enable_check_cookies().redirect(cible)

    @app.post("/lti/launch")
    def launch():
        lancement = FlaskMessageLaunch(FlaskRequest(), lti.conf_outil(),
                                       launch_data_storage=stockage())
        nom, code = traiter_lancement(app.cx, lancement.get_launch_data())
        return PAGE_CODE.format(nom=nom, code=f"{code[:3]}-{code[3:]}")

    @app.post("/api/appairage")
    def appairage():
        jeton = base.echanger_code(app.cx, (request.get_json() or {}).get("code", ""))
        if jeton is None:
            return jsonify({"erreur": "code inconnu ou expiré"}), 404
        # Reprise multi-poste : on renvoie les étapes déjà validées de cet étudiant.
        # La note Moodle s'agrège ici, côté serveur, mais le déverrouillage des niveaux
        # vit dans progression.json, local à chaque poste. Sans ce renvoi, un étudiant
        # qui se connecte sur une nouvelle machine repart au niveau 1 alors que le
        # compagnon sait déjà ce qu'il a fait ailleurs.
        sub = base.sub_du_jeton(app.cx, jeton)
        faites = sorted(base.etapes_validees(app.cx, sub))
        return jsonify({"jeton": jeton, "etapes_faites": faites})

    @app.post("/api/evenements")
    def evenements():
        entete = request.headers.get("Authorization", "")
        sub = base.sub_du_jeton(app.cx, entete.removeprefix("Bearer ").strip())
        if sub is None:
            return jsonify({"erreur": "jeton inconnu"}), 401
        evts = (request.get_json() or {}).get("evenements", [])
        n = base.ajouter_evenements(app.cx, sub, evts)
        # On ne retient que les étapes notées : l'atelier signale les portes de tous les
        # parcours sans dire lequel, et sans ce filtre l'entraînement gonflerait la note.
        retenues = base.etapes_validees(app.cx, sub) & set(app.etapes_notees)
        valeur = base.score(len(retenues), len(app.etapes_notees))
        base.marquer_a_pousser(app.cx, sub, valeur)
        pousser_en_arriere_plan(app, sub)
        return jsonify({"recu": n, "score": valeur})

    return app


# point d'entrée gunicorn ; protégé pour que les tests importent le module sans
# les variables d'environnement de déploiement (spec section 11)
if os.environ.get("MOODLE_ISS"):
    application = creer_app()
    demarrer_rejeu(application)
