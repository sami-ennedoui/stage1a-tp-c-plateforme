"""Boîtes de dialogue du mode auteur : gérer les niveaux d'un parcours.

Couche PyQt6 mince au-dessus de gestion_niveaux.py, qui fait tout le travail sur les
fichiers. Ouverte depuis le menu Paramètres de la fenêtre, une fois le mot de passe
auteur validé (voir auteur.py et fenetre.py).
"""
from pathlib import Path

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QListWidget,
                             QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox,
                             QPlainTextEdit, QDialogButtonBox, QMessageBox)

import gestion_niveaux


class DialogueAjout(QDialog):
    """Formulaire de création d'un niveau. Renvoie les champs saisis via .valeurs()."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un niveau")
        self.setModal(True)

        self.champ_id = QLineEdit()
        self.champ_id.setPlaceholderText("ex14_boucles")
        self.champ_titre = QLineEdit()
        self.champ_titre.setPlaceholderText("Exercice 14, les boucles")
        self.champ_mode = QComboBox()
        self.champ_mode.addItems(gestion_niveaux.MODES)
        self.champ_fichier = QLineEdit("programme.c")
        self.champ_cran = QSpinBox()
        self.champ_cran.setRange(0, 3)
        self.champ_cran.setValue(1)
        self.champ_noeud = QLineEdit()
        self.champ_noeud.setPlaceholderText("Exercice 14 du BE C, slides 30 à 32")
        self.champ_sortie = QPlainTextEdit()
        self.champ_sortie.setPlaceholderText("Une ligne par fragment attendu dans la sortie.")
        self.champ_sortie.setFixedHeight(90)

        form = QFormLayout()
        form.addRow("Identifiant", self.champ_id)
        form.addRow("Titre", self.champ_titre)
        form.addRow("Mode", self.champ_mode)
        form.addRow("Fichier édité", self.champ_fichier)
        form.addRow("Cran débloqué", self.champ_cran)
        form.addRow("Nœud de cours", self.champ_noeud)
        form.addRow("Sortie attendue", self.champ_sortie)

        boutons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        boutons.accepted.connect(self.accept)
        boutons.rejected.connect(self.reject)

        racine = QVBoxLayout(self)
        racine.addLayout(form)
        racine.addWidget(boutons)

    def valeurs(self) -> dict:
        sortie = [l.strip() for l in self.champ_sortie.toPlainText().splitlines() if l.strip()]
        return {
            "ident": self.champ_id.text(),
            "titre": self.champ_titre.text(),
            "mode": self.champ_mode.currentText(),
            "fichier_edite": self.champ_fichier.text().strip() or "programme.c",
            "cran_debloque": self.champ_cran.value(),
            "noeud_cours": self.champ_noeud.text().strip(),
            "sortie_attendue": sortie,
        }


class DialogueNiveaux(QDialog):
    """Gestionnaire des niveaux d'un parcours : ajouter, retirer, réordonner."""

    def __init__(self, dossier_parcours: Path, parent=None):
        super().__init__(parent)
        self.dossier = dossier_parcours
        self.setWindowTitle(f"Gérer les niveaux, parcours « {dossier_parcours.name} »")
        self.setModal(True)
        self.resize(560, 440)

        self.liste = QListWidget()

        b_ajouter = QPushButton("Ajouter…")
        b_retirer = QPushButton("Retirer")
        b_monter = QPushButton("Monter")
        b_descendre = QPushButton("Descendre")
        b_ajouter.clicked.connect(self._ajouter)
        b_retirer.clicked.connect(self._retirer)
        b_monter.clicked.connect(lambda: self._deplacer(-1))
        b_descendre.clicked.connect(lambda: self._deplacer(1))

        colonne = QVBoxLayout()
        for b in (b_ajouter, b_retirer, b_monter, b_descendre):
            colonne.addWidget(b)
        colonne.addStretch(1)

        milieu = QHBoxLayout()
        milieu.addWidget(self.liste, 1)
        milieu.addLayout(colonne)

        self.info = QLabel("Retirer détache le niveau du parcours ; son dossier reste sur le disque.")
        self.info.setWordWrap(True)

        fermeture = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        fermeture.rejected.connect(self.reject)
        fermeture.accepted.connect(self.accept)

        racine = QVBoxLayout(self)
        racine.addWidget(QLabel("Niveaux actifs, dans l'ordre du parcours :"))
        racine.addLayout(milieu, 1)
        racine.addWidget(self.info)
        racine.addWidget(fermeture)

        self._rafraichir()

    def _rafraichir(self):
        self.liste.clear()
        self.liste.addItems(gestion_niveaux.lister_niveaux(self.dossier))

    def _selection(self) -> str | None:
        item = self.liste.currentItem()
        return item.text() if item is not None else None

    def _ajouter(self):
        form = DialogueAjout(self)
        if form.exec() != QDialog.DialogCode.Accepted:
            return
        v = form.valeurs()
        try:
            gestion_niveaux.ajouter_niveau(
                self.dossier, v["ident"], v["titre"],
                mode=v["mode"], cran_debloque=v["cran_debloque"],
                noeud_cours=v["noeud_cours"], fichier_edite=v["fichier_edite"],
                sortie_attendue=v["sortie_attendue"])
        except ValueError as e:
            QMessageBox.warning(self, "Ajout impossible", str(e))
            return
        self._rafraichir()
        QMessageBox.information(
            self, "Niveau créé",
            f"Le niveau « {v['ident'].strip()} » a été créé.\n\n"
            "Édite enonce.md, starter.c et corrige.c dans son dossier pour le remplir.")

    def _retirer(self):
        ident = self._selection()
        if ident is None:
            return
        reponse = QMessageBox.question(
            self, "Retirer le niveau",
            f"Détacher « {ident} » du parcours ?\n\n"
            "Le dossier n'est pas effacé, tu pourras le remettre plus tard.")
        if reponse != QMessageBox.StandardButton.Yes:
            return
        try:
            gestion_niveaux.retirer_niveau(self.dossier, ident)
        except ValueError as e:
            QMessageBox.warning(self, "Retrait impossible", str(e))
            return
        self._rafraichir()

    def _deplacer(self, delta: int):
        ident = self._selection()
        if ident is None:
            return
        try:
            gestion_niveaux.deplacer_niveau(self.dossier, ident, delta)
        except ValueError as e:
            QMessageBox.warning(self, "Déplacement impossible", str(e))
            return
        self._rafraichir()
        # garde la sélection sur le niveau déplacé
        for i in range(self.liste.count()):
            if self.liste.item(i).text() == ident:
                self.liste.setCurrentRow(i)
                break
