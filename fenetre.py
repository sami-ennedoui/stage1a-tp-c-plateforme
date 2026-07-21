"""Fenêtre de l'atelier Snake. Câble énoncé, éditeur, console, tuteur et portes.
Deux parcours partagent ce moteur : 'hybride', des étapes isolées avec test à écrire,
et 'projet', où l'étudiant remplit la vraie structure du jeu jusqu'à pouvoir y jouer."""
import html
import sys
from pathlib import Path

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
                             QPlainTextEdit, QTextEdit, QPushButton, QLabel, QTabWidget,
                             QListWidgetItem, QDialog, QLineEdit, QCheckBox,
                             QDialogButtonBox, QComboBox, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

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
from journal_session import Journal, JournalMuet
from espace_projet import EspaceProjet
from modele_etape import charger_parcours_complet


def _chemin_lanceur() -> Path:
    """Trouve lancer.bat, où qu'il soit selon la façon dont l'atelier tourne.

    Dans le bundle figé, chemins.RACINE désigne _internal et le lanceur est au niveau
    au-dessus ; dans un clone du dépôt il vit dans packaging\\. On rend le premier
    qui existe, et à défaut le chemin attendu du bundle, pour que le message d'erreur
    du dialogue désigne un endroit sensé plutôt qu'un chemin interne."""
    candidats = [chemins.RACINE.parent / "lancer.bat",
                 chemins.RACINE / "lancer.bat",
                 chemins.RACINE / "packaging" / "lancer.bat"]
    for c in candidats:
        if c.exists():
            return c
    return candidats[0]


def _titre(texte: str) -> QLabel:
    """Petit en-tête de colonne, stylé par la feuille de style via son objectName."""
    etiquette = QLabel(texte)
    etiquette.setObjectName("titre")
    return etiquette


class FilTuteur(QThread):
    """Appel IA dans un fil séparé pour ne pas figer la fenêtre."""
    repondu = pyqtSignal(str)

    def __init__(self, etape, code, question, niveau, historique=None, console=""):
        super().__init__()
        self._args = (etape, code, question, niveau, historique, console)

    def run(self):
        self.repondu.emit(tuteur_ia.demander_aide(*self._args))


class FilGeneration(QThread):
    """Mode démo : le tuteur écrit le programme lui-même, dans un fil séparé."""
    genere = pyqtSignal(str)

    def __init__(self, etape, variante=""):
        super().__init__()
        self._args = (etape, variante)

    def run(self):
        self.genere.emit(tuteur_ia.generer_solution(*self._args))


class Fenetre(QMainWindow):
    def __init__(self, demo=False, parcours_nom="hybride", tracer=False):
        super().__init__()
        self.demo = demo
        self.parcours_nom = parcours_nom
        parcours = charger_parcours_complet(chemins.contenu_racine(parcours_nom))
        self.mode = parcours.mode
        self.parcours = parcours.etapes
        self.libre = parcours.libre
        # mode enseignant/démo mémorisé : tout ouvert, tous les crans du tuteur. Activé
        # depuis le menu Paramètres (protégé par le mot de passe auteur). N'altère pas la
        # progression réelle : le décocher rend le parcours progressif tel qu'il était.
        self.tout_debloque = reglages.tout_debloque()

        titre = "Atelier Snake"
        if self.mode == "projet":
            titre += ", parcours projet"
        if demo:
            titre += " (mode démo)"
        self.setWindowTitle(titre)

        # Journal de session (instrumentation pédagogique). On ne trace qu'en session
        # réelle : jamais en démo (le tuteur écrit alors le code) ni au smoketest/tests,
        # où le journal reste muet (mêmes méthodes, n'écrit rien). Voir journal_session.py.
        self._trace_active = tracer and not demo
        if self._trace_active:
            # exe figé : écrire journaux/ À CÔTÉ de l'exe, pas dans _internal (où pointe
            # __file__ du module). En source, on laisse le défaut du module.
            base = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else None
            self.journal = Journal(dossier=(base / "journaux") if base else None,
                                   meta={"parcours": parcours_nom, "mode": self.mode,
                                         "moteur": tuteur_ia._moteur_choisi()})
        else:
            self.journal = JournalMuet()
        self._exo_valide_courant = False        # l'exo affiché est-il déjà validé (pour l'inactivité)

        # parcours projet : une copie de travail vivante, remplie étape par étape.
        # On part du squelette à trous. En démo on repart propre à chaque lancement.
        self.espace = None
        self._etape_courante = None      # étape dont l'éditeur est affiché, pour la sauvegarde
        # mémoire du tuteur : les (question, réponse) de l'exercice courant, remises à zéro
        # quand on change d'exercice, pour que le tuteur suive le fil d'un échange
        self._historique_tuteur = []
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
        # cran restauré depuis l'état sauvegardé, l'étudiant qui revient garde son niveau ;
        # _cran_dispo tient compte du mode « tout débloqué » (tous les crans ouverts)
        self.niveau = 0 if self.mode == "projet" else self._cran_dispo()

        self.liste = QListWidget()
        self.liste.currentRowChanged.connect(self._changer_etape)

        self.enonce = QTextEdit(readOnly=True)
        # l'enonce est rendu en markdown ; on force une police lisible (le defaut Qt
        # est petit) et un peu d'air entre les puces via la feuille de style du document
        _police_enonce = QFont()
        _police_enonce.setPointSize(11)
        self.enonce.document().setDefaultFont(_police_enonce)
        self.enonce.document().setDefaultStyleSheet(
            "li { margin-bottom: 6px; } "
            "h1 { color: %s; } "
            "p { margin-bottom: 6px; }" % theme.ACCENT
        )
        # badge persistant du niveau caché : reste affiché tant que l'exercice validé a un
        # approfondissement (contrairement à la note console, éphémère). Un faux débutant
        # pressé ne peut pas le manquer : il est au-dessus de la ligne de flottaison.
        self.badge_appro = QLabel("▼  NIVEAU CACHÉ DÉBLOQUÉ  —  un approfondissement est ajouté sous l'énoncé")
        self.badge_appro.setObjectName("badge_appro")
        self.badge_appro.setStyleSheet(
            "#badge_appro { background:%s; color:%s; font-weight:bold; "
            "padding:6px 10px; border-radius:4px; }" % (theme.ACCENT, theme.FOND)
        )
        self.badge_appro.setVisible(False)
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
        # veille : si l'étudiant ne fait rien pendant 90 s sur un exo non validé, on le
        # note (rend le profil « passif » visible). Le timer est remis à zéro à chaque
        # action (frappe, test, demande d'aide) via _reveil.
        self._timer_inactif = QTimer(self)
        self._timer_inactif.setSingleShot(True)
        self._timer_inactif.setInterval(90000)
        self._timer_inactif.timeout.connect(self._sur_inactivite)
        self.label_lsp = QLabel()
        self.label_lsp.setVisible(False)
        self.label_lsp.setObjectName("avertissement_lsp")
        if self.mode != "projet" and not lsp_clangd.clangd_disponible():
            self.label_lsp.setText(
                "clangd absent, diagnostics live indisponibles. Installe clang-tools-extra."
            )
            self.label_lsp.setVisible(True)
        self.reponse_tuteur = QTextEdit(readOnly=True)

        b_compiler = QPushButton("Compiler")
        b_tester = QPushButton("Tester")
        b_tester.setObjectName("primaire")     # bouton d'action principal, accent vert
        self.b_jeu = QPushButton("Compiler et jouer" if self.mode == "projet" else "Lancer le jeu")
        # attribut et non variable locale : _appliquer_reglage_tuteur doit pouvoir
        # le masquer quand le tuteur est désactivé
        self.b_aide = QPushButton("Demander de l'aide")
        self.b_ecrire = QPushButton("Le tuteur écrit le code")
        self.b_ecrire.setVisible(self.demo)      # bouton du mode démo seulement
        self.b_corrige = QPushButton("Charger le corrigé")
        self.b_corrige.setVisible(self.demo)     # bouton du mode démo seulement
        b_compiler.clicked.connect(self._compiler)
        b_tester.clicked.connect(self._tester)
        self.b_jeu.clicked.connect(self._lancer_jeu)
        self.b_aide.clicked.connect(self._demander_aide)
        self.b_ecrire.clicked.connect(self._tuteur_ecrit_code)
        self.b_corrige.clicked.connect(self._charger_corrige)

        barre = QHBoxLayout()
        barre.setSpacing(8)
        for b in (b_compiler, b_tester, self.b_jeu, self.b_aide, self.b_ecrire, self.b_corrige):
            barre.addWidget(b)
        barre.addStretch(1)

        gauche = QVBoxLayout()
        gauche.setSpacing(6)
        gauche.addWidget(_titre("PARCOURS"))
        gauche.addWidget(self.liste)
        self.b_moodle = QPushButton("Connecté à Moodle" if moodle_sync.actif()
                                    else "Connecter à Moodle")
        self.b_moodle.clicked.connect(self._connecter_moodle)
        gauche.addWidget(self.b_moodle)

        centre = QVBoxLayout()
        centre.setSpacing(6)
        centre.addWidget(_titre("ÉNONCÉ"))
        centre.addWidget(self.badge_appro)
        centre.addWidget(self.enonce, 2)
        centre.addWidget(_titre("ATELIER"))
        centre.addWidget(self.onglets, 5)
        centre.addWidget(self.label_lsp)
        centre.addLayout(barre)
        # la console est enveloppée pour pouvoir la masquer (plus de place au code)
        console_layout = QVBoxLayout()
        console_layout.setContentsMargins(0, 0, 0, 0)
        console_layout.setSpacing(6)
        console_layout.addWidget(_titre("CONSOLE"))
        console_layout.addWidget(self.console, 1)
        self.panneau_console = QWidget()
        self.panneau_console.setLayout(console_layout)
        centre.addWidget(self.panneau_console, 3)

        droite = QVBoxLayout()
        droite.setSpacing(6)
        droite.addWidget(_titre("TUTEUR IA"))
        droite.addWidget(self.reponse_tuteur)

        # panneaux lateraux enveloppes pour pouvoir les montrer ou cacher d'un clic
        self.panneau_parcours = QWidget()
        self.panneau_parcours.setLayout(gauche)
        self.panneau_tuteur = QWidget()
        self.panneau_tuteur.setLayout(droite)

        racine = QHBoxLayout()
        racine.setContentsMargins(14, 14, 14, 14)
        racine.setSpacing(14)
        racine.addWidget(self.panneau_parcours, 1)
        racine.addLayout(centre, 4)
        racine.addWidget(self.panneau_tuteur, 2)
        conteneur = QWidget()
        conteneur.setLayout(racine)
        self.setCentralWidget(conteneur)
        self._construire_barre_affichage()
        self._construire_menu()
        self._appliquer_reglage_tuteur()

        # anti-rebond : textChanged déclenche le timer, pas l'envoi direct
        self.editeur.textChanged.connect(self._timer_lsp.start)
        # toute frappe compte comme une activité : réarme le compteur d'inactivité
        self.editeur.textChanged.connect(self._reveil)

        self._remplir_liste()
        self.liste.setCurrentRow(0)
        if self._trace_active:
            self._timer_inactif.start()
        moodle_sync.rejouer()   # vide au lancement ce qui attendait d'être envoyé

    def _construire_menu(self):
        """Menu Paramètres : navigation, dossiers, diagnostic, et édition protégée.

        Ce menu avait disparu de la lignée de livraison lors de la fusion b40a8db, en
        emportant le seul point d'entrée de reglages, auteur, diagnostic et des deux
        dialogues : les modules étaient toujours livrés, mais plus rien ne pouvait les
        ouvrir. Repère de contrôle donné par la vérification Linux : DialogueNiveaux
        doit être référencé deux fois dans ce fichier, import compris."""
        menu = self.menuBar().addMenu("Paramètres")
        menu.addAction("Changer de parcours…").triggered.connect(self._changer_parcours)
        menu.addAction("Ouvrir le dossier du contenu").triggered.connect(
            self._ouvrir_dossier_contenu)
        menu.addAction("Emplacements et diagnostic…").triggered.connect(
            self._ouvrir_diagnostic)
        menu.addSeparator()
        self.action_tuteur = menu.addAction("Tuteur IA")
        self.action_tuteur.setCheckable(True)
        self.action_tuteur.setChecked(reglages.tuteur_actif())
        self.action_tuteur.toggled.connect(self._basculer_tuteur)
        menu.addAction("Commande du tuteur…").triggered.connect(self._changer_commande_ia)
        menu.addSeparator()
        menu.addAction("Gérer les niveaux…").triggered.connect(self._ouvrir_gestion_niveaux)
        # Tout débloquer : mode enseignant/démo, toutes les étapes ouvertes et tous les
        # crans du tuteur. Coché avant de connecter le signal pour ne pas déclencher la
        # demande de mot de passe au démarrage. Sans objet en parcours projet (déjà ouvert).
        self.action_tout_debloque = menu.addAction("Tout débloquer (mode enseignant)")
        self.action_tout_debloque.setCheckable(True)
        self.action_tout_debloque.setChecked(self.tout_debloque)
        self.action_tout_debloque.setEnabled(self.mode != "projet")
        self.action_tout_debloque.toggled.connect(self._basculer_tout_debloque)
        menu.addSeparator()
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
            "Ferme puis relance l'atelier pour basculer dessus.")

    def _basculer_tuteur(self, actif: bool):
        reglages.definir_tuteur_actif(actif)
        self._appliquer_reglage_tuteur()
        if actif and not tuteur_ia.moteur_disponible():
            # Réactiver le réglage ne fait pas apparaître un moteur : le dire tout de
            # suite, sinon l'enseignant croit avoir rendu le tuteur et rien ne bouge.
            QMessageBox.information(
                self, "Tuteur activé, moteur absent",
                "Le tuteur est réactivé dans les réglages, mais aucun moteur IA n'a été "
                "trouvé sur ce poste. Renseigne « Commande du tuteur… » ou installe un "
                "moteur pour que l'aide soit réellement disponible.")

    def _basculer_tout_debloque(self, actif: bool):
        """Active/désactive le mode enseignant « tout débloqué ». L'activation exige le
        mot de passe auteur ; la désactivation ne fait que re-verrouiller, sans mot de passe."""
        if actif and not self._demander_mot_de_passe():
            # annulation ou mot de passe faux : on rétablit la case sans rien changer
            self.action_tout_debloque.blockSignals(True)
            self.action_tout_debloque.setChecked(False)
            self.action_tout_debloque.blockSignals(False)
            return
        reglages.definir_tout_debloque(actif)
        self.tout_debloque = actif
        self._maj_cran()             # ouvre (ou referme) les crans du tuteur
        self._remplir_liste()        # ouvre (ou reverrouille) les étapes à l'affichage
        if actif:
            QMessageBox.information(
                self, "Tout débloqué",
                "Toutes les étapes sont ouvertes et les quatre crans du tuteur "
                "disponibles, comme en mode démo. La progression réelle de l'étudiant "
                "n'est pas modifiée. Ce réglage reste actif au prochain lancement ; "
                "décoche-le pour revenir au parcours progressif.")

    def _changer_commande_ia(self):
        actuelle = reglages.commande_ia()
        texte, ok = QInputDialog.getText(
            self, "Commande du tuteur",
            "Commande qui lance le moteur IA.\n"
            "Vide = détection automatique. Utilise {prompt} pour placer la question,\n"
            "sinon elle est ajoutée en dernier argument.\n"
            "Exemple :  mon-moteur --sans-couleur {prompt}",
            QLineEdit.EchoMode.Normal, actuelle)
        if not ok:
            return
        reglages.definir_commande_ia(texte.strip())
        self._appliquer_reglage_tuteur()
        if texte.strip() and not tuteur_ia.moteur_disponible():
            QMessageBox.warning(
                self, "Commande introuvable",
                "Le premier mot de cette commande n'a pas été trouvé sur le PATH.\n"
                "Le tuteur restera indisponible tant qu'elle ne pointe pas sur un "
                "exécutable existant.")

    def _ouvrir_dossier_contenu(self):
        try:
            diagnostic.ouvrir_dossier(chemins.contenu_racine(self.parcours_nom))
        except OSError as e:
            QMessageBox.warning(self, "Ouverture impossible", str(e))

    def _ouvrir_diagnostic(self):
        DialogueDiagnostic(self.parcours_nom, _chemin_lanceur(), self).exec()

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
        DialogueNiveaux(chemins.contenu_racine(self.parcours_nom), self).exec()
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
        self.libre = parcours.libre
        if not self.parcours:
            self.liste.clear()
            return
        self._remplir_liste()
        ligne = min(self.liste.currentRow(), len(self.parcours) - 1)
        self.liste.setCurrentRow(max(0, ligne))

    def _connecter_moodle(self):
        code, ok = QInputDialog.getText(
            self, "Connecter à Moodle",
            "Colle le code affiché par l'activité Moodle du TP :")
        if not ok or not code.strip():
            return
        reussi, message, deja_faits = moodle_sync.appairer(code.strip())
        self.console.setPlainText(message)
        if reussi:
            self.b_moodle.setText("Connecté à Moodle")
            # Reprise multi-poste : le compagnon renvoie les étapes déjà validées par
            # cet étudiant, peut-être depuis une autre machine. On les fusionne dans la
            # progression locale pour déverrouiller les niveaux au bon endroit.
            if deja_faits:
                self.prog = progression.fusionner(self.prog, deja_faits, self.parcours)
                progression.sauver(self.prog)
                self.niveau = progression.cran_disponible(self.prog)
                self._remplir_liste()
                self._maj_cran()
            # Renvoie tout ce qui avait été validé AVANT la connexion : sans appairage
            # signaler_porte ne gardait rien, cette progression serait perdue.
            moodle_sync.signaler_deja_faits(self.prog.etapes_faites)
            moodle_sync.rejouer()

    def _reveil(self):
        """Remet à zéro le compteur d'inactivité : appelé à chaque action de l'étudiant."""
        if self._trace_active:
            self._timer_inactif.start()

    def _sur_inactivite(self):
        """90 s sans action sur un exercice non validé : on le trace au journal (rend le
        profil « passif » visible pour un enseignant), puis on ré-arme pour capter une
        inactivité prolongée en plusieurs tranches.

        On ne pousse PAS de coup de pouce à l'écran : décision de conception fondée sur la
        biblio (Prather 2024 « widening gap » ; Shen-Tamkin, aide tirée >> aide poussée).
        L'aide reste tirée par l'étudiant, jamais poussée vers lui. On garde seulement la
        mesure au journal."""
        etape = getattr(self, "etape", None)
        if etape is not None and not self._exo_valide_courant:
            self.journal.event("inactivite", exo=etape.id, secondes=90)
        self._timer_inactif.start()

    def _construire_barre_affichage(self):
        """Barre en haut pour montrer ou cacher les panneaux Parcours et Tuteur, afin
        d'alleger l'interface quand on veut se concentrer sur l'enonce et le code."""
        barre = self.addToolBar("Affichage")
        barre.setObjectName("barre_affichage")
        barre.setMovable(False)
        self._bascules_affichage = {}
        for texte, panneau in (("Parcours", self.panneau_parcours),
                               ("Console", self.panneau_console),
                               ("Tuteur IA", self.panneau_tuteur)):
            action = barre.addAction(texte)
            action.setCheckable(True)
            action.setChecked(True)
            action.toggled.connect(panneau.setVisible)
            self._bascules_affichage[texte] = action

    def _appliquer_reglage_tuteur(self):
        """Montre ou masque tout ce qui relève du tuteur, selon le réglage.

        Masquer le panneau ne suffirait pas : la barre d'affichage porte une bascule
        « Tuteur IA » qui le ramènerait d'un clic. On retire donc aussi cette bascule,
        sinon le réglage se contourne sans le vouloir.

        On se règle sur la BASCULE seule, pas sur la présence d'un moteur, et la
        distinction est délibérée. Un moteur absent doit laisser le bouton en place :
        il répond alors « Moteur IA indisponible, le reste de l'atelier marche », ce
        qui apprend à l'étudiant que sa séance n'est pas cassée. Le masquer aurait
        supprimé cette explication et transformé une panne lisible en absence muette."""
        actif = reglages.tuteur_actif()
        self.b_aide.setVisible(actif)
        if not actif:
            self.b_ecrire.setVisible(False)      # y compris en démo : plus de génération
        elif self.demo:
            self.b_ecrire.setVisible(True)
        self.panneau_tuteur.setVisible(actif)
        bascule = self._bascules_affichage.get("Tuteur IA")
        if bascule is not None:
            bascule.setChecked(actif)
            bascule.setVisible(actif)

    def _remplir_liste(self):
        self.liste.clear()
        for e in self.parcours:
            faite = e.id in self.prog.etapes_faites
            if self.mode == "projet" or self.libre or self.tout_debloque:
                # parcours projet : on travaille sur la vraie structure, tout est ouvert.
                # parcours libre : l'étudiant révise le point qu'il veut, sans refaire la file.
                # tout débloqué (enseignant) : verrouillage levé, comme en démo.
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

    def _maj_enonce(self):
        """Affiche l'énoncé de l'étape courante. Si l'exercice est validé et qu'un
        approfondissement.md existe, on l'ajoute dessous : c'est le niveau caché,
        débloqué une fois la porte de base franchie."""
        md = (self.etape.dossier / "enonce.md").read_text(encoding="utf-8")
        appro = self.etape.dossier / "approfondissement.md"
        debloque = appro.exists() and self.etape.id in self.prog.etapes_faites
        if debloque:
            md += "\n\n---\n\n" + appro.read_text(encoding="utf-8")
        self.enonce.setMarkdown(md)
        # le badge reste affiché tant que l'exo validé a un approfondissement : signal
        # persistant, corrigé à chaque changement d'exercice comme à la révélation.
        self.badge_appro.setVisible(debloque)

    def _changer_etape_isole(self, ligne):
        self.etape = self.parcours[ligne]
        self._historique_tuteur = []     # nouvel exercice, le tuteur repart sans historique
        self.reponse_tuteur.clear()      # ne pas laisser la réponse de l'exo précédent affichée
        self._exo_valide_courant = self.etape.id in self.prog.etapes_faites
        self.journal.event("exo_ouvert", exo=self.etape.id)
        self._reveil()
        self._maj_enonce()
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
        self._historique_tuteur = []     # nouvel exercice, le tuteur repart sans historique
        self.reponse_tuteur.clear()      # ne pas laisser la réponse de l'exo précédent affichée
        self._exo_valide_courant = self.etape.id in self.prog.etapes_faites
        self.journal.event("exo_ouvert", exo=self.etape.id)
        self._reveil()
        self.enonce.setMarkdown((self.etape.dossier / "enonce.md").read_text(encoding="utf-8"))
        # le code affiché vient de la copie de travail, l'étudiant retrouve son dernier état
        self.editeur.setPlainText(self.espace.lire_fichier(self.etape.fichier_edite))
        self.onglets.setTabVisible(1, False)        # pas de test à écrire en parcours projet
        self.b_jeu.setVisible(True)                 # Compiler et jouer disponible en permanence
        self._maj_cran()

    def _cran_dispo(self):
        # parcours projet et mode « tout débloqué » : les quatre crans d'aide sont ouverts
        # d'emblée, pas de déverrouillage progressif
        if self.mode == "projet" or self.tout_debloque:
            return 3
        return progression.cran_disponible(self.prog)

    def _maj_cran(self):
        # le tuteur utilise automatiquement le meilleur cran débloqué ; l'aide devient
        # plus directe au fil des exercices validés, sans réglage manuel à l'écran
        self.niveau = self._cran_dispo()

    def _compiler(self):
        """Compile et exécute, n'affiche que la sortie console. Ne tente pas la porte et
        ne valide pas l'étape : franchir la porte est le rôle du bouton Tester."""
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
            self._afficher_porte(r.ok, r.sortie, categorie=r.categorie, manquants=r.manquants)
        elif self.etape.mode == "programme":
            r = executeur.porte_programme(self.etape, code)
            self._afficher_porte(r.ok, r.sortie, categorie=r.categorie, manquants=r.manquants)
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
            self._afficher_porte(r.ok, "Ton test est solide.\n" + r.sortie,
                                 categorie=r.categorie, manquants=r.manquants)

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

    def _afficher_porte(self, ok, sortie, valider=True, categorie="", manquants=()):
        # resultat : categorie fine si la porte la fournit (porte_programme), sinon
        # on retombe sur ok/ferme. manquants : fragments manquants si sortie_incomplete.
        resultat = categorie if categorie else ("ok" if ok else "ferme")
        self.journal.event("test_porte", exo=self.etape.id, ok=bool(ok),
                           resultat=resultat, manquants=list(manquants))
        self._reveil()
        if ok and valider:
            self._exo_valide_courant = True
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
            # niveau caché : révéler l'approfondissement dès que la porte de base passe
            if (self.etape.dossier / "approfondissement.md").exists():
                self._maj_enonce()   # ajoute l'approfondissement et allume le badge persistant
                # l'amener dans le champ de vision : il est sous la ligne de flottaison, un
                # faux débutant pressé ne scrollerait pas jusqu'en bas de lui-même.
                self.enonce.moveCursor(QTextCursor.MoveOperation.Start)
                if self.enonce.find("Approfondissement"):
                    self.enonce.ensureCursorVisible()
                self.console.append(
                    f'<span style="color:{theme.ACCENT};font-weight:bold;">'
                    "Niveau caché débloqué : un approfondissement est apparu sous "
                    "l'énoncé (voir le bandeau vert).</span>")

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

    # libellés du choix d'aide, du plus autonome au plus direct ; index = cran
    _LIBELLES_CRAN = (
        "Juste un indice, je cherche seul",
        "Un exemple de structure",
        "Une piste à vérifier",
        "Aide directe",
    )

    def _dialogue_aide(self):
        """Demande la question, le niveau d'aide voulu, et en option (décoché par défaut)
        si l'étudiant veut joindre son code et/ou le rendu de la console. Le choix de
        niveau va de N0 au meilleur cran débloqué : l'étudiant peut demander MOINS d'aide
        que le maximum, jamais plus. Renvoie (question, niveau, joindre_code,
        joindre_console) ou None si annulé."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Demander de l'aide")
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("Ta question :"))
        champ = QLineEdit()
        champ.setMinimumWidth(360)
        lay.addWidget(champ)
        # choix du niveau, seulement si plus d'un cran est débloqué
        dispo = self._cran_dispo()
        choix_niveau = None
        if dispo >= 1:
            lay.addWidget(QLabel("Niveau d'aide :"))
            choix_niveau = QComboBox()
            for n in range(dispo + 1):
                choix_niveau.addItem(self._LIBELLES_CRAN[n], n)
            choix_niveau.setCurrentIndex(dispo)   # par défaut, l'aide la plus complète débloquée
            lay.addWidget(choix_niveau)
        case_code = QCheckBox("Joindre mon code")
        case_console = QCheckBox("Joindre le rendu de la console")
        lay.addWidget(case_code)
        lay.addWidget(case_console)
        boutons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel)
        boutons.accepted.connect(dlg.accept)
        boutons.rejected.connect(dlg.reject)
        champ.returnPressed.connect(dlg.accept)
        lay.addWidget(boutons)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return None
        question = champ.text().strip()
        if not question:
            return None
        niveau = choix_niveau.currentData() if choix_niveau is not None else dispo
        return question, niveau, case_code.isChecked(), case_console.isChecked()

    def _demander_aide(self):
        if getattr(self, "_fil", None) is not None and self._fil.isRunning():
            return                       # un appel tuteur déjà en cours, on ne le détruit pas
        reponse = self._dialogue_aide()
        if reponse is None:
            return
        question, niveau, joindre_code, joindre_console = reponse
        self._cran_derniere_aide = niveau
        self.journal.event("tuteur_demande", exo=self.etape.id, cran=niveau,
                           longueur_question=len(question),
                           joint_code=joindre_code, joint_console=joindre_console)
        self._reveil()
        self.reponse_tuteur.setPlainText("Le tuteur réfléchit…")
        code = self.editeur.toPlainText() if joindre_code else ""
        console = self.console.toPlainText() if joindre_console else ""
        historique = list(self._historique_tuteur)   # instantané passé au fil
        self._fil = FilTuteur(self.etape, code, question, niveau, historique, console)
        self._fil.repondu.connect(lambda rep, q=question: self._tuteur_a_repondu(q, rep))
        self._fil.start()

    def _tuteur_a_repondu(self, question, reponse):
        self.reponse_tuteur.setPlainText(reponse)
        erreur = tuteur_ia.reponse_est_erreur(reponse)
        self.journal.event("tuteur_reponse", exo=self.etape.id,
                           cran=getattr(self, "_cran_derniere_aide", None),
                           longueur_reponse=len(reponse),
                           filtre_a_masque=tuteur_ia.filtre_a_masque(reponse),
                           erreur=erreur)
        # on ne mémorise que les vraies réponses, pas les messages d'erreur du moteur
        if not erreur:
            self._historique_tuteur.append((question, reponse))

    def _dialogue_generation(self):
        """Mode démo. Demande une consigne optionnelle au tuteur qui va écrire le code
        (vide = solution correcte ; sinon on peut réclamer une variante buggée pour voir
        comment la porte réagit). Renvoie la consigne (str, possiblement vide) ou None."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Le tuteur écrit le code")
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("Consigne au tuteur (laisse vide pour une solution correcte) :"))
        champ = QLineEdit()
        champ.setMinimumWidth(420)
        champ.setPlaceholderText("ex. introduis une erreur de format d'affichage")
        lay.addWidget(champ)
        boutons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel)
        boutons.accepted.connect(dlg.accept)
        boutons.rejected.connect(dlg.reject)
        champ.returnPressed.connect(dlg.accept)
        lay.addWidget(boutons)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return None
        return champ.text().strip()

    def _tuteur_ecrit_code(self):
        """Mode démo : le tuteur génère un programme complet et le place dans l'éditeur."""
        if getattr(self, "_fil_gen", None) is not None and self._fil_gen.isRunning():
            return
        variante = self._dialogue_generation()
        if variante is None:
            return
        self.journal.event("tuteur_ecrit_code", exo=self.etape.id, variante=variante)
        self.console.setPlainText("Le tuteur écrit le code…")
        self._fil_gen = FilGeneration(self.etape, variante)
        self._fil_gen.genere.connect(self._code_genere)
        self._fil_gen.start()

    def _code_genere(self, code):
        if tuteur_ia.reponse_est_erreur(code):
            self.console.setPlainText(code)     # message d'indisponibilité du moteur
            return
        self.editeur.setPlainText(code)
        self.console.setPlainText("Code généré par le tuteur. Clique Tester pour voir la porte.")


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
        """Sauve le travail projet courant, clôt le journal, puis arrête le client LSP."""
        self._timer_inactif.stop()
        self.journal.fin()
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
