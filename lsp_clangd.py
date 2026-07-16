"""Intégration LSP clangd pour l'affichage de diagnostics en direct.
Diagnostics uniquement : pas d'autocomplétion, pas de survol, pas d'aller-à-la-définition.
C'est un choix pédagogique : le compilateur guide l'étudiant sans le décharger du travail.

Si clangd est absent (paquet Fedora : clang-tools-extra), le module se tait proprement.
Aucun plantage, un message français clair, le reste de la plateforme continue."""
import json
import shutil
import subprocess
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit

import chemins


# ---------------------------------------------------------------------------
# Modèle de donnée
# ---------------------------------------------------------------------------

@dataclass
class Diagnostic:
    """Un problème signalé par clangd : positions en base 0 (convention LSP)."""
    ligne: int
    colonne: int
    ligne_fin: int
    colonne_fin: int
    severite: int   # 1 = erreur, 2 = avertissement, 3 = info, 4 = indice
    message: str


# ---------------------------------------------------------------------------
# Fonctions pures (testables sans processus ni UI)
# ---------------------------------------------------------------------------

def clangd_disponible() -> bool:
    """Renvoie True si clangd est trouvé dans le PATH."""
    return shutil.which("clangd") is not None


def encadrer_message(obj: dict) -> bytes:
    """Encode un objet en JSON-RPC LSP avec l'en-tête Content-Length."""
    corps = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    en_tete = f"Content-Length: {len(corps)}\r\n\r\n".encode("ascii")
    return en_tete + corps


def lire_messages(tampon: bytes) -> tuple[list[dict], bytes]:
    """Extrait tous les messages JSON-RPC complets du tampon.

    Renvoie la liste des objets décodés et les octets non consommés.
    Un message partiel en fin de tampon reste dans le reste renvoyé.
    Plusieurs messages collés sont tous extraits en un seul appel."""
    messages = []
    sep = b"\r\n\r\n"
    while True:
        pos = tampon.find(sep)
        if pos == -1:
            break
        en_tete_brut = tampon[:pos].decode("ascii", errors="replace")
        longueur = None
        for ligne in en_tete_brut.splitlines():
            if ligne.lower().startswith("content-length:"):
                try:
                    longueur = int(ligne.split(":", 1)[1].strip())
                except ValueError:
                    pass
        if longueur is None:
            # en-tête malformé : on abandonne ce tampon pour éviter une boucle infinie
            break
        debut_corps = pos + len(sep)
        if len(tampon) < debut_corps + longueur:
            break  # message partiel, on attend la suite
        corps = tampon[debut_corps:debut_corps + longueur]
        try:
            messages.append(json.loads(corps))
        except json.JSONDecodeError:
            pass
        tampon = tampon[debut_corps + longueur:]
    return messages, tampon


def extraire_diagnostics(notif: dict) -> list[Diagnostic]:
    """Transforme une notification textDocument/publishDiagnostics en liste de Diagnostic.

    Renvoie une liste vide si la notification n'est pas du bon type."""
    if notif.get("method") != "textDocument/publishDiagnostics":
        return []
    params = notif.get("params", {})
    resultat = []
    for d in params.get("diagnostics", []):
        rang = d.get("range", {})
        debut = rang.get("start", {})
        fin = rang.get("end", {})
        resultat.append(Diagnostic(
            ligne=debut.get("line", 0),
            colonne=debut.get("character", 0),
            ligne_fin=fin.get("line", 0),
            colonne_fin=fin.get("character", 0),
            severite=d.get("severity", 1),
            message=d.get("message", ""),
        ))
    return resultat


def flags_pour_etape(etape) -> list[str]:
    """Renvoie les drapeaux de compilation à écrire dans compile_flags.txt.

    clangd lit ce fichier dans le dossier de travail pour résoudre les en-têtes."""
    flags = list(chemins.flags_toolchain_clangd())
    flags += chemins.cflags_sdl()
    flags += [f"-I{etape.dossier}", "-std=c11"]
    return flags


# ---------------------------------------------------------------------------
# Rendu Qt : applique les diagnostics sur un QPlainTextEdit
# ---------------------------------------------------------------------------

_COULEUR_ERREUR = "#f7768e"       # rouge du thème nuit
_COULEUR_AVERTISSEMENT = "#e0af68"  # ambre du thème nuit


def appliquer_diagnostics(editeur: QPlainTextEdit, diagnostics: list[Diagnostic]) -> None:
    """Pose les soulignements ondulés sur l'éditeur selon la liste de diagnostics.

    Les positions LSP sont en base 0. Les diagnostics hors des limites du document
    sont ignorés silencieusement."""
    selections = []
    doc = editeur.document()
    for diag in diagnostics:
        bloc_debut = doc.findBlockByLineNumber(diag.ligne)
        if not bloc_debut.isValid():
            continue
        bloc_fin = doc.findBlockByLineNumber(diag.ligne_fin)
        if not bloc_fin.isValid():
            bloc_fin = bloc_debut

        pos_debut = bloc_debut.position() + diag.colonne
        pos_fin = bloc_fin.position() + diag.colonne_fin
        if pos_fin <= pos_debut:
            pos_fin = pos_debut + 1  # au moins un caractère pour que le soulignement soit visible

        curseur = QTextCursor(doc)
        curseur.setPosition(pos_debut)
        curseur.setPosition(pos_fin, QTextCursor.MoveMode.KeepAnchor)

        fmt = QTextCharFormat()
        fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
        if diag.severite == 1:
            fmt.setUnderlineColor(QColor(_COULEUR_ERREUR))
        else:
            fmt.setUnderlineColor(QColor(_COULEUR_AVERTISSEMENT))

        sel = QTextEdit.ExtraSelection()
        sel.format = fmt
        sel.cursor = curseur
        selections.append(sel)

    editeur.setExtraSelections(selections)


# ---------------------------------------------------------------------------
# Client LSP : communique avec clangd dans un fil séparé
# ---------------------------------------------------------------------------

class ClientClangd(QThread):
    """Lance clangd en sous-processus et lit ses notifications dans un fil séparé.

    Le fil principal peut appeler notifier_changement() à tout moment.
    Le signal diagnostics_recus est émis depuis le fil de lecture, mais
    Qt achemine le signal sur le fil principal via la connexion par file d'attente."""

    diagnostics_recus = pyqtSignal(list)

    def __init__(self, etape, parent=None):
        super().__init__(parent)
        self._etape = etape
        self._processus = None
        self._dossier_tmp: Path | None = None
        self._uri: str = ""
        self._arret = False
        self._pret = threading.Event()
        self._verrou_stdin = threading.Lock()
        self._id_seq = 0
        self._doc_version = 0

    # --- interface publique (fil principal) ---------------------------------

    def demarrer(self, code: str) -> None:
        """Lance le fil de lecture. Le handshake LSP et l'ouverture du document
        se font dans run(), donc cette méthode retourne immédiatement."""
        self._code_initial = code
        self.start()

    def notifier_changement(self, code: str) -> None:
        """Envoie un textDocument/didChange à clangd.

        Sans effet si clangd n'est pas encore prêt ou si l'arrêt est demandé."""
        if self._arret or not self._pret.is_set() or not self._processus:
            return
        self._doc_version += 1
        self._ecrire({
            "jsonrpc": "2.0",
            "method": "textDocument/didChange",
            "params": {
                "textDocument": {"uri": self._uri, "version": self._doc_version},
                "contentChanges": [{"text": code}],
            },
        })

    def arreter(self) -> None:
        """Demande l'arrêt propre : shutdown/exit LSP, puis termine le processus."""
        self._arret = True
        if self._processus:
            try:
                self._ecrire({
                    "jsonrpc": "2.0",
                    "id": self._prochain_id(),
                    "method": "shutdown",
                    "params": {},
                })
                self._ecrire({"jsonrpc": "2.0", "method": "exit"})
            except Exception:
                pass
            self._processus.terminate()

    # --- fil de lecture (run) -----------------------------------------------

    def run(self) -> None:
        """Point d'entrée du fil : crée le dossier temporaire, lance clangd,
        fait le handshake, puis entre dans la boucle de lecture."""
        dossier_tmp = Path(tempfile.mkdtemp(prefix="atelier_lsp_"))
        self._dossier_tmp = dossier_tmp
        try:
            self._lancer_et_boucler(dossier_tmp)
        finally:
            self._nettoyer_processus()
            shutil.rmtree(dossier_tmp, ignore_errors=True)

    def _nettoyer_processus(self) -> None:
        """Ferme les pipes et attend la fin du processus clangd, sans laisser de flux ouvert."""
        proc = self._processus
        self._processus = None
        if proc is None:
            return
        if proc.poll() is None:
            proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        for flux in (proc.stdin, proc.stdout):
            try:
                if flux is not None:
                    flux.close()
            except Exception:
                pass

    def _lancer_et_boucler(self, dossier: Path) -> None:
        fichier_c = dossier / "atelier.c"
        fichier_c.write_text(self._code_initial, encoding="utf-8")

        flags = flags_pour_etape(self._etape)
        (dossier / "compile_flags.txt").write_text(
            "\n".join(flags) + "\n", encoding="utf-8"
        )

        self._processus = subprocess.Popen(
            ["clangd", "--log=error"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=str(dossier),
        )

        self._uri = fichier_c.as_uri()

        # Handshake : initialize
        self._ecrire({
            "jsonrpc": "2.0",
            "id": self._prochain_id(),
            "method": "initialize",
            "params": {
                "processId": None,
                "rootUri": None,
                "capabilities": {},
            },
        })
        self._lire_une_reponse()  # on attend la réponse avant d'envoyer initialized

        self._ecrire({"jsonrpc": "2.0", "method": "initialized", "params": {}})

        # didOpen : envoie le code initial
        self._doc_version += 1
        self._ecrire({
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {
                "textDocument": {
                    "uri": self._uri,
                    "languageId": "c",
                    "version": self._doc_version,
                    "text": self._code_initial,
                }
            },
        })

        self._pret.set()  # notifier_changement peut maintenant écrire

        # Boucle de lecture des notifications
        while not self._arret:
            msg = self._lire_une_reponse()
            if msg is None:
                break
            if msg.get("method") == "textDocument/publishDiagnostics":
                self.diagnostics_recus.emit(extraire_diagnostics(msg))

    def _lire_une_reponse(self) -> dict | None:
        """Lit exactement un message LSP depuis stdout de clangd.

        Renvoie None si le flux est fermé ou si le message est malformé."""
        if not self._processus:
            return None
        en_tete = b""
        while True:
            try:
                ch = self._processus.stdout.read(1)
            except Exception:
                return None
            if not ch:
                return None
            en_tete += ch
            if en_tete.endswith(b"\r\n\r\n"):
                break

        longueur = None
        for ligne in en_tete.decode("ascii", errors="replace").splitlines():
            if ligne.lower().startswith("content-length:"):
                try:
                    longueur = int(ligne.split(":", 1)[1].strip())
                except ValueError:
                    pass
        if longueur is None:
            return None

        try:
            corps = self._processus.stdout.read(longueur)
        except Exception:
            return None
        try:
            return json.loads(corps)
        except json.JSONDecodeError:
            return None

    # --- utilitaires privés -------------------------------------------------

    def _prochain_id(self) -> int:
        self._id_seq += 1
        return self._id_seq

    def _ecrire(self, obj: dict) -> None:
        """Écrit un message LSP sur stdin de clangd. Thread-safe grâce au verrou."""
        if not self._processus:
            return
        data = encadrer_message(obj)
        with self._verrou_stdin:
            try:
                self._processus.stdin.write(data)
                self._processus.stdin.flush()
            except Exception:
                pass
