"""Fenêtre de l'atelier Snake. Câble énoncé, éditeur, console, tuteur et portes."""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
                             QPlainTextEdit, QTextEdit, QPushButton, QLabel, QTabWidget,
                             QListWidgetItem, QInputDialog, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

import chemins
import executeur
import progression
import tuteur_ia
from modele_etape import charger_parcours


class FilTuteur(QThread):
    """Appel IA dans un fil séparé pour ne pas figer la fenêtre."""
    repondu = pyqtSignal(str)

    def __init__(self, etape, code, question, niveau):
        super().__init__()
        self._args = (etape, code, question, niveau)

    def run(self):
        self.repondu.emit(tuteur_ia.demander_aide(*self._args))


class Fenetre(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atelier Snake")
        self.parcours = charger_parcours(chemins.CONTENU)
        self.prog = progression.charger()
        self.etape = self.parcours[0]
        # cran restauré depuis l'état sauvegardé, l'étudiant qui revient garde son niveau
        self.niveau = progression.cran_disponible(self.prog)

        self.liste = QListWidget()
        self.liste.currentRowChanged.connect(self._changer_etape)

        self.enonce = QTextEdit(readOnly=True)
        self.editeur = QPlainTextEdit()
        self.editeur_test = QPlainTextEdit()
        self.onglets = QTabWidget()
        self.onglets.addTab(self.editeur, "Mon code")
        self.onglets.addTab(self.editeur_test, "Mon test")

        self.console = QTextEdit(readOnly=True)
        self.label_cran = QLabel()
        self.choix_cran = QComboBox()    # redescendre sous le cran débloqué pour moins d'aide
        self.choix_cran.currentIndexChanged.connect(self._changer_cran)
        self.reponse_tuteur = QTextEdit(readOnly=True)

        b_compiler = QPushButton("Compiler")
        b_tester = QPushButton("Tester")
        self.b_jeu = QPushButton("Lancer le jeu")
        b_aide = QPushButton("Demander de l'aide")
        b_compiler.clicked.connect(self._compiler)
        b_tester.clicked.connect(self._tester)
        self.b_jeu.clicked.connect(self._lancer_jeu)
        b_aide.clicked.connect(self._demander_aide)

        barre = QHBoxLayout()
        for b in (b_compiler, b_tester, self.b_jeu, b_aide):
            barre.addWidget(b)

        centre = QVBoxLayout()
        centre.addWidget(self.enonce, 2)
        centre.addWidget(self.onglets, 5)
        centre.addLayout(barre)
        centre.addWidget(self.console, 3)

        droite = QVBoxLayout()
        droite.addWidget(self.label_cran)
        droite.addWidget(self.choix_cran)
        droite.addWidget(self.reponse_tuteur)

        racine = QHBoxLayout()
        racine.addWidget(self.liste, 1)
        racine.addLayout(centre, 4)
        racine.addLayout(droite, 2)
        conteneur = QWidget()
        conteneur.setLayout(racine)
        self.setCentralWidget(conteneur)

        self._remplir_liste()
        self.liste.setCurrentRow(0)

    def _remplir_liste(self):
        self.liste.clear()
        for e in self.parcours:
            ouverte = progression.etape_deverrouillee(e, self.parcours, self.prog)
            faite = e.id in self.prog.etapes_faites
            marque = "[fait]" if faite else ("[ouvert]" if ouverte else "[verrou]")
            item = QListWidgetItem(f"{marque}  {e.titre}")
            if not ouverte:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.liste.addItem(item)

    def _changer_etape(self, ligne):
        if ligne < 0:
            return
        self.etape = self.parcours[ligne]
        self.enonce.setMarkdown((self.etape.dossier / "enonce.md").read_text(encoding="utf-8"))
        self.editeur.setPlainText((self.etape.dossier / "starter.c").read_text(encoding="utf-8"))
        self.editeur_test.setPlainText("")
        a_ecrire = self.etape.mode == "test_a_ecrire"
        self.onglets.setTabVisible(1, a_ecrire)
        self.b_jeu.setVisible(self.etape.type == "jalon")
        self._maj_cran()

    def _maj_cran(self):
        dispo = progression.cran_disponible(self.prog)
        if self.niveau > dispo:          # le plafond, jamais au-dessus du cran débloqué
            self.niveau = dispo
        self.choix_cran.blockSignals(True)
        self.choix_cran.clear()
        self.choix_cran.addItems([f"N{i}" for i in range(dispo + 1)])
        self.choix_cran.setCurrentIndex(self.niveau)
        self.choix_cran.blockSignals(False)
        self.label_cran.setText(f"Tuteur, cran courant N{self.niveau} sur N{dispo} débloqué")

    def _changer_cran(self, i):
        if i < 0:
            return
        self.niveau = i                  # l'étudiant choisit un cran <= ce qu'il a débloqué
        dispo = progression.cran_disponible(self.prog)
        self.label_cran.setText(f"Tuteur, cran courant N{self.niveau} sur N{dispo} débloqué")

    def _compiler(self):
        self.console.setPlainText("Compilation et exécution en cours…")
        self._tester()

    def _tester(self):
        code = self.editeur.toPlainText()
        if self.etape.mode == "test_fourni":
            r = executeur.porte_perso(self.etape, code)
            self._afficher_porte(r.ok, r.sortie)
        else:
            test = self.editeur_test.toPlainText()
            jug = executeur.juger_test(self.etape, test)
            if not jug.test_solide:
                self.console.setPlainText(
                    "Ton test n'est pas encore solide.\n" +
                    ("Il rejette un code correct.\n" if not jug.passe_corrige else "") +
                    ("Il laisse passer un bug, renforce-le.\n" if not jug.attrape_bug else "") +
                    "\n" + jug.sortie)
                return
            r = executeur.porte_jalon(self.etape, code, test)
            self._afficher_porte(r.ok, "Ton test est solide.\n" + r.sortie)

    def _afficher_porte(self, ok, sortie):
        self.console.setPlainText(("PORTE OUVERTE\n\n" if ok else "PORTE FERMÉE\n\n") + sortie)
        if ok:
            self.prog = progression.valider(self.etape, self.prog)
            progression.sauver(self.prog)
            self.niveau = progression.cran_disponible(self.prog)
            self._remplir_liste()
            self._maj_cran()

    def _lancer_jeu(self):
        r = executeur.lancer_jeu(self.etape, self.editeur.toPlainText())
        self.console.setPlainText(r.sortie)

    def _demander_aide(self):
        if getattr(self, "_fil", None) is not None and self._fil.isRunning():
            return                       # un appel tuteur déjà en cours, on ne le détruit pas
        question, ok = QInputDialog.getText(self, "Demander de l'aide", "Ta question :")
        if not ok or not question:
            return
        dispo = progression.cran_disponible(self.prog)
        niveau = min(self.niveau, dispo)
        self.reponse_tuteur.setPlainText("Le tuteur réfléchit…")
        self._fil = FilTuteur(self.etape, self.editeur.toPlainText(), question, niveau)
        self._fil.repondu.connect(self.reponse_tuteur.setPlainText)
        self._fil.start()


def construire(app):
    """Construit la fenêtre sans l'afficher. Sert au smoketest."""
    return Fenetre()
