# Reconstruire le livrable Windows (exe + doc)

Mode d'emploi complet pour rebatir le dossier livrable `TP-C-perso-exe` (parcours
`be_c`) a partir du depot. Remplace l'ancien `build_exe.txt`.

## 0. Prerequis

- Un **vrai Python 3.12** (pas l'embeddable). Sur ce poste :
  `C:\Users\VETTEL\AppData\Local\Programs\Python\Python312\python.exe`.
- Les paquets : `python -m pip install pyinstaller pyqt6 markdown`.
- **w64devkit 2.8.0** (gcc pour Windows), extrait de `w64devkit-x64-2.8.0.7z.exe`. Sur
  ce poste, le dossier `w64devkit\` est deja dans le livrable
  (`C:\Users\VETTEL\TP-C-perso-exe\w64devkit`, gcc 16.1.0).
- Un navigateur Chromium (Edge ou Chrome) pour generer le PDF de la doc. Present par
  defaut sous Windows 11 (`msedge.exe`).

## 1. Synchroniser les sources dans le dossier de build

Le dossier de build : `C:\Users\VETTEL\_tpc_exe_build` (contient `TP-C-perso.spec`).

Y copier depuis le depot, **a chaque changement des sources** :

- **tous** les `*.py` de la racine du depot (ne pas en oublier : `journal_session.py`
  fait partie des modules importes par `fenetre`) ;
- `packaging/entree_be_c.py` (le point d'entree qui force `--parcours be_c`) ;
- le dossier `contenu/be_c/` en entier vers `<build>/contenu/be_c/`.

Piege deja rencontre : si un module manque dans le dossier de build (par ex.
`journal_session.py`), PyInstaller ne l'embarque pas et l'exe plante au demarrage. Copier
**tous** les `.py`, pas seulement ceux qu'on a modifies.

## 2. Construire l'exe (PyInstaller)

Depuis le dossier de build, avec le vrai Python :

```
python -m PyInstaller --noconfirm TP-C-perso.spec
```

(Le `.spec` fait un onedir `--windowed`, nom `TP-C-perso`, avec
`datas=[('contenu/be_c', 'contenu/be_c')]`.)

Resultat : `<build>/dist/TP-C-perso/` = `TP-C-perso.exe` + `_internal/` (Python et Qt
embarques, environ 90 Mo).

## 3. Assembler le livrable

Dans `C:\Users\VETTEL\TP-C-perso-exe`, a cote de `w64devkit\` (a garder tel quel) :

- copier `dist\TP-C-perso\TP-C-perso.exe` (ecrase l'ancien) ;
- copier `dist\TP-C-perso\_internal\` en miroir (remplace l'ancien exactement, par
  exemple `robocopy dist\TP-C-perso\_internal _internal /MIR`) ;
- copier depuis `packaging\` : `lancer.bat`, `diagnostic.bat`, `README.md`, `README.pdf`
  et le dossier `captures\` ;
- `lancer_demo.bat` est **interne** (tout debloque, bouton "Le tuteur ecrit le code" et
  "Charger le corrige"). **A retirer avant de distribuer aux etudiants.**

Taille finale du livrable : environ 564 Mo (l'essentiel etant `w64devkit`).

## 4. Regenerer la documentation (captures + PDF)

Les captures sont produites **sans prendre l'ecran**, par capture Qt (`widget.grab()`),
dans des etats controles (progression neutralisee pour ne pas toucher l'etat reel). Le
script vit dans le depot sous `outils/` (ou dans le scratchpad de la session qui l'a
cree). Il ecrit dans `packaging/captures/` :

- `01-vue-ensemble.png`, `02-erreur-compilation.png`,
  `03-porte-ouverte-niveau-cache.png`, `04-demander-aide.png`.

Le PDF est rendu depuis `README.md` : markdown -> HTML style (theme clair, images en
base64) -> `msedge --headless --print-to-pdf`. Le script de generation vit sous
`outils/doc_pdf.py`. Refaire tourner captures puis PDF quand l'UI ou le texte changent.

## 5. Verifier

- `python -m unittest tests.test_parcours_tp tests.test_executeur` : les 4 echecs
  restants sont **pre-existants** (SDL3/SDL.h absent, parcours hybride), sans rapport
  avec `be_c`.
- Verifier les 14 exercices : pour chaque exo de `be_c`, `corrige.c` ouvre la porte et
  `starter.c` la ferme (14/14).
- Smoke de l'exe fige : le lancer (au besoin avec `QT_QPA_PLATFORM=offscreen`), il doit
  rester vivant quelques secondes (imports resolus, fenetre construite).
- Auto-suffisance : avec seulement `w64devkit\bin` au PATH (aucun gcc systeme), le gcc du
  bundle compile un corrige embarque et sort le resultat attendu.

## Notes

- Le `.exe` force `--parcours be_c` via `entree_be_c.py` et laisse passer les autres
  arguments (par ex. `--demo`).
- `lancer.bat` et `lancer_demo.bat` mettent `w64devkit\bin` puis
  `%USERPROFILE%\.local\bin` (ou vivent `claude` et `codex`) au PATH, puis lancent le
  `.exe`. Ils ciblent le `.exe`, pas un `python\plateforme`.
- L'exe trouve aussi gcc seul s'il voit `w64devkit\` a cote de lui
  (`executeur.assurer_compilateur_sur_path`), donc il marche meme en double-clic direct,
  sans passer par `lancer.bat`.
- Le dossier livrable garde le nom historique `TP-C-perso-exe` / `TP-C-perso.exe` bien
  qu'il lance `be_c`.
