"""Fenêtre de l'atelier Snake. Câble énoncé, éditeur, console, tuteur et portes.
Deux parcours partagent ce moteur : 'hybride', des étapes isolées avec test à écrire,
et 'projet', où l'étudiant remplit la vraie structure du jeu jusqu'à pouvoir y jouer."""
import html
from pathlib import Path

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
                             QPlainTextEdit, QTextEdit, QPushButton, QLabel, QTabWidget,
                             QListWidgetItem, QInputDialog, QComboBox, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

import auteur
import chemins
import coloration
import diagnostic
import executeur
import lsp_clangd
import moodle_sync
import progression
import reglages
import tuteur_ia
import theme
from dialogue_diagnostic import DialogueDiagnostic
from dialogue_niveaux import DialogueNiveaux
from espace_projet import EspaceProjet
from modele_etape import charger_parcours_complet


def _titre(texte: str) -> QLabel:
    """Petit en-tête de colonne, stylé par la feuille de style via son objectName."""
    etiquette = QLabel(texte)
    etiquette.setObjectName("titre")
    return etiquette


class FilTuteur(QThread):
    """Appel IA dans un fil séparé pour ne pas figer la fenêtre."""
    repondu = pyqtSignal(str)

    def __init__(self, etape, code, question, niveau):
        super().__init__()
        self._args = (etape, code, question, niveau)

    def run(self):
        self.repondu.emit(tuteur_ia.demander_aide(*self._args))


class Fenetre(QMainWindow):
    def __init__(self, demo=False, parcours_nom="hybride"):
        super().__init__()
        self.demo = demo
        self.parcours_nom = parcours_nom
        parcours = charger_parcours_complet(chemins.contenu_racine(parcours_nom))
        self.mode = parcours.mode
        self.parcours = parcours.etapes

        titre = "Atelier Snake"
        if self.mode == "projet":
            titre += ", parcours projet"
        if demo:
            titre += " (mode démo)"
        self.setWindowTitle(titre)
        self._construire_menu()

        # parcours projet : une copie de travail vivante, remplie étape par étape.
        # On part du squelette à trous. En démo on repart propre à chaque lancement.
        self.espace = None
        self._etape_courante = None      # étape dont l'éditeur est affiché, pour la sauvegarde
        if self.mode == "projet":
            self.espace = EspaceProjet(chemins.PROJET_SQUELETTE, chemins.ESPACE_SESSION)
            if demo:
                self.espace.reinitialiser()
            else:
                self.espace.initialiser()

        if self.mode == "projet":
            # le travail persistant, c'est la copie de projet elle-même, pas un fichier d'état
            self.prog = progression.Progression([], 0)
        elif demo:
            # mode démo : tout débloqué, cran poussé à N3 pour tester les quatre niveaux d'IA
            self.prog = progression.Progression([e.id for e in self.parcours], 3)
        else:
            self.prog = progression.charger()
        self.etape = self.parcours[0]
        # cran restauré depuis l'état sauvegardé, l'étudiant qui revient garde son niveau
        self.niveau = 0 if self.mode == "projet" else progression.cran_disponible(self.prog)

        self.liste = QListWidget()
        self.liste.currentRowChanged.connect(self._changer_etape)

        self.enonce = QTextEdit(readOnly=True)
        self.editeur = QPlainTextEdit()
        self.editeur_test = QPlainTextEdit()
        self.onglets = QTabWidget()
        self.onglets.addTab(self.editeur, "Mon code")
        self.onglets.addTab(self.editeur_test, "Mon test")

        self.console = QTextEdit(readOnly=True)

        # police à chasse fixe pour tout ce qui contient du code
        police_code = QFont()
        police_code.setFamilies(["JetBrains Mono", "Fira Code", "DejaVu Sans Mono", "monospace"])
        police_code.setStyleHint(QFont.StyleHint.Monospace)
        police_code.setPointSize(11)
        for edit in (self.editeur, self.editeur_test, self.console):
            edit.setFont(police_code)
        for edit in (self.editeur, self.editeur_test):
            edit.setTabStopDistance(4 * edit.fontMetrics().horizontalAdvance(" "))

        # coloration syntaxique C, gardée en attribut pour ne pas être ramassée
        self._color_code = coloration.ColorationC(self.editeur.document())
        self._color_test = coloration.ColorationC(self.editeur_test.document())

        # diagnostics LSP clangd, désactivés proprement si clangd est absent
        self._client_lsp: lsp_clangd.ClientClangd | None = None
        self._timer_lsp = QTimer(self)
        self._timer_lsp.setSingleShot(True)
        self._timer_lsp.setInterval(400)
        self._timer_lsp.timeout.connect(self._envoyer_code_a_clangd)
        self.label_lsp = QLabel()
        self.label_lsp.setVisible(False)
        self.label_lsp.setObjectName("avertissement_lsp")
        if self.mode != "projet" and not lsp_clangd.clangd_disponible():
            self.label_lsp.setText(
                "clangd absent, diagnostics live indisponibles. Installe clang-tools-extra."
            )
            self.label_lsp.setVisible(True)
        self.label_cran = QLabel()
        self.choix_cran = QComboBox()    # redescendre sous le cran débloqué pour moins d'aide
        self.choix_cran.currentIndexChanged.connect(self._changer_cran)
        self.reponse_tuteur = QTextEdit(readOnly=True)

        b_compiler = QPushButton("Compiler")
        b_tester = QPushButton("Tester")
        b_tester.setObjectName("primaire")     # bouton d'action principal, accent vert
        self.b_jeu = QPushButton("Compiler et jouer" if self.mode == "projet" else "Lancer le jeu")
        b_aide = QPushButton("Demander de l'aide")
        self.b_corrige = QPushButton("Charger le corrigé")
        self.b_corrige.setVisible(self.demo)     # bouton du mode démo seulement
        b_compiler.clicked.connect(self._compiler)
        b_tester.clicked.connect(self._tester)
        self.b_jeu.clicked.connect(self._lancer_jeu)
        b_aide.clicked.connect(self._demander_aide)
        self.b_corrige.clicked.connect(self._charger_corrige)

        barre = QHBoxLayout()
        barre.setSpacing(8)
        for b in (b_compiler, b_tester, self.b_jeu, b_aide, self.b_corrige):
            barre.addWidget(b)
        barre.addStretch(1)

        gauche = QVBoxLayout()
        gauche.setSpacing(6)
        gauche.addWidget(_titre("PARCOURS"))
        gauche.addWidget(self.liste)
        self.b_moodle = QPushButton()
        if chemins.ATELIER_SUIVI == "local":
            # mode local : indicateur non cliquable, pas de proposition de connexion
            self.b_moodle.setEnabled(False)
            self._maj_indicateur_local()
        else:
            self.b_moodle.setText("Connecté à Moodle" if moodle_sync.actif()
                                  else "Connecter à Moodle")
            self.b_moodle.clicked.connect(self._connecter_moodle)
        gauche.addWidget(self.b_moodle)

        centre = QVBoxLayout()
        centre.setSpacing(6)
        centre.addWidget(_titre("ÉNONCÉ"))
        centre.addWidget(self.enonce, 2)
        centre.addWidget(_titre("ATELIER"))
        centre.addWidget(self.onglets, 5)
        centre.addWidget(self.label_lsp)
        centre.addLayout(barre)
        centre.addWidget(_titre("CONSOLE"))
        centre.addWidget(self.console, 3)

        droite = QVBoxLayout()
        droite.setSpacing(6)
        droite.addWidget(_titre("TUTEUR IA"))
        droite.addWidget(self.label_cran)
        droite.addWidget(self.choix_cran)
        droite.addWidget(self.reponse_tuteur)

        racine = QHBoxLayout()
        racine.setContentsMargins(14, 14, 14, 14)
        racine.setSpacing(14)
        racine.addLayout(gauche, 1)
        racine.addLayout(centre, 4)
        racine.addLayout(droite, 2)
        conteneur = QWidget()
        conteneur.setLayout(racine)
        self.setCentralWidget(conteneur)

        # anti-rebond : textChanged déclenche le timer, pas l'envoi direct
        self.editeur.textChanged.connect(self._timer_lsp.start)

        self._remplir_liste()
        self.liste.setCurrentRow(0)
        if chemins.ATELIER_SUIVI == "moodle":
            ancienne = moodle_sync.desaccord_url()
            if ancienne:
                print(
                    f"Attention : l'appairage Moodle enregistré vise {ancienne}, "
                    f"l'atelier pointe maintenant vers {chemins.COMPAGNON_URL}. "
                    "Reclique l'activité dans Moodle pour te réappairer."
                )
            moodle_sync.rejouer()
            # Rafraîchit périodiquement le libellé du bouton avec le score Moodle,
            # que le compagnon renvoie de façon asynchrone après chaque envoi.
            self._timer_moodle = QTimer(self)
            self._timer_moodle.setInterval(1500)
            self._timer_moodle.timeout.connect(self._maj_moodle)
            self._timer_moodle.start()

    def _construire_menu(self):
        """Menu Paramètres : navigation, dossiers, diagnostic, et édition protégée."""
        menu = self.menuBar().addMenu("Paramètres")
        menu.addAction("Changer de parcours…").triggered.connect(self._changer_parcours)
        menu.addAction("Ouvrir le dossier du contenu").triggered.connect(
            self._ouvrir_dossier_contenu)
        menu.addAction("Emplacements et diagnostic…").triggered.connect(
            self._ouvrir_diagnostic)
        menu.addSeparator()
        menu.addAction("Gérer les niveaux…").triggered.connect(self._ouvrir_gestion_niveaux)
        menu.addAction("Changer le mot de passe auteur…").triggered.connect(
            self._changer_mot_de_passe)

    def _changer_parcours(self):
        noms = diagnostic.parcours_disponibles()
        if not noms:
            QMessageBox.warning(self, "Aucun parcours",
                                "Aucun dossier de contenu avec un parcours.json.")
            return
        depart = noms.index(self.parcours_nom) if self.parcours_nom in noms else 0
        choix, ok = QInputDialog.getItem(
            self, "Changer de parcours", "Parcours :", noms, depart, editable=False)
        if not ok or not choix or choix == self.parcours_nom:
            return
        reglages.definir_parcours(choix)
        QMessageBox.information(
            self, "Parcours enregistré",
            f"Le parcours « {choix} » s'ouvrira au prochain lancement.\n"
            "Ferme puis relance l'appli pour basculer dessus.")

    def _ouvrir_dossier_contenu(self):
        try:
            diagnostic.ouvrir_dossier(chemins.contenu_racine(self.parcours_nom))
        except OSError as e:
            QMessageBox.warning(self, "Ouverture impossible", str(e))

    def _ouvrir_diagnostic(self):
        DialogueDiagnostic(self.parcours_nom, chemins.RACINE / "Atelier.bat", self).exec()

    def _demander_mot_de_passe(self) -> bool:
        """Demande le mot de passe auteur. Vrai s'il est correct."""
        saisi, ok = QInputDialog.getText(
            self, "Mode auteur", "Mot de passe pour modifier le contenu :",
            QLineEdit.EchoMode.Password)
        if not ok:
            return False
        if not auteur.verifier(saisi):
            QMessageBox.warning(self, "Accès refusé", "Mot de passe incorrect.")
            return False
        return True

    def _ouvrir_gestion_niveaux(self):
        if self.mode == "projet":
            QMessageBox.information(
                self, "Indisponible",
                "La gestion des niveaux ne concerne que les parcours isolés, "
                "pas le parcours projet.")
            return
        if not self._demander_mot_de_passe():
            return
        dlg = DialogueNiveaux(chemins.contenu_racine(self.parcours_nom), self)
        dlg.exec()
        self._recharger_parcours()

    def _changer_mot_de_passe(self):
        if not self._demander_mot_de_passe():
            return
        nouveau, ok = QInputDialog.getText(
            self, "Changer le mot de passe", "Nouveau mot de passe :",
            QLineEdit.EchoMode.Password)
        if not ok or not nouveau:
            return
        auteur.definir(nouveau)
        QMessageBox.information(self, "Mot de passe changé",
                                "Le nouveau mot de passe auteur est enregistré.")

    def _recharger_parcours(self):
        """Recharge le parcours depuis le disque après une édition du contenu."""
        parcours = charger_parcours_complet(chemins.contenu_racine(self.parcours_nom))
        self.parcours = parcours.etapes
        if not self.parcours:
            self.liste.clear()
            return
        self._remplir_liste()
        ligne = min(self.liste.currentRow(), len(self.parcours) - 1)
        self.liste.setCurrentRow(max(0, ligne))

    def _remplir_liste(self):
        self.liste.clear()
        for e in self.parcours:
            faite = e.id in self.prog.etapes_faites
            if self.mode == "projet":
                # parcours projet : on travaille sur la vraie structure, tout est ouvert
                ouverte = True
                marque = "[fait]" if faite else "[à faire]"
            else:
                ouverte = progression.etape_deverrouillee(e, self.parcours, self.prog)
                marque = "[fait]" if faite else ("[ouvert]" if ouverte else "[verrou]")
            item = QListWidgetItem(f"{marque}  {e.titre}")
            if not ouverte:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.liste.addItem(item)

    def _changer_etape(self, ligne):
        if ligne < 0:
            return
        if self.mode == "projet":
            self._changer_etape_projet(ligne)
        else:
            self._changer_etape_isole(ligne)

    def _changer_etape_isole(self, ligne):
        self.etape = self.parcours[ligne]
        self.enonce.setMarkdown((self.etape.dossier / "enonce.md").read_text(encoding="utf-8"))
        self.editeur.setPlainText((self.etape.dossier / "starter.c").read_text(encoding="utf-8"))
        self.editeur_test.setPlainText("")
        a_ecrire = self.etape.mode == "test_a_ecrire"
        self.onglets.setTabVisible(1, a_ecrire)
        self.b_jeu.setVisible(self.etape.type == "jalon")
        self._maj_cran()
        # démarrage différé à la boucle d'événements : le constructeur reste sans
        # fil vivant, donc le smoketest sans boucle ne laisse aucun QThread orphelin
        QTimer.singleShot(0, self._demarrer_lsp)

    def _changer_etape_projet(self, ligne):
        # avant de changer, on sauve le travail de l'étape qu'on quitte dans la copie
        if self._etape_courante is not None:
            self.espace.ecrire_fichier(self._etape_courante.fichier_edite,
                                       self.editeur.toPlainText())
        self.etape = self.parcours[ligne]
        self._etape_courante = self.etape
        self.enonce.setMarkdown((self.etape.dossier / "enonce.md").read_text(encoding="utf-8"))
        # le code affiché vient de la copie de travail, l'étudiant retrouve son dernier état
        self.editeur.setPlainText(self.espace.lire_fichier(self.etape.fichier_edite))
        self.onglets.setTabVisible(1, False)        # pas de test à écrire en parcours projet
        self.b_jeu.setVisible(True)                 # Compiler et jouer disponible en permanence
        self._maj_cran()

    def _cran_dispo(self):
        # parcours projet : les quatre crans d'aide sont ouverts d'emblée, pas de déverrouillage
        return 3 if self.mode == "projet" else progression.cran_disponible(self.prog)

    def _maj_cran(self):
        dispo = self._cran_dispo()
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
        dispo = self._cran_dispo()
        self.label_cran.setText(f"Tuteur, cran courant N{self.niveau} sur N{dispo} débloqué")

    def _connecter_moodle(self):
        if chemins.ATELIER_SUIVI == "local":
            return    # bouton désactivé en mode local, non atteignable normalement
        code, ok = QInputDialog.getText(
            self, "Connecter à Moodle",
            "Colle le code affiché par l'activité Moodle du TP :")
        if not ok or not code.strip():
            return
        reussi, message = moodle_sync.appairer(code.strip())
        self.console.setPlainText(message)
        if reussi:
            # Renvoie tout ce qui a déjà été validé avant la connexion, sinon
            # cette progression serait perdue (signaler_porte l'avait jetée).
            moodle_sync.signaler_deja_faits(self.prog.etapes_faites)
            self._maj_moodle()

    def _maj_moodle(self):
        """Reflète la connexion et le dernier score Moodle sur le bouton."""
        if not moodle_sync.actif():
            self.b_moodle.setText("Connecter à Moodle")
            return
        s = moodle_sync.dernier_score
        self.b_moodle.setText("Connecté à Moodle" if s is None
                              else f"Connecté à Moodle : {s} %")

    def _maj_indicateur_local(self):
        """Mode local : le bouton, désactivé, affiche juste la progression locale."""
        total = len(self.parcours)
        faites = sum(1 for e in self.parcours if e.id in self.prog.etapes_faites)
        self.b_moodle.setText(f"Progression locale : {faites} / {total} étapes")

    def _compiler(self):
        """Compile et exécute, affiche seulement la console. Ne tente pas la porte et ne
        valide pas l'étape, c'est le rôle de Tester."""
        if self.mode == "projet":
            # parcours projet : le compiler-jouer reste le geste dédié, on le garde
            self._tester()
            return
        self.console.setPlainText("Compilation et exécution en cours…")
        r = executeur.compiler_et_executer(self.etape, self.editeur.toPlainText())
        self.console.setPlainText(r.sortie)

    def _tester(self):
        if self.mode == "projet":
            self._tester_projet()
            return
        code = self.editeur.toPlainText()
        if self.etape.mode == "test_fourni":
            r = executeur.porte_perso(self.etape, code)
            self._afficher_porte(r.ok, r.sortie)
        elif self.etape.mode == "programme":
            r = executeur.porte_programme(self.etape, code)
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

    def _tester_projet(self):
        """Porte du parcours projet. Pour le capstone, on construit tout et on joue.
        Sinon on lance chaque harnais logique sur la copie de travail."""
        if self.etape.porte == "build":
            self._compiler_et_jouer()
            return
        code = self.editeur.toPlainText()
        self.console.setPlainText("Compilation et exécution des vérifications…")
        ok_global = True
        morceaux = []
        for h in self.etape.harnais:
            r = executeur.porte_logique(self.espace, self.etape.fichier_edite, code,
                                        chemins.RACINE / h, self.etape.sources)
            etat = "OK" if r.ok else "ÉCHEC"
            morceaux.append(f"--- {Path(h).stem} : {etat} ---\n{r.sortie}".rstrip())
            if not r.ok:
                ok_global = False
        self._afficher_porte(ok_global, "\n\n".join(morceaux))

    def _afficher_porte(self, ok, sortie, valider=True):
        couleur = theme.ACCENT if ok else theme.ROUGE
        titre = "PORTE OUVERTE" if ok else "PORTE FERMÉE"
        self.console.setHtml(
            f'<span style="color:{couleur};font-weight:bold;font-size:15px;">{titre}</span>'
            f'<pre style="font-family:monospace;color:{theme.TEXTE};white-space:pre-wrap;">'
            f'{html.escape(sortie)}</pre>')
        if ok and valider:
            self.prog = progression.valider(self.etape, self.prog)
            if not self.demo:
                moodle_sync.signaler_porte(self.etape.id)
            if not self.demo and self.mode != "projet":   # projet : l'état vit dans la copie
                progression.sauver(self.prog)
            if self.mode != "projet":
                self.niveau = progression.cran_disponible(self.prog)
                self._maj_cran()
            self._remplir_liste()
            if chemins.ATELIER_SUIVI == "local":
                self._maj_indicateur_local()

    def _lancer_jeu(self):
        if self.mode == "projet":
            self._compiler_et_jouer()
            return
        r = executeur.lancer_jeu(self.etape, self.editeur.toPlainText())
        self.console.setPlainText(r.sortie)

    def _compiler_et_jouer(self):
        """Écrit le code courant dans la copie, construit le projet entier et lance le jeu.
        Ne valide l'étape que si c'est bien le capstone, le simple essai du jeu ne la coche pas."""
        self.espace.ecrire_fichier(self.etape.fichier_edite, self.editeur.toPlainText())
        self.console.setPlainText("Construction du projet complet…")
        r = executeur.construire_et_jouer_projet(self.espace, lancer=True)
        self._afficher_porte(r.ok, r.sortie, valider=(r.ok and self.etape.porte == "build"))

    def _charger_corrige(self):
        if self.mode == "projet":
            # mode démo : remplit l'éditeur avec le corrigé du fichier de l'étape
            corrige = (chemins.PROJET_CORRIGE / self.etape.fichier_edite).read_text(encoding="utf-8")
            self.editeur.setPlainText(corrige)
            self.console.setPlainText("Corrigé chargé. Clique Tester pour franchir la porte.")
            return
        # mode démo : remplit l'éditeur avec le code correct, plus le test de référence pour un jalon
        self.editeur.setPlainText((self.etape.dossier / "corrige.c").read_text(encoding="utf-8"))
        if self.etape.mode == "test_a_ecrire":
            self.editeur_test.setPlainText(
                (self.etape.dossier / "test_reference.c").read_text(encoding="utf-8"))
        self.console.setPlainText("Corrigé chargé. Clique Tester pour franchir la porte.")

    def _demander_aide(self):
        if getattr(self, "_fil", None) is not None and self._fil.isRunning():
            return                       # un appel tuteur déjà en cours, on ne le détruit pas
        question, ok = QInputDialog.getText(self, "Demander de l'aide", "Ta question :")
        if not ok or not question:
            return
        niveau = min(self.niveau, self._cran_dispo())
        self.reponse_tuteur.setPlainText("Le tuteur réfléchit…")
        self._fil = FilTuteur(self.etape, self.editeur.toPlainText(), question, niveau)
        self._fil.repondu.connect(self.reponse_tuteur.setPlainText)
        self._fil.start()


    def _demarrer_lsp(self) -> None:
        """Arrête le client précédent si besoin, puis en lance un nouveau pour l'étape courante."""
        if self.mode == "projet":
            return                       # diagnostics live réservés au parcours isolé pour l'instant
        if not lsp_clangd.clangd_disponible():
            return
        if self._client_lsp is not None:
            self._client_lsp.diagnostics_recus.disconnect()
            self._client_lsp.arreter()
            self._client_lsp.wait(2000)
            self._client_lsp = None
        # efface les soulignements de l'étape précédente
        self.editeur.setExtraSelections([])
        code = self.editeur.toPlainText()
        self._client_lsp = lsp_clangd.ClientClangd(self.etape, parent=self)
        self._client_lsp.diagnostics_recus.connect(self._appliquer_diagnostics)
        self._client_lsp.demarrer(code)

    def _envoyer_code_a_clangd(self) -> None:
        """Appelée par le timer anti-rebond : transmet le code courant à clangd."""
        if self._client_lsp is not None:
            self._client_lsp.notifier_changement(self.editeur.toPlainText())

    def _appliquer_diagnostics(self, diagnostics: list) -> None:
        """Reçoit la liste de Diagnostic depuis le fil LSP et met à jour les soulignements."""
        lsp_clangd.appliquer_diagnostics(self.editeur, diagnostics)

    def closeEvent(self, event) -> None:
        """Sauve le travail projet courant, puis arrête proprement le client LSP."""
        if self.mode == "projet" and self._etape_courante is not None:
            self.espace.ecrire_fichier(self._etape_courante.fichier_edite,
                                       self.editeur.toPlainText())
        if self._client_lsp is not None:
            self._client_lsp.arreter()
            self._client_lsp.wait(2000)
        super().closeEvent(event)


def construire(app, demo=False, parcours_nom="hybride"):
    """Construit la fenêtre sans l'afficher. Sert au smoketest."""
    return Fenetre(demo=demo, parcours_nom=parcours_nom)
