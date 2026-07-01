# BRIEFING WINDOWS — tester et packager le TP C

> ## MISE À JOUR 2026-07-01 (LIS CECI EN PREMIER, remplace la version précédente)
>
> **Le parcours à tester et à packager est `be_c`, et il a été refait pour ÊTRE le vrai BE.**
>
> - `perso` (inventé) est abandonné. **`be_c`** est maintenant **le BE fidèle** : les **14 exercices dans
>   l'ordre exact des slides** (Exercice 1 à 13 + équation du second degré), en mode programme complet.
>   **Énoncés = questions exactes du BE** (recopiées dans `contenu/be_c/QUESTIONS-BE-exactes.md`), corrigés
>   fidèles. 4 exercices manquants ont été **créés** (Ex3 menu switch/case, Ex5 rectangle de tirets, Ex6
>   rectangle multi-sous-programmes, Ex7 struct rectangle). Les dossiers ont été **renumérotés** selon le BE.
>   Les 14 séances sont **vérifiées** (corrigé ouvre la porte, starter échoue), sur `version-projet`.
> - **Bonus séparé** : 3 anciens exercices hors-BE (pointeurs, cercle) ont été sortis dans un parcours
>   **`contenu/bonus_pointeurs/`** (`--parcours bonus_pointeurs`). Ils ne font PAS partie du BE.
> - **Hidden level / approfondissement** : certaines séances ont un fichier **`approfondissement.md`** (le
>   « en plus » que le corrigé officiel faisait au-delà de l'énoncé, ex : `ex01_types` = `sizeof` + troncature
>   du char). **À implémenter dans l'appli** : révéler `approfondissement.md` **une fois la porte de base
>   passée** (niveau caché débloqué à la validation). Pour l'instant le fichier existe mais l'appli ne
>   l'affiche pas encore : c'est le prochain bout d'UI côté toi.
> - **Ce que tu dois faire côté Windows** :
>   1. `git pull` (ou merge `version-projet` dans ta branche `windows-packaging-tuteur-multimoteur`).
>   2. `lancer.bat` + bundle + PyInstaller sur **`--parcours be_c`** (plus `perso`). La copie `plateforme/`
>      du bundle doit inclure tout **`contenu/be_c/`** (14 sous-dossiers + `parcours.json` + les
>      `approfondissement.md`). `--add-data` PyInstaller doit inclure `contenu/be_c`.
>   3. Teste sur Windows : la fenêtre s'ouvre sur `be_c`, chaque exercice compile, la porte s'ouvre avec le
>      corrigé et pas avec le starter.
> - **Écarts VALIDÉS tels quels (c'est une démo), ne les "corrige" pas** : `ex08_tableaux` (ancien Ex5) a son
>   débordement neutralisé pour ne pas planter ; `ex10_fichier` a une ligne de confirmation en plus pour la
>   porte ; les fragments `sortie_attendue` sont déjà sans accent (console Windows cp1252).
> - Ton travail packaging + tuteur multi-moteur (`claude`/`codex`) **reste bon**, combine-le avec `be_c` et
>   repointe le lancement. Garde l'utilisateur dans la boucle.

Ce fichier permet à une **nouvelle session Claude Code, lancée sur le PC Windows**, de
reprendre seule. Lis-le en entier avant d'agir. Rendus en **français**. **Garde l'utilisateur
dans la boucle pour chaque décision.** Ne fais **aucun commit ni push sans accord explicite**.

## 1. Contexte (le minimum à savoir)

- Stage 1A, ENSEEIHT, sujet « intégrer l'IA générative dans l'apprentissage de la
  programmation ». Phase 3 = « apprendre un langage avec l'IA ».
- Cette plateforme (appli **PyQt6**) est un **TP d'apprentissage du C**, sur les exercices
  d'introduction du cours (types, opérateurs, pointeurs, tableaux, sous-programmes).
- **Le Snake est ABANDONNÉ** (trop compliqué, c'était l'autre BE du cours). Les parcours
  `hybride` et `projet` existent dans le code mais sont **parqués**. **On ne travaille QUE le
  parcours `perso`.**
- Principe « contenu = donnée » : un parcours est un dossier sous `contenu/`, lancé par
  `--parcours <nom>`. Ici, **toujours `--parcours perso`**.
- Le parcours `perso` = **4 séances isolées avec l'IA**, sur de vrais exercices du BE C :
  - `s1_types` : un `char` tient sur 1 octet, troncature (320 rangé dans un char redonne 64) ;
  - `s2_pointeurs` : passage par adresse, `permuter_valeur` fait tourner 3 valeurs ((3,5,1)→(1,3,5)) ;
  - `s3_tableaux` : longueur d'une chaîne via le `\0` de fin ("Salut"→5) ;
  - `s4_sousprog` : un sous-programme `calculer_y` qui renvoie `a*x+b` ((4,3,2)→11).
- Plan d'ensemble en 3 temps : (1) perso relu/affiné **[FAIT]**, (2) **version Windows portable
  [TON JOB]**, (3) remarques du 2A.
- **Sur ce PC Windows, tu as l'admin et la sub Claude Code de l'utilisateur**, donc le tuteur IA
  (`claude -p`) fonctionne ici. Chez le 2A il sera optionnel (voir §7).

## 2. Ton objectif

1. **Valider** que le parcours perso tourne vraiment sur Windows : la fenêtre PyQt6 s'ouvre,
   gcc compile, les 4 portes passent avec le corrigé et échouent avec le starter, le tuteur répond.
2. **Corriger** ce qui casse (voir les pièges §5).
3. **Produire un `.exe` PyInstaller** pour un lancement propre côté 2A (voir §6, avec sa réserve).
4. **Élaguer** le poids (826 Mo → beaucoup moins) **après** validation, puis re-tester (§8).

## 3. Ce qui est DÉJÀ fait dans le code (ne pas refaire)

- **Correctif portabilité dans `executeur.py`** : sous Windows, gcc (MinGW) produit `prog.exe`
  alors que le code lançait `prog`. La fonction `_nom_binaire()` ajoute `.exe` si `os.name == "nt"`,
  utilisée par `_compiler_et_lancer` et `porte_programme`. **C'est en place.**
- Côté parcours perso : filtre anti-solution du tuteur réparé (clé normalisée, code seul sans
  commentaire ni espaces, dans `tuteur_ia.py`), starters allégés (consigne uniforme), forme des
  énoncés uniformisée. **2 tests TDD** ajoutés dans `tests/test_tuteur_ia.py`.
- **57 tests verts sous Linux.** Sous Windows, relance-les pour confirmer :
  `python -m pytest tests/ -q` (installe pytest si besoin). Note : `test_parcours_projet` (Snake,
  parqué) a un test sensible à l'ordre qui flotte parfois, **hors périmètre**.

## 4. Assembler le bundle portable, **nativement sur Windows**

La version Linux du bundle (826 Mo) **n'est pas transférée** : tu ré-assembles ici, c'est plus
propre. Toutes les pièces se téléchargent. Versions validées :

- **Python embeddable 3.12.10** :
  `https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip`
- **PyQt6 (wheels win_amd64)** :
  `python -m pip download --only-binary=:all: --platform win_amd64 --python-version 3.12 PyQt6 -d wheels`
  → récupère PyQt6 6.11 (abi3), PyQt6-Qt6 6.11.1 (py3-none), PyQt6-sip 13.11.1 (cp312).
  **Le runtime MSVC (`msvcp140.dll`, `vcruntime140*`) est DANS le wheel `PyQt6-Qt6`** (dossier
  `PyQt6/Qt6/bin`), ne le cherche pas ailleurs.
- **w64devkit 2.8.0 x64** (gcc 16.1, archive 7z auto-extractible) :
  `https://github.com/skeeto/w64devkit/releases/download/v2.8.0/w64devkit-x64-2.8.0.7z.exe`
  (double-clic pour extraire, ou `7z x`).

Structure cible :

```
TP-C-perso/
├── lancer.bat          (copie depuis packaging/ de ce dépôt)
├── diagnostic.bat      (copie depuis packaging/)
├── README-2A.txt       (copie depuis packaging/)
├── python/             décompresser python-3.12.10-embed-amd64.zip ici
│                        PUIS éditer python312._pth pour qu'il contienne EXACTEMENT :
│                            python312.zip
│                            .
│                            Lib\site-packages
│                            import site
│                        PUIS décompresser les 3 wheels (ce sont des zip) dans python/Lib/site-packages/
├── w64devkit/          extraire le 7z ici → doit donner w64devkit/bin/gcc.exe
└── plateforme/         copier depuis ce dépôt : tous les *.py + le dossier contenu/perso/
                        NE PAS copier : tests/, SPEC-*, PLAN-*, contenu/hybride, contenu/projet,
                        contenu/tp_c, .git, __pycache__
```

`lancer.bat` ajoute `w64devkit\bin` et `python` au PATH puis lance
`python\python.exe plateforme\atelier_snake.py --parcours perso`.

## 5. Tester (l'étape qui tranche)

1. **`diagnostic.bat`** doit afficher : gcc 16.1, Python 3.12.10, **`PyQt6 OK`**, et le chemin de
   `claude` (présent sur ce PC). Si `PyQt6 OK` ne s'affiche pas, c'est l'assemblage Python/wheels.
2. **`lancer.bat`** : la fenêtre doit s'ouvrir sur le parcours perso. Pour chaque séance, colle le
   corrigé (il est dans `contenu/perso/<sX>/corrige.c`), compile : la porte doit s'ouvrir. Le
   `starter.c` ne doit PAS passer la porte. Teste le **bouton tuteur** : il doit répondre **sans
   donner la solution** (le filtre masque les lignes du corrigé ; aux crans N0-N2 il reste
   socratique, au cran N3 il est libre, c'est voulu).
3. Observe et note tout ce qui cloche.

Note importante sur Wine : sous Linux, l'import PyQt6 échoue **sous Wine** parce que Wine
n'implémente pas complètement l'UCRT (`api-ms-win-crt-*`). Sur un vrai Windows 10/11 l'UCRT est
**natif**, donc l'import **doit** marcher. Si jamais il ne marche pas ici, c'est un vrai problème
à diagnostiquer (pas un effet Wine).

## 6. PyInstaller (.exe) — avec sa réserve

Tu as l'admin, donc installe un vrai Python (pas l'embeddable) + `pip install pyinstaller pyqt6`,
puis depuis `plateforme/` :
`pyinstaller --noconfirm --windowed --name TP-C-perso --add-data "contenu/perso;contenu/perso" atelier_snake.py`
(adapter ; `--windowed` = sans console). Pense à forcer `--parcours perso` au lancement.

**Réserve à ne pas oublier** : PyInstaller fige **Python + PyQt6**, mais **PAS gcc**. Le
compilateur w64devkit doit rester **un dossier à côté du .exe**, ajouté au PATH au démarrage.
Donc le `.exe` simplifie le lancement de l'appli mais **ne supprime pas** le dossier `w64devkit`.
**Décide avec l'utilisateur** si le `.exe` en vaut la peine vs le dossier portable + `lancer.bat`.

## 7. Le tuteur IA chez le 2A (déjà tranché, pour info)

- Vérifié sur `claude.com/pricing` : **pas d'essai gratuit** Claude Code. Pro = 20 $/mois (inclut
  Claude Code), le plan gratuit ne l'inclut pas.
- Le bundle marche **sans tuteur** : `tuteur_ia.py` dégrade proprement si `claude` est absent du
  PATH. Le 2A allume le tuteur s'il a son propre Claude Code, sinon il fait les 4 séances sans IA.
- **Ne pas** tenter Ollama (petit modèle local CPU = mauvaise qualité pour un tuteur, écarté).

## 8. Élaguer (APRÈS validation, et re-tester à chaque coupe)

Poids actuel 826 Mo : w64devkit 587, Qt 239. Coupes sûres :
- `python/Lib/site-packages/PyQt6/Qt6/qml` (~21M), `.../Qt6/translations` (~11M),
- `w64devkit/share` (~46M, docs/man), les binaires `gdb*`, le Fortran (`gfortran*`, `f951`, libgfortran).
Plus risqué (tester après chaque coupe) : DLL Qt inutilisées (garder Qt6Core/Gui/Widgets + leurs
dépendances), le C++ si le perso reste C-only. **Relance `lancer.bat` après chaque coupe.**

## 9. Conventions et état du projet

- Français, pas d'em-dash dans les rendus, pas d'emoji. Garder l'utilisateur dans la boucle.
- Pas de commit/push sans accord.
- Si le vault Obsidian est accessible sur ce PC, l'état vit dans
  `Stage1A/00-Pilotage/Reprise-session.md` (§Phase 3) et `Stage1A/00-Pilotage/Handoff.md`. Sinon,
  **ce fichier suffit pour démarrer**. À la fin, redonne à l'utilisateur un compte rendu de ce qui
  marche, ce qui a été corrigé, et le poids final.

Les fichiers `lancer.bat`, `diagnostic.bat`, `README-2A.txt` prêts à l'emploi sont dans
`packaging/` de ce dépôt (encodés en CRLF).
