"""Thème sombre de l'atelier. Une palette Fusion plus une feuille de style Qt.
On applique le tout sur la QApplication, donc les fenêtres et les dialogues suivent."""
from PyQt6.QtGui import QColor, QPalette

# Palette type « nuit », fond bleu très sombre, accent vert clin d'œil au Snake.
FOND = "#1a1b26"
FOND_PROFOND = "#16161e"
SURFACE = "#24283b"
SURFACE_HAUTE = "#2a2e42"
BORD = "#3b4261"
BORD_VIF = "#565f89"
TEXTE = "#c0caf5"
TEXTE_ATTENUE = "#787c99"
ACCENT = "#9ece6a"
ACCENT_CLAIR = "#b9f27c"
ACCENT_SOMBRE = "#7fb04f"
BLEU = "#7aa2f7"
ROUGE = "#f7768e"

QSS = f"""
QMainWindow, QWidget {{
    background-color: {FOND};
    color: {TEXTE};
    font-size: 13px;
}}
QLabel {{
    color: {TEXTE};
}}
QLabel#titre {{
    color: {BLEU};
    font-size: 10px;
    font-weight: bold;
    padding: 2px 0;
}}
QPushButton {{
    background-color: {SURFACE_HAUTE};
    color: {TEXTE};
    border: 1px solid {BORD};
    border-radius: 6px;
    padding: 8px 14px;
}}
QPushButton:hover {{
    background-color: #343a55;
    border-color: {BORD_VIF};
}}
QPushButton:pressed {{
    background-color: #222636;
}}
QPushButton:disabled {{
    color: {BORD_VIF};
    background-color: #20222e;
    border-color: {SURFACE_HAUTE};
}}
QPushButton#primaire {{
    background-color: {ACCENT};
    color: {FOND_PROFOND};
    border: none;
    font-weight: bold;
}}
QPushButton#primaire:hover {{
    background-color: {ACCENT_CLAIR};
}}
QPushButton#primaire:pressed {{
    background-color: {ACCENT_SOMBRE};
}}
QListWidget {{
    background-color: {FOND_PROFOND};
    border: 1px solid {SURFACE_HAUTE};
    border-radius: 8px;
    padding: 4px;
    outline: 0;
}}
QListWidget::item {{
    padding: 8px;
    border-radius: 6px;
    margin: 1px 0;
}}
QListWidget::item:hover {{
    background-color: #20222e;
}}
QListWidget::item:selected {{
    background-color: #2f334d;
    color: {TEXTE};
}}
QListWidget::item:disabled {{
    color: {BORD_VIF};
}}
QTabWidget::pane {{
    border: 1px solid {SURFACE_HAUTE};
    border-radius: 8px;
    top: -1px;
}}
QTabBar::tab {{
    background-color: {FOND_PROFOND};
    color: {TEXTE_ATTENUE};
    padding: 8px 16px;
    border: 1px solid {SURFACE_HAUTE};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {SURFACE};
    color: {ACCENT};
}}
QPlainTextEdit, QTextEdit {{
    background-color: {FOND_PROFOND};
    color: {TEXTE};
    border: 1px solid {SURFACE_HAUTE};
    border-radius: 8px;
    padding: 8px;
    selection-background-color: #33467c;
    selection-color: {TEXTE};
}}
QComboBox {{
    background-color: {SURFACE_HAUTE};
    color: {TEXTE};
    border: 1px solid {BORD};
    border-radius: 6px;
    padding: 6px 10px;
}}
QComboBox:hover {{
    border-color: {BORD_VIF};
}}
QComboBox::drop-down {{
    border: none;
    width: 18px;
}}
QComboBox QAbstractItemView {{
    background-color: {SURFACE};
    color: {TEXTE};
    border: 1px solid {BORD};
    selection-background-color: #2f334d;
    outline: 0;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORD};
    border-radius: 5px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {BORD_VIF};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {BORD};
    border-radius: 5px;
    min-width: 24px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
QDialog {{
    background-color: {FOND};
}}
"""


def _palette_sombre() -> QPalette:
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor(FOND))
    p.setColor(QPalette.ColorRole.WindowText, QColor(TEXTE))
    p.setColor(QPalette.ColorRole.Base, QColor(FOND_PROFOND))
    p.setColor(QPalette.ColorRole.AlternateBase, QColor(SURFACE))
    p.setColor(QPalette.ColorRole.Text, QColor(TEXTE))
    p.setColor(QPalette.ColorRole.Button, QColor(SURFACE_HAUTE))
    p.setColor(QPalette.ColorRole.ButtonText, QColor(TEXTE))
    p.setColor(QPalette.ColorRole.Highlight, QColor("#33467c"))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor(TEXTE))
    p.setColor(QPalette.ColorRole.ToolTipBase, QColor(SURFACE))
    p.setColor(QPalette.ColorRole.ToolTipText, QColor(TEXTE))
    p.setColor(QPalette.ColorRole.PlaceholderText, QColor(BORD_VIF))
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(BORD_VIF))
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(BORD_VIF))
    return p


def appliquer(app) -> None:
    """Pose le style Fusion, la palette sombre et la feuille de style sur l'appli."""
    app.setStyle("Fusion")
    app.setPalette(_palette_sombre())
    app.setStyleSheet(QSS)
