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
