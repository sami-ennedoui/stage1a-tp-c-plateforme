"""Fenêtre « Emplacements et diagnostic », version graphique de diagnostic.bat.

Montre les chemins clés et l'état présent/absent des outils (gcc, clangd, claude),
chacun avec un bouton pour ouvrir le dossier. Couche PyQt6 mince au-dessus de
diagnostic.py, qui fait toute la détection.
"""
from pathlib import Path

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLabel,
                             QPushButton, QDialogButtonBox, QMessageBox, QFrame)
from PyQt6.QtCore import Qt

import diagnostic
import theme


def _ligne_separateur() -> QFrame:
    trait = QFrame()
    trait.setFrameShape(QFrame.Shape.HLine)
    return trait


class DialogueDiagnostic(QDialog):
    def __init__(self, parcours_nom: str, chemin_atelier_bat: Path, parent=None):
        super().__init__(parent)
        self.parcours_nom = parcours_nom
        self.chemin_atelier_bat = chemin_atelier_bat
        self.setWindowTitle("Emplacements et diagnostic")
        self.setModal(True)
        self.resize(640, 460)

        racine = QVBoxLayout(self)

        racine.addWidget(QLabel("Emplacements clés"))
        grille_chemins = QGridLayout()
        for i, (libelle, chemin) in enumerate(diagnostic.chemins_cles(parcours_nom)):
            grille_chemins.addWidget(QLabel(libelle), i, 0)
            valeur = QLabel(str(chemin))
            valeur.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            grille_chemins.addWidget(valeur, i, 1)
            bouton = QPushButton("Ouvrir le dossier")
            bouton.clicked.connect(lambda _, c=chemin: self._ouvrir(c))
            grille_chemins.addWidget(bouton, i, 2)
        racine.addLayout(grille_chemins)

        racine.addWidget(_ligne_separateur())

        racine.addWidget(QLabel("Outils"))
        grille_outils = QGridLayout()
        for i, (nom, chemin) in enumerate(diagnostic.outils()):
            grille_outils.addWidget(QLabel(nom), i, 0)
            present = chemin is not None
            etat = QLabel("présent" if present else "absent")
            etat.setStyleSheet(
                f"color:{theme.ACCENT if present else theme.ROUGE};font-weight:bold;")
            grille_outils.addWidget(etat, i, 1)
            grille_outils.addWidget(QLabel(str(chemin) if present else ""), i, 2)
            if present:
                bouton = QPushButton("Ouvrir le dossier")
                bouton.clicked.connect(lambda _, c=chemin: self._ouvrir(c))
                grille_outils.addWidget(bouton, i, 3)
        racine.addLayout(grille_outils)

        rappel = QLabel(
            "gcc est nécessaire pour compiler et ouvrir les portes. clangd (diagnostics "
            "live) et claude (tuteur IA) sont optionnels : l'appli marche sans eux.")
        rappel.setWordWrap(True)
        racine.addWidget(rappel)

        racine.addStretch(1)

        b_raccourci = QPushButton("Créer un raccourci sur le bureau")
        b_raccourci.clicked.connect(self._creer_raccourci)
        racine.addWidget(b_raccourci)

        fermeture = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        fermeture.rejected.connect(self.reject)
        fermeture.accepted.connect(self.accept)
        racine.addWidget(fermeture)

    def _ouvrir(self, chemin: Path):
        try:
            diagnostic.ouvrir_dossier(chemin)
        except OSError as e:
            QMessageBox.warning(self, "Ouverture impossible", str(e))

    def _creer_raccourci(self):
        if not self.chemin_atelier_bat.exists():
            QMessageBox.warning(
                self, "Lanceur introuvable",
                f"Atelier.bat est introuvable ({self.chemin_atelier_bat}).")
            return
        try:
            cible = _creer_raccourci_bureau(self.chemin_atelier_bat)
        except OSError as e:
            QMessageBox.warning(self, "Raccourci non créé", str(e))
            return
        QMessageBox.information(self, "Raccourci créé",
                                f"Raccourci créé sur le bureau :\n{cible}")


def _creer_raccourci_bureau(cible_bat: Path) -> Path:
    """Crée un .lnk « Atelier TP C » sur le bureau, pointant vers Atelier.bat.

    Passe par WScript.Shell (COM), disponible d'origine sous Windows."""
    import os
    bureau = Path(os.path.join(os.environ["USERPROFILE"], "Desktop"))
    lien = bureau / "Atelier TP C.lnk"
    ps = (
        "$s = New-Object -ComObject WScript.Shell; "
        f"$r = $s.CreateShortcut('{lien}'); "
        f"$r.TargetPath = '{cible_bat}'; "
        f"$r.WorkingDirectory = '{cible_bat.parent}'; "
        "$r.Save()"
    )
    import subprocess
    import chemins
    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                         capture_output=True, text=True,
                         encoding="utf-8", errors="replace",
                         creationflags=chemins.SANS_FENETRE)
    if res.returncode != 0:
        raise OSError(res.stderr.strip() or "Échec de la création du raccourci.")
    return lien
