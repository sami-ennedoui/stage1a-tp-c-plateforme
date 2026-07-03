# Reconstruire le livrable Windows (exe + doc)

Mode d'emploi pour rebatir le bundle lancable (parcours `be_c`) a partir du depot.
Remplace l'ancien `build_exe.txt`.

Deux voies : le **script automatise** (recommande, surtout sur un PC neuf) ou les
**etapes manuelles** detaillees plus bas.

## Voie rapide : build automatise sur un PC neuf

Sur un poste Windows neuf, **droits admin conseilles** (pour l'install de Python via
winget) :

1. Installer git et cloner le depot (ou telecharger le source en zip).
2. Depuis la racine du clone, lancer :

   ```
   powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1 -Zip
   ```

Le script (`packaging/build_windows.ps1`) fait tout, de facon idempotente :

- installe **Python 3.12** via winget s'il manque, puis les paquets pip
  (`pyinstaller`, `pyqt6`, `markdown`) ;
- telecharge et auto-extrait **w64devkit** (gcc) a la racine du depot s'il manque
  (derniere version x64 depuis GitHub) ;
- construit l'exe (PyInstaller), regenere les captures et le PDF ;
- assemble le bundle dans `_bundle\TP-C-perso\` (exe, `w64devkit`, `lancer.bat`,
  `diagnostic.bat`, `GUIDE.md` comme `README.md`, `README.pdf`, `captures\`) ;
- verifie que l'exe assemble demarre ;
- avec `-Zip`, produit `_bundle\TP-C-perso.zip`, pret pour une Release GitHub.

Options : `-SkipInstall` (ne rien installer, environnement deja pret). Le
`lancer_demo.bat` interne n'est pas inclus, le bundle est distribuable tel quel. Sorties
(`w64devkit\`, `.build\`, `_bundle\`) ignorees par git.

Pour **publier** ensuite le zip en Release GitHub, voir la section « Publier une Release »
plus bas.

---

Le reste de ce document detaille les memes etapes a la main (utile pour comprendre ou
depanner).

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
- copier `lancer.bat` et `diagnostic.bat` depuis `packaging\` ;
- **doc utilisateur du bundle** : copier `GUIDE.md` (racine du depot) dans le bundle sous
  le nom `README.md` (c'est la doc conviviale, ou "Python et gcc sont dans ce dossier" est
  vrai), copier le dossier `captures\` (racine), et generer `README.pdf` (voir section 4) ;
- `lancer_demo.bat` est **interne** (tout debloque, bouton "Le tuteur ecrit le code" et
  "Charger le corrige"). **A retirer avant de distribuer aux etudiants.**

Ne PAS copier le `README.md` **racine du depot** dans le bundle : celui-la parle du depot
source (Releases, reconstruction), il tromperait l'utilisateur du bundle. Le bundle recoit
`GUIDE.md` renomme en `README.md`.

Taille finale du livrable : environ 564 Mo (l'essentiel etant `w64devkit`).

## 4. Regenerer la documentation (captures + PDF)

Les captures sont produites **sans prendre l'ecran**, par capture Qt (`widget.grab()`),
dans des etats controles (progression neutralisee pour ne pas toucher l'etat reel). Le
script `outils/captures_doc.py` ecrit dans `captures/` a la racine :

- `01-vue-ensemble.png`, `02-erreur-compilation.png`,
  `03-porte-ouverte-niveau-cache.png`, `04-demander-aide.png`.

Le PDF du bundle est rendu depuis `GUIDE.md` (racine) : markdown -> HTML style (theme
clair, images en base64) -> `msedge --headless --print-to-pdf`. Le script de generation
est `outils/doc_pdf.py`. Enchainer (le PDF est ecrit directement dans le bundle) :

```
python outils/captures_doc.py
python outils/doc_pdf.py GUIDE.md "C:\Users\VETTEL\TP-C-perso-exe\README.pdf"
```

Refaire tourner captures puis PDF quand l'UI ou le texte changent.

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

## Publier une Release GitHub

La charge utile (exe + w64devkit, ~800 Mo assembles) n'est pas sur git : on distribue le
bundle par une **Release GitHub** (zip telechargeable au navigateur, meme sur un depot
prive). Avec `gh` authentifie (`gh auth status`) et le zip a la main :

```
gh release create v0.1-demo --target <branche> --prerelease ^
  --title "TP C, atelier d'introduction au langage C (v0.1-demo)" ^
  --notes-file notes.md ^
  chemin\vers\TP-C-perso.zip
```

Remplacer l'asset d'une release existante : `gh release upload v0.1-demo <zip> --clobber`.
Mettre a jour les notes : `gh release edit v0.1-demo --notes-file notes.md`.

Note distribution : l'exe n'est pas signe. Apres un telechargement navigateur, SmartScreen
affiche « Windows a protege votre PC ». Parades sans admin, documentees dans `GUIDE.md` :
« Informations complementaires > Executer quand meme », ou clic droit sur le zip >
Proprietes > Debloquer avant d'extraire.

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
