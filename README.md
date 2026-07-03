# TP C, atelier d'introduction au langage C

Atelier de bureau pour Windows : 14 exercices d'introduction au langage C, avec
compilation et test integres, et un tuteur IA optionnel.

![Vue d'ensemble de l'atelier](captures/01-vue-ensemble.png)

## Ce depot

Ce depot contient le **code source** de l'atelier. Il ne contient **pas** le bundle
lancable : Python et le compilateur gcc (environ 800 Mo une fois assembles) ne sont pas
versionnes sur git. **Cloner le depot ne suffit donc pas pour lancer l'atelier.**

## Utiliser l'atelier (sans rien installer)

Telechargez le bundle pret a lancer depuis la page des Releases :

<https://github.com/sami-ennedoui/stage1a-tp-c-plateforme/releases>

1. Telechargez le fichier `.zip` de la derniere release (connexion a votre compte
   GitHub requise, le depot est prive).
2. Decompressez-le ou vous voulez (le Bureau, par exemple).
3. Double-cliquez sur `lancer.bat`.

Le bundle est **autonome** : Python et gcc sont dedans, rien d'autre a installer, pas
de droits admin requis. Le guide utilisateur complet est fourni dans le zip
(`README.md`) et lisible ici : **[GUIDE.md](GUIDE.md)**.

## Reconstruire le bundle depuis le source

Voir **[RECONSTRUCTION.md](RECONSTRUCTION.md)** : construction de l'exe (PyInstaller),
assemblage du bundle, regeneration de la documentation.

## Structure du depot

- Modules Python de l'atelier a la racine : `fenetre.py`, `executeur.py`,
  `tuteur_ia.py`, `modele_etape.py`, `progression.py`, `theme.py`, etc.
- `contenu/be_c/` : les 14 exercices (enonces, corriges, tests).
- `packaging/` : point d'entree du bundle (`entree_be_c.py`) et lanceurs
  (`lancer.bat`, `diagnostic.bat`).
- `outils/` : bancs de test du correcteur et du tuteur, et le pipeline de
  documentation (`captures_doc.py`, `doc_pdf.py`).
- `tests/` : tests unitaires.
- **[GUIDE.md](GUIDE.md)** : le guide utilisateur (aussi livre dans le bundle).
- **[RECONSTRUCTION.md](RECONSTRUCTION.md)** : mode d'emploi de reconstruction.
