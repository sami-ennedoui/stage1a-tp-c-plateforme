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

    def test_evenement_ajoute_pendant_l_envoi_n_est_pas_perdu(self):
        # Une porte deja en file avant l'appel.
        self.fichier.write_text(json.dumps(
            {"url": "https://compagnon.example", "jeton": "J123",
             "file": [{"etape": "perso_P0", "reussite": True, "horodatage": "t0"}]}),
            encoding="utf-8")

        def urlopen_concurrent(requete, timeout=None):
            # Simule un signaler_porte concurrent qui ecrit dans le fichier
            # pendant que la requete precedente est en vol.
            d = json.loads(self.fichier.read_text(encoding="utf-8"))
            d["file"].append({"etape": "perso_P2", "reussite": True, "horodatage": "t2"})
            self.fichier.write_text(json.dumps(d), encoding="utf-8")
            return reponse_http({"recu": 2, "score": 33.3})

        with mock.patch("moodle_sync.urllib.request.urlopen",
                        side_effect=urlopen_concurrent):
            moodle_sync.signaler_porte("perso_P1", fichier=self.fichier, attendre=True)

        d = json.loads(self.fichier.read_text(encoding="utf-8"))
        # perso_P0 et perso_P1 ont ete envoyes et acquittes : retires.
        # perso_P2, arrive pendant l'envoi, n'a jamais ete envoye : il reste, une seule fois.
        self.assertEqual(len(d["file"]), 1)
        self.assertEqual(d["file"][0]["etape"], "perso_P2")

    def test_fichier_corrompu_ne_leve_pas(self):
        self.fichier.write_text("{ceci n'est pas du JSON valide", encoding="utf-8")
        self.assertFalse(moodle_sync.actif(self.fichier))
        with mock.patch("moodle_sync.urllib.request.urlopen") as u:
            moodle_sync.signaler_porte("perso_P1", fichier=self.fichier, attendre=True)
            u.assert_not_called()


if __name__ == "__main__":
    unittest.main()
