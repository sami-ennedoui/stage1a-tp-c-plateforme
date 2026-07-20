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
    })
    os.environ.pop("TOTAL_ETAPES", None)  # remplacée par etapes_notees.json


# Les six étapes que ce compagnon de test note. Tout id absent d'ici vient d'un
# parcours d'entraînement et ne doit peser sur aucune note.
NOTEES_TEST = ["perso_P1", "jalon1_parametrage", "n1", "n2", "n3", "n4"]


class TestApp(unittest.TestCase):
    def setUp(self):
        _env_test()
        from compagnon import app as module_app
        self.app = module_app.creer_app(":memory:", notees=NOTEES_TEST)
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

    def test_login_sans_parametres_montre_une_page_de_relance(self):
        # Réveil à froid de Render : la page d'attente recharge le POST de
        # lancement en GET sans ses paramètres, donc target_link_uri manque.
        # Au lieu d'un 500 illisible, on affiche une consigne de relance.
        # Régression du bug observé le 2026-07-11.
        r = self.client.get("/lti/login?lti1p3_new_window=1")
        self.assertEqual(r.status_code, 200)
        corps = r.get_data(as_text=True)
        self.assertIn("F5", corps)
        self.assertIn("relance", corps.lower())


class TestApi(unittest.TestCase):
    def setUp(self):
        _env_test()
        from compagnon import app as module_app
        self.module_app = module_app
        self.app = module_app.creer_app(":memory:", notees=NOTEES_TEST)
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

    def test_appairage_renvoie_les_etapes_deja_validees(self):
        """Reprise multi-poste : un étudiant qui se reconnecte (nouveau code) récupère
        la liste de ce qu'il a déjà validé, pour reprendre au bon niveau ailleurs."""
        from compagnon import base
        jeton = self._appairer()
        self.client.post("/api/evenements",
                         headers={"Authorization": f"Bearer {jeton}"},
                         json={"evenements": [
                             {"etape": "ex01_types", "reussite": True,
                              "horodatage": "2026-07-16T10:00:00"},
                             {"etape": "ex02_operateurs", "reussite": True,
                              "horodatage": "2026-07-16T10:05:00"}]})
        # nouvelle machine : nouveau lancement, nouveau code, nouvel appairage
        code = base.enregistrer_lancement(
            self.app.cx, "u12", "Sami", "c4665",
            {"lineitem": "https://moodle.example/ligne/1", "scope": []})
        r = self.client.post("/api/appairage", json={"code": code})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(sorted(r.get_json()["etapes_faites"]),
                         ["ex01_types", "ex02_operateurs"])

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
        self.assertEqual(r.get_json(), {"recu": 2, "score": 33.3})  # 2 des 6 étapes notées
        self.app.fil_poussee.join(timeout=5)
        self.assertEqual(self.pousses, [("u12", 33.3)])

    def test_un_parcours_non_note_ne_gonfle_pas_la_note(self):
        """L'atelier signale une porte franchie sans jamais dire de quel parcours elle
        vient, et les ids d'étapes sont uniques d'un parcours à l'autre. Le compagnon
        ne doit donc retenir que les étapes qu'il note, sinon un étudiant gagne des
        points en s'entraînant sur un parcours qui n'est pas noté."""
        jeton = self._appairer()
        entete = {"Authorization": f"Bearer {jeton}"}

        def valider(*etapes):
            r = self.client.post("/api/evenements", headers=entete, json={"evenements": [
                {"etape": e, "reussite": True, "horodatage": "2026-07-16T10:00:00"}
                for e in etapes]})
            return r.get_json()["score"]

        # 3 des 6 étapes notées : la moitié du parcours.
        self.assertEqual(valider("n1", "n2", "n3"), 50.0)
        # Il s'entraîne sur un parcours qui n'est pas noté. Sa note ne doit pas bouger.
        self.assertEqual(valider("entrainement_a", "entrainement_b", "entrainement_c"), 50.0)

    def test_une_variable_total_etapes_perimee_ne_fausse_plus_rien(self):
        """TOTAL_ETAPES vivait dans le tableau de bord Render, aucun test ne pouvait la
        lire et rien ne l'obligeait à suivre le contenu. Elle est restée sur le
        déploiement : il faut qu'elle soit inerte, même en mentant grossièrement."""
        os.environ["TOTAL_ETAPES"] = "2"          # le parcours de test en compte six
        try:
            app = self.module_app.creer_app(":memory:", notees=NOTEES_TEST)
            client = app.test_client()
            from compagnon import base
            code = base.enregistrer_lancement(app.cx, "u99", "Sami", "c4665",
                                              {"lineitem": "https://moodle.example/l/1",
                                               "scope": []})
            jeton = client.post("/api/appairage", json={"code": code}).get_json()["jeton"]
            r = client.post("/api/evenements",
                            headers={"Authorization": f"Bearer {jeton}"},
                            json={"evenements": [
                                {"etape": "n1", "reussite": True,
                                 "horodatage": "2026-07-16T10:00:00"},
                                {"etape": "n2", "reussite": True,
                                 "horodatage": "2026-07-16T10:01:00"}]})
            # Avec l'ancien code : 2 sur 2, soit 100. Avec la liste : 2 sur 6.
            self.assertEqual(r.get_json()["score"], 33.3)
        finally:
            os.environ.pop("TOTAL_ETAPES", None)

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
        self.app.fil_poussee.join(timeout=5)
        attente = base.notes_en_attente(self.app.cx)
        self.assertEqual(len(attente), 1)
        # le rejeu la pousse quand Moodle revit
        self.module_app.lti.pousser_score = lambda sub, v, ags: self.pousses.append((sub, v))
        self.module_app.repousser_notes(self.app)
        self.assertEqual(self.pousses, [("u12", 16.7)])
        self.assertEqual(base.notes_en_attente(self.app.cx), [])


if __name__ == "__main__":
    unittest.main()
