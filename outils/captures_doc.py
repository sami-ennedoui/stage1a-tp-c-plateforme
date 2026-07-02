"""Genere les captures de la doc (parcours be_c) par capture Qt, sans prendre l'ecran.

La fenetre n'est jamais montree : on rend chaque widget avec widget.grab() dans des
etats controles et reproductibles. La progression reelle de l'utilisateur n'est PAS
touchee (progression.sauver est neutralise le temps du script).

Prerequis : gcc sur le PATH (w64devkit) pour que les vraies compilations s'executent.
Sortie : packaging/captures/*.png

Usage : python outils/captures_doc.py
"""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QComboBox, QCheckBox, QDialogButtonBox)
import fenetre, theme, progression, executeur, modele_etape

progression.sauver = lambda *a, **k: None          # ne pas ecrire l'etat reel
executeur.assurer_compilateur_sur_path()

CAP = RACINE / "packaging" / "captures"
CAP.mkdir(parents=True, exist_ok=True)

app = QApplication([])
theme.appliquer(app)
etapes = {e.id: e for e in modele_etape.charger_parcours(RACINE / "contenu" / "be_c")}

EXEMPLE_TUTEUR = (
    "Ton `char c` contient un code numerique (le code ASCII de la lettre). "
    "Avec le format `%d`, `printf` affiche ce nombre, pas la lettre.\n\n"
    "Pour afficher le caractere lui-meme, le format attendu est `%c`. "
    "Repere la ligne du `printf` qui traite ton `char`."
)
MAUVAIS = ('#include <stdio.h>\nint main(void)\n{\n    char c = "A";\n'
           '    printf("%d", &c)\n    return 0;\n}\n')


def fenetre_neuve(faits):
    w = fenetre.Fenetre(demo=False, parcours_nom="be_c")
    w.prog = progression.Progression(list(faits),
                                     progression.cran_disponible(progression.Progression(list(faits), 0)))
    w._remplir_liste()
    w.resize(1400, 880)
    w._changer_etape(0)
    app.processEvents(); app.processEvents()
    return w


w = fenetre_neuve([])
w.reponse_tuteur.setMarkdown(EXEMPLE_TUTEUR)
app.processEvents()
w.grab().save(str(CAP / "01-vue-ensemble.png"))

w = fenetre_neuve([])
w.editeur.setPlainText(MAUVAIS)
w._tester()
app.processEvents()
w.grab().save(str(CAP / "02-erreur-compilation.png"))

w = fenetre_neuve([])
w.editeur.setPlainText((etapes["ex01_types"].dossier / "corrige.c").read_text(encoding="utf-8"))
w._tester()
app.processEvents(); app.processEvents()
w.grab().save(str(CAP / "03-porte-ouverte-niveau-cache.png"))

dlg = QDialog()
dlg.setWindowTitle("Demander de l'aide")
lay = QVBoxLayout(dlg)
lay.addWidget(QLabel("Ta question :"))
champ = QLineEdit(); champ.setMinimumWidth(360)
champ.setText("Pourquoi mon char affiche un nombre et pas la lettre ?")
lay.addWidget(champ)
lay.addWidget(QLabel("Niveau d'aide :"))
combo = QComboBox()
for lib in ("Juste un indice, je cherche seul", "Un exemple de structure", "Une piste a verifier"):
    combo.addItem(lib)
combo.setCurrentIndex(2)
lay.addWidget(combo)
lay.addWidget(QCheckBox("Joindre mon code"))
lay.addWidget(QCheckBox("Joindre le rendu de la console"))
lay.addWidget(QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                               | QDialogButtonBox.StandardButton.Cancel))
dlg.adjustSize(); app.processEvents()
dlg.grab().save(str(CAP / "04-demander-aide.png"))

print("captures ecrites dans", CAP)
