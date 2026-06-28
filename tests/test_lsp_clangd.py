"""Tests du module lsp_clangd. Aucun processus clangd n'est lancé.
Les messages JSON-RPC sont construits à la main pour tester l'encodage/décodage
et le rendu Qt. Le test Qt tourne en mode offscreen (QT_QPA_PLATFORM=offscreen)."""
import os
import sys
import unittest

# La variable doit être posée avant tout import Qt.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Ajoute la racine du projet au chemin pour trouver lsp_clangd.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lsp_clangd import (
    Diagnostic,
    clangd_disponible,
    encadrer_message,
    extraire_diagnostics,
    lire_messages,
    appliquer_diagnostics,
)


# ---------------------------------------------------------------------------
# Tests purs : encodage/décodage JSON-RPC
# ---------------------------------------------------------------------------

class TestEncodageDecodage(unittest.TestCase):
    """Vérifie que encadrer_message suivi de lire_messages est un aller-retour exact."""

    def test_aller_retour_simple(self):
        msg = {"jsonrpc": "2.0", "method": "test", "params": {"x": 1}}
        encoded = encadrer_message(msg)
        messages, reste = lire_messages(encoded)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], msg)
        self.assertEqual(reste, b"")

    def test_deux_messages_colles(self):
        m1 = {"jsonrpc": "2.0", "method": "premier"}
        m2 = {"jsonrpc": "2.0", "method": "second", "params": {"n": 42}}
        tampon = encadrer_message(m1) + encadrer_message(m2)
        messages, reste = lire_messages(tampon)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["method"], "premier")
        self.assertEqual(messages[1]["params"]["n"], 42)
        self.assertEqual(reste, b"")

    def test_message_partiel_reste_en_tampon(self):
        msg = {"jsonrpc": "2.0", "method": "test", "params": {"cle": "valeur"}}
        encoded = encadrer_message(msg)
        # on coupe au milieu du corps JSON
        partiel = encoded[: len(encoded) // 2]
        messages, reste = lire_messages(partiel)
        self.assertEqual(messages, [])
        self.assertEqual(reste, partiel)

    def test_message_complet_suivi_dun_partiel(self):
        m1 = {"jsonrpc": "2.0", "method": "complet"}
        m2 = {"jsonrpc": "2.0", "method": "partiel", "params": {"long": "x" * 100}}
        encoded1 = encadrer_message(m1)
        encoded2 = encadrer_message(m2)
        # m1 complet + début de m2
        tampon = encoded1 + encoded2[: len(encoded2) // 2]
        messages, reste = lire_messages(tampon)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["method"], "complet")
        # le reste contient le début de m2
        self.assertGreater(len(reste), 0)

    def test_tampon_vide(self):
        messages, reste = lire_messages(b"")
        self.assertEqual(messages, [])
        self.assertEqual(reste, b"")

    def test_encadrer_encode_en_utf8(self):
        msg = {"jsonrpc": "2.0", "method": "x", "params": {"texte": "été"}}
        encoded = encadrer_message(msg)
        self.assertIn(b"Content-Length:", encoded)
        messages, _ = lire_messages(encoded)
        self.assertEqual(messages[0]["params"]["texte"], "été")


# ---------------------------------------------------------------------------
# Tests de extraire_diagnostics
# ---------------------------------------------------------------------------

_NOTIF_REALISTE = {
    "jsonrpc": "2.0",
    "method": "textDocument/publishDiagnostics",
    "params": {
        "uri": "file:///tmp/atelier_lsp_/atelier.c",
        "diagnostics": [
            {
                "range": {
                    "start": {"line": 4, "character": 8},
                    "end": {"line": 4, "character": 15},
                },
                "severity": 1,
                "message": "variable non déclarée : 'resultat'",
                "source": "clang",
            },
            {
                "range": {
                    "start": {"line": 9, "character": 0},
                    "end": {"line": 9, "character": 6},
                },
                "severity": 2,
                "message": "valeur de retour ignorée (attribut 'warn_unused_result')",
                "source": "clang",
            },
        ],
    },
}


class TestExtraireDiagnostics(unittest.TestCase):

    def test_parse_notification_realiste(self):
        diags = extraire_diagnostics(_NOTIF_REALISTE)
        self.assertEqual(len(diags), 2)

    def test_erreur_ligne_colonne(self):
        diags = extraire_diagnostics(_NOTIF_REALISTE)
        erreur = diags[0]
        self.assertEqual(erreur.ligne, 4)
        self.assertEqual(erreur.colonne, 8)
        self.assertEqual(erreur.ligne_fin, 4)
        self.assertEqual(erreur.colonne_fin, 15)
        self.assertEqual(erreur.severite, 1)
        self.assertIn("resultat", erreur.message)

    def test_avertissement(self):
        diags = extraire_diagnostics(_NOTIF_REALISTE)
        avert = diags[1]
        self.assertEqual(avert.ligne, 9)
        self.assertEqual(avert.severite, 2)
        self.assertIn("retour", avert.message)

    def test_notif_diagnostics_vides(self):
        notif = {
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {"uri": "file:///tmp/ok.c", "diagnostics": []},
        }
        self.assertEqual(extraire_diagnostics(notif), [])

    def test_mauvaise_methode_renvoie_liste_vide(self):
        notif = {"jsonrpc": "2.0", "method": "window/logMessage", "params": {}}
        self.assertEqual(extraire_diagnostics(notif), [])

    def test_diagnostic_rend_un_dataclass(self):
        diags = extraire_diagnostics(_NOTIF_REALISTE)
        self.assertIsInstance(diags[0], Diagnostic)


# ---------------------------------------------------------------------------
# Test de clangd_disponible
# ---------------------------------------------------------------------------

class TestClangdDisponible(unittest.TestCase):

    def test_renvoie_un_booleen(self):
        resultat = clangd_disponible()
        self.assertIsInstance(resultat, bool)


# ---------------------------------------------------------------------------
# Test Qt offscreen : rendu des soulignements
# ---------------------------------------------------------------------------

class TestRenduDiagnostics(unittest.TestCase):
    """Prouve que appliquer_diagnostics pose bien les extra selections sur un
    QPlainTextEdit. N'exige pas clangd."""

    @classmethod
    def setUpClass(cls):
        from PyQt6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication(sys.argv[:1])

    def _creer_editeur(self, texte: str):
        from PyQt6.QtWidgets import QPlainTextEdit
        e = QPlainTextEdit()
        e.setPlainText(texte)
        return e

    def test_nombre_de_selections_correct(self):
        code = "int x = ;\nvoid f() {}\nreturn 0;\n"
        editeur = self._creer_editeur(code)
        diags = [
            Diagnostic(ligne=0, colonne=8, ligne_fin=0, colonne_fin=9,
                       severite=1, message="erreur syntaxe"),
            Diagnostic(ligne=2, colonne=0, ligne_fin=2, colonne_fin=6,
                       severite=2, message="return hors fonction"),
        ]
        appliquer_diagnostics(editeur, diags)
        sels = editeur.extraSelections()
        self.assertEqual(len(sels), 2)

    def test_liste_vide_efface_les_selections(self):
        code = "int x = ;\n"
        editeur = self._creer_editeur(code)
        diags = [Diagnostic(0, 8, 0, 9, 1, "erreur")]
        appliquer_diagnostics(editeur, diags)
        self.assertEqual(len(editeur.extraSelections()), 1)
        appliquer_diagnostics(editeur, [])
        self.assertEqual(len(editeur.extraSelections()), 0)

    def test_plage_selection_correspond_au_diagnostic(self):
        code = "int x = ;\n"
        editeur = self._creer_editeur(code)
        diag = Diagnostic(ligne=0, colonne=4, ligne_fin=0, colonne_fin=5,
                          severite=1, message="type attendu")
        appliquer_diagnostics(editeur, [diag])
        sels = editeur.extraSelections()
        self.assertEqual(len(sels), 1)
        curseur = sels[0].cursor
        doc = editeur.document()
        bloc = doc.findBlockByLineNumber(0)
        # position de début attendue : debut du bloc + colonne
        pos_attendue = bloc.position() + 4
        self.assertEqual(curseur.selectionStart(), pos_attendue)
        # position de fin attendue : debut du bloc + colonne_fin
        pos_fin_attendue = bloc.position() + 5
        self.assertEqual(curseur.selectionEnd(), pos_fin_attendue)

    def test_diagnostic_hors_document_est_ignore(self):
        code = "int x;\n"  # 1 seule ligne
        editeur = self._creer_editeur(code)
        diag = Diagnostic(ligne=99, colonne=0, ligne_fin=99, colonne_fin=5,
                          severite=1, message="ligne inexistante")
        appliquer_diagnostics(editeur, [diag])
        # aucun plantage et aucune sélection
        self.assertEqual(len(editeur.extraSelections()), 0)


# ---------------------------------------------------------------------------
# Test live : lance vraiment clangd. Sauté si clang-tools-extra est absent,
# donc la suite reste verte partout. Là où clangd existe, il prouve la chaîne
# complète : lancement, handshake, didOpen, remontée par le signal Qt, arrêt.
# ---------------------------------------------------------------------------

@unittest.skipUnless(clangd_disponible(), "clangd absent, test live ignoré")
class TestClangdLive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from PyQt6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication(sys.argv[:1])

    def _charger_etape(self):
        import chemins
        from modele_etape import charger_etape
        return charger_etape(chemins.CONTENU / "perso_P1")

    def _attendre(self, predicat, ms=12000):
        from PyQt6.QtCore import QEventLoop, QTimer
        loop = QEventLoop()
        sonde = QTimer()
        sonde.timeout.connect(lambda: predicat() and loop.quit())
        sonde.start(150)
        secours = QTimer()
        secours.setSingleShot(True)
        secours.timeout.connect(loop.quit)
        secours.start(ms)
        loop.exec()

    def test_diagnostics_live_sur_code_fautif(self):
        from lsp_clangd import ClientClangd
        etape = self._charger_etape()
        # 'y' n'est pas déclaré : clangd doit signaler une erreur
        code = ("#include <stdio.h>\nint main(void){\n"
                "    int x = y + 1;\n    return x;\n}\n")
        recus = []
        client = ClientClangd(etape)
        client.diagnostics_recus.connect(recus.append)
        client.demarrer(code)
        try:
            self._attendre(lambda: any(lot for lot in recus))
            non_vides = [lot for lot in recus if lot]
            self.assertTrue(non_vides, "clangd n'a renvoyé aucun diagnostic")
            erreurs = [d for lot in non_vides for d in lot if d.severite == 1]
            self.assertTrue(erreurs, "aucune erreur signalée sur du code fautif")
        finally:
            client.arreter()
            self.assertTrue(client.wait(3000), "le client clangd ne s'est pas arrêté")


if __name__ == "__main__":
    unittest.main()
