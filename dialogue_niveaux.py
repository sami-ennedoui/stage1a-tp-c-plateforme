"""Boîtes de dialogue du mode auteur : gérer les niveaux d'un parcours.

Couche PyQt6 mince au-dessus de gestion_niveaux.py, qui fait tout le travail sur les
fichiers. Ouverte depuis le menu Paramètres de la fenêtre, une fois le mot de passe
auteur validé (voir auteur.py et fenetre.py).
"""
from pathlib import Path

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QListWidget,
                             QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox,
                             QPlainTextEdit, QDialogButtonBox, QMessageBox, QTabWidget,
                             QInputDialog)
from PyQt6.QtGui import QFont

import gestion_niveaux


def _police_code() -> QFont:
    police = QFont()
    police.setFamilies(["JetBrains Mono", "Fira Code", "DejaVu Sans Mono", "monospace"])
    police.setStyleHint(QFont.StyleHint.Monospace)
    police.setPointSize(11)
    return police


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


class DialogueEdition(QDialog):
    """Édite le contenu d'un niveau : énoncé, starter, corrigé, titre et sortie attendue.

    Écrit directement dans les fichiers du dossier du niveau, sans passer par
    l'Explorateur. Le titre et la sortie attendue vivent dans meta.json."""

    def __init__(self, dossier_parcours, ident: str, parent=None):
        super().__init__(parent)
        self.dossier = dossier_parcours
        self.ident = ident
        self.setWindowTitle(f"Modifier le niveau « {ident} »")
        self.setModal(True)
        self.resize(720, 560)

        meta = gestion_niveaux.lire_meta(dossier_parcours, ident)
        self.champ_titre = QLineEdit(meta.get("titre", ""))
        self.champ_sortie = QPlainTextEdit(
            "\n".join(meta.get("sortie_attendue") or []))
        self.champ_sortie.setFixedHeight(90)
        self.champ_sortie.setFont(_police_code())

        entete = QFormLayout()
        entete.addRow("Titre", self.champ_titre)
        entete.addRow("Sortie attendue", self.champ_sortie)

        # un onglet par fichier texte du niveau
        self.editeurs = {}
        onglets = QTabWidget()
        for nom in gestion_niveaux.FICHIERS_TEXTE:
            edit = QPlainTextEdit(
                gestion_niveaux.lire_fichier_niveau(dossier_parcours, ident, nom))
            edit.setFont(_police_code())
            self.editeurs[nom] = edit
            onglets.addTab(edit, nom)

        boutons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        boutons.accepted.connect(self._enregistrer)
        boutons.rejected.connect(self.reject)

        racine = QVBoxLayout(self)
        racine.addLayout(entete)
        racine.addWidget(onglets, 1)
        racine.addWidget(boutons)

    def _enregistrer(self):
        try:
            for nom, edit in self.editeurs.items():
                gestion_niveaux.ecrire_fichier_niveau(
                    self.dossier, self.ident, nom, edit.toPlainText())
            meta = gestion_niveaux.lire_meta(self.dossier, self.ident)
            meta["titre"] = self.champ_titre.text().strip() or meta.get("titre", "")
            meta["sortie_attendue"] = [
                l.strip() for l in self.champ_sortie.toPlainText().splitlines() if l.strip()]
            gestion_niveaux.ecrire_meta(self.dossier, self.ident, meta)
        except (ValueError, OSError) as e:
            QMessageBox.warning(self, "Enregistrement impossible", str(e))
            return
        self.accept()


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
        b_modifier = QPushButton("Modifier…")
        b_retirer = QPushButton("Retirer")
        b_monter = QPushButton("Monter")
        b_descendre = QPushButton("Descendre")
        b_detaches = QPushButton("Détachés…")
        b_ajouter.clicked.connect(self._ajouter)
        b_modifier.clicked.connect(self._modifier)
        b_retirer.clicked.connect(self._retirer)
        b_monter.clicked.connect(lambda: self._deplacer(-1))
        b_descendre.clicked.connect(lambda: self._deplacer(1))
        b_detaches.clicked.connect(self._reattacher)

        colonne = QVBoxLayout()
        for b in (b_ajouter, b_modifier, b_retirer, b_monter, b_descendre):
            colonne.addWidget(b)
        colonne.addStretch(1)
        colonne.addWidget(b_detaches)

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
        ident = v["ident"].strip()
        editer = QMessageBox.question(
            self, "Niveau créé",
            f"Le niveau « {ident} » a été créé.\n\n"
            "L'éditer maintenant (énoncé, starter, corrigé) ?")
        if editer == QMessageBox.StandardButton.Yes:
            DialogueEdition(self.dossier, ident, self).exec()

    def _modifier(self):
        ident = self._selection()
        if ident is None:
            return
        DialogueEdition(self.dossier, ident, self).exec()

    def _reattacher(self):
        detaches = gestion_niveaux.dossiers_detaches(self.dossier)
        if not detaches:
            QMessageBox.information(
                self, "Aucun niveau détaché",
                "Aucun dossier de niveau détaché du parcours pour le moment.")
            return
        ident, ok = QInputDialog.getItem(
            self, "Réattacher un niveau", "Niveau détaché à remettre :",
            detaches, 0, editable=False)
        if not ok or not ident:
            return
        try:
            gestion_niveaux.reattacher_niveau(self.dossier, ident)
        except ValueError as e:
            QMessageBox.warning(self, "Réattachement impossible", str(e))
            return
        self._rafraichir()

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
