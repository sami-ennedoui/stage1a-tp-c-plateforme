"""Coloration syntaxique du C pour l'éditeur. Purement lexicale, à base
d'expressions régulières via QSyntaxHighlighter. Aucun processus externe, donc
robuste et instantané. Les couleurs restent dans le ton du thème nuit."""
import re

from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat

_MOTCLE = "#bb9af7"     # mots-clés de contrôle
_TYPE = "#2ac3de"       # types
_CHAINE = "#9ece6a"     # chaînes et caractères
_COMMENT = "#565f89"    # commentaires
_NOMBRE = "#ff9e64"     # nombres
_PREPRO = "#7dcfff"     # directives préprocesseur
_CONST = "#e0af68"      # constantes EN_MAJUSCULES
_FONCTION = "#7aa2f7"   # appels de fonction

_MOTS = ["if", "else", "while", "for", "do", "switch", "case", "default", "break",
         "continue", "return", "goto", "sizeof", "typedef", "struct", "union",
         "enum", "const", "static", "extern", "volatile", "register", "inline"]
_TYPES = ["void", "int", "char", "short", "long", "float", "double", "unsigned",
          "signed", "bool", "size_t", "FILE"]


def _format(couleur: str, gras: bool = False, italique: bool = False) -> QTextCharFormat:
    f = QTextCharFormat()
    f.setForeground(QColor(couleur))
    if gras:
        f.setFontWeight(QFont.Weight.Bold)
    if italique:
        f.setFontItalic(True)
    return f


class ColorationC(QSyntaxHighlighter):
    """À brancher sur un QTextDocument. Colore mots-clés, types, constantes,
    fonctions, nombres, chaînes, directives et commentaires (y compris bloc)."""

    def __init__(self, document):
        super().__init__(document)
        self._f_chaine = _format(_CHAINE)
        self._f_comment = _format(_COMMENT, italique=True)
        mot = lambda l: r"\b(" + "|".join(l) + r")\b"
        # ordre voulu : les règles plus tardives écrasent les plus précoces
        self._regles = [
            (re.compile(r"^\s*#.*"), _format(_PREPRO)),                 # préprocesseur
            (re.compile(r"\b([A-Za-z_]\w*)\s*(?=\()"), _format(_FONCTION)),  # appel f(
            (re.compile(r"\b[A-Z][A-Z0-9_]+\b"), _format(_CONST)),     # CONSTANTES
            (re.compile(r"\b\d+(\.\d+)?[fFuUlL]*\b"), _format(_NOMBRE)),  # nombres
            (re.compile(mot(_TYPES)), _format(_TYPE)),                  # types
            (re.compile(mot(_MOTS)), _format(_MOTCLE, gras=True)),      # mots-clés (gagnent)
        ]
        self._chaine = re.compile(r'"(\\.|[^"\\])*"|\'(\\.|[^\'\\])*\'')
        self._ligne = re.compile(r"//.*")
        self._bloc_ouvre = "/*"
        self._bloc_ferme = "*/"

    def highlightBlock(self, text: str | None) -> None:
        if not text:
            return
        for regex, fmt in self._regles:
            for m in regex.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)
        for m in self._chaine.finditer(text):            # chaînes par-dessus le code
            self.setFormat(m.start(), m.end() - m.start(), self._f_chaine)
        m = self._ligne.search(text)                     # commentaire de fin de ligne
        if m:
            self.setFormat(m.start(), len(text) - m.start(), self._f_comment)
        self._colorer_bloc(text)                         # commentaire bloc, gagne toujours

    def _colorer_bloc(self, texte: str) -> None:
        """Gère les /* ... */ qui s'étendent sur plusieurs lignes via l'état de bloc."""
        self.setCurrentBlockState(0)
        if self.previousBlockState() == 1:
            debut = 0
        else:
            debut = texte.find(self._bloc_ouvre)
        while debut >= 0:
            fin = texte.find(self._bloc_ferme, debut)
            if fin == -1:
                self.setCurrentBlockState(1)
                longueur = len(texte) - debut
            else:
                longueur = fin - debut + len(self._bloc_ferme)
            self.setFormat(debut, longueur, self._f_comment)
            debut = texte.find(self._bloc_ouvre, debut + longueur)
