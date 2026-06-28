# Plan d'implémentation — Version « projet » de l'atelier Snake

> **Pour les exécutants agentiques :** SOUS-COMPÉTENCE REQUISE, utiliser
> superpowers:subagent-driven-development pour exécuter ce plan tâche par tâche.
> Les étapes sont en cases à cocher pour le suivi.

**But :** une version « projet » où l'étudiant complète les vrais sous-programmes
du projet Snake dans un espace de travail persistant, puis compile le projet et
joue. En démo, les corrigés sont chargés et le jeu se lance.

**Architecture :** un seul moteur, la version est le parcours chargé. La version
projet ajoute un espace de travail projet persistant et une porte « compiler et
jouer le vrai projet ». Le jeu jouable doit d'abord être écrit dans la structure
du projet, c'est la Phase A.

**Pile technique :** C avec SDL3 et le moteur Outils du projet, build via gcc et
pkg-config. Plateforme en PyQt6, Python 3.14.

## Contraintes globales
- Rendus et commentaires en français. Pas de tiret cadratin, pas de parenthèses
  bourrées de mots-clés, pas d'emoji. En prose, sujet et verbe.
- On ne modifie ni les libs SDL3, ni l'archive d'origine. Tout se fait sur des
  copies sous `~/scratch-stage1a/snake-sdl/`.
- Exécuter et pas seulement compiler. Chaque porte se prouve en exécutant.
- Pas de ligne Co-Authored-By dans les commits.
- Référence qui marche : `~/scratch-stage1a/snake-sdl/linux-build/SNAKE/jeu_demo.c`,
  Snake complet jouable. Les tâches de portage s'en inspirent, adapté aux
  sous-programmes `SP_` du projet.
- Squelette du projet : `linux-build/SNAKE/`, fichiers à compléter
  `GestionMenuParametrage.c`, `GestionGraphismes.c`, `InitialisationJeu.c`,
  `GestionJeu.c` (`Update_Jeu` vide), boucle `main.c` qui ne câble que l'Accueil.
- Constantes jeu dans `ConfigurationJeu.h` : `TAILLE_CELLULE 40`, grille 20 par 20,
  `TAILLE_INITIALE 20`, `PAS_DE_DEPLACEMENT 4`.
- Enum d'états dans `MesTypes.h` : `MENU_ACCEUIL, MENU_PARAMETRAGE,
  MENU_COULEUR_SNAKE, MENU_COULEUR_STADE, MENU_COULEUR_BORD, MENU_JEU, QUITTER_MENU`.

---

## Structure de fichiers

**Phase A, le corrigé projet jouable.** On crée une copie de travail du projet
qui sera remplie pour devenir la cible jouable.
- Créer : `~/scratch-stage1a/snake-sdl/projet-corrige/SNAKE/` (copie de
  `linux-build/SNAKE/`, sans `jeu_demo.c` ni `shooter.c`).
- Modifier dans cette copie : `VariablesGlobales.h/.c`, `InitialisationJeu.c/.h`,
  `GestionJeu.c`, `GestionMenuParametrage.c`, `GestionGraphismes.c/.h`, `main.c`,
  `build.sh`.
- Tests logiques C : `projet-corrige/tests_logique/` (harnais à bouchons par
  sous-programme testable).

**Phase B, le parcours projet dans la plateforme.** Tout sous
`~/scratch-stage1a/snake-sdl/plateforme/`.
- Créer : `espace_projet.py` (espace de travail persistant), `contenu/projet/`
  (un dossier par étape avec `meta.json`, `enonce.md`, harnais de porte),
  `contenu/projet/parcours.json`.
- Modifier : `chemins.py` (racines de contenu multiples), `executeur.py`
  (`porte_logique`, `construire_et_jouer_projet`), `fenetre.py` (mode projet,
  charge et sauve depuis l'espace, bouton « Compiler et jouer »),
  `atelier_snake.py` (sélecteur `--parcours`).
- Le parcours actuel devient `contenu/hybride/`.

---

## PHASE A — Corrigé projet jouable

### Tâche A0 : copie de travail et build nettoyé

**Files:**
- Create: `~/scratch-stage1a/snake-sdl/projet-corrige/` (copie de `linux-build/SNAKE/`)
- Modify: `projet-corrige/SNAKE/build.sh`

**Interfaces:**
- Produces: un dossier `projet-corrige/SNAKE/` qui compile en `snake` avec le menu
  Accueil seul, sans fichier à `main` parasite.

- [ ] **Étape 1 :** copier `linux-build/SNAKE/` vers `projet-corrige/SNAKE/`, puis
  supprimer `jeu_demo.c` et `shooter.c` de la copie.
- [ ] **Étape 2 :** dans `build.sh`, garder l'exclusion de `main_start.c`, `save.c`,
  `myLib.c`. Vérifier que `jeu_demo.c` et `shooter.c` ne sont plus présents.
- [ ] **Étape 3 :** lancer `bash build.sh`. Attendu : compile, produit `snake`.
- [ ] **Étape 4 :** lancer `./snake` brièvement en capture auto si possible, sinon
  vérifier le démarrage sans crash. Attendu : la fenêtre du menu Accueil s'ouvre.
- [ ] **Étape 5 :** commit.

### Tâche A1 : structures de données du serpent

**Files:**
- Modify: `projet-corrige/SNAKE/VariablesGlobales.h`, `VariablesGlobales.c`

**Interfaces:**
- Produces: les variables globales du jeu, serpent et pomme, avec les types et
  noms repris de `jeu_demo.c`. Par exemple un tableau de segments, la longueur
  courante, la direction, la position de la pomme.
- Consumes: les types de `MesTypes.h` (`Direction`, structures de position).

- [ ] **Étape 1 :** lire `jeu_demo.c` pour relever les structures de jeu et leur
  usage. Lister les globales nécessaires.
- [ ] **Étape 2 :** déclarer ces globales dans `VariablesGlobales.h` en `extern` et
  les définir dans `VariablesGlobales.c`, en français, noms cohérents avec le projet.
- [ ] **Étape 3 :** `bash build.sh`. Attendu : compile toujours, globales non encore
  utilisées tolérées par les flags `-Wno-unused`.
- [ ] **Étape 4 :** commit.

### Tâche A2 : initialisation du jeu

**Files:**
- Modify: `projet-corrige/SNAKE/InitialisationJeu.c`, `InitialisationJeu.h`
- Test: `projet-corrige/tests_logique/test_init.c`

**Interfaces:**
- Produces: `void SP_Initialisation_Partie(void)` qui place le serpent au centre à
  `TAILLE_INITIALE` segments et pose une première pomme dans la grille.
- Consumes: les globales de A1, les constantes de `ConfigurationJeu.h`.

- [ ] **Étape 1 :** écrire `test_init.c`, un harnais qui bouchonne les fonctions
  Outils graphiques, appelle `SP_Initialisation_Partie`, et vérifie par assertions
  la longueur initiale, la position centrale du serpent, et une pomme dans les
  bornes de la grille. Sortie non nulle si une assertion casse.
- [ ] **Étape 2 :** lancer le harnais, attendu échec, fonction absente.
- [ ] **Étape 3 :** écrire `SP_Initialisation_Partie` en portant la logique d'init
  de `jeu_demo.c`.
- [ ] **Étape 4 :** relancer le harnais, attendu sortie 0.
- [ ] **Étape 5 :** commit.

### Tâche A3 : déplacement du serpent dans Update_Jeu

**Files:**
- Modify: `projet-corrige/SNAKE/GestionJeu.c` (`Update_Jeu`)
- Test: `projet-corrige/tests_logique/test_deplacement.c`

**Interfaces:**
- Produces: dans `Update_Jeu`, le décalage du corps puis le déplacement de la tête
  selon la direction courante. Réutilise le principe du décalage de tableau de P3.
- Consumes: globales de A1, `SP_Gestion_Clavier` déjà fourni pour la direction.

- [ ] **Étape 1 :** écrire `test_deplacement.c`. Initialise une partie, fixe une
  direction, appelle le pas de déplacement, vérifie que la tête a avancé d'une
  cellule dans la bonne direction et que chaque segment a pris la place du précédent.
- [ ] **Étape 2 :** lancer, attendu échec.
- [ ] **Étape 3 :** implémenter le décalage et le déplacement dans `Update_Jeu`, en
  séparant la logique pure du rendu pour qu'elle soit testable sans graphique.
- [ ] **Étape 4 :** relancer, attendu sortie 0.
- [ ] **Étape 5 :** commit.

### Tâche A4 : croissance sur la pomme

**Files:**
- Modify: `projet-corrige/SNAKE/GestionJeu.c`
- Test: `projet-corrige/tests_logique/test_croissance.c`

**Interfaces:**
- Produces: quand la tête atteint la pomme, la longueur augmente et une nouvelle
  pomme apparaît hors du serpent.
- Consumes: la logique de déplacement de A3.

- [ ] **Étape 1 :** écrire `test_croissance.c`. Place la pomme devant la tête, fait
  un pas, vérifie longueur plus un et nouvelle pomme dans les bornes, hors du corps.
- [ ] **Étape 2 :** lancer, attendu échec.
- [ ] **Étape 3 :** implémenter la croissance et la repose de pomme.
- [ ] **Étape 4 :** relancer, attendu sortie 0.
- [ ] **Étape 5 :** commit.

### Tâche A5 : collision et fin de partie

**Files:**
- Modify: `projet-corrige/SNAKE/GestionJeu.c`
- Test: `projet-corrige/tests_logique/test_collision.c`

**Interfaces:**
- Produces: détection de collision avec les murs et avec soi, qui passe l'état à la
  fin de partie.
- Consumes: la logique de A3 et A4.

- [ ] **Étape 1 :** écrire `test_collision.c`. Deux cas, la tête sort de la grille,
  et la tête rencontre un segment du corps. Chacun doit marquer la fin de partie.
- [ ] **Étape 2 :** lancer, attendu échec.
- [ ] **Étape 3 :** implémenter les deux collisions et le passage en fin de partie.
- [ ] **Étape 4 :** relancer, attendu sortie 0.
- [ ] **Étape 5 :** commit.

### Tâche A6 : menus Paramétrage et couleur

**Files:**
- Modify: `projet-corrige/SNAKE/GestionMenuParametrage.c`, plus les sous-programmes
  des menus couleur dans le même fichier ou un fichier dédié cohérent.

**Interfaces:**
- Produces: `SP_Structure_Menu_Parametrage`, `SP_Gestion_Evenements_Menu_Parametrage`,
  et les structures et événements des menus couleur, qui changent l'état via le
  pointeur, sur le modèle de `GestionMenuAcceuil.c`.
- Consumes: le menu Paramétrage déjà écrit dans
  `plateforme/contenu/jalon1_parametrage/corrige.c`, à intégrer.

- [ ] **Étape 1 :** intégrer le corrigé Paramétrage existant dans le fichier projet.
- [ ] **Étape 2 :** écrire les menus couleur par analogie, chaque bouton mène au bon
  état ou applique la couleur choisie.
- [ ] **Étape 3 :** `bash build.sh`, attendu compile.
- [ ] **Étape 4 :** commit.

### Tâche A7 : dispatch graphismes et dessins du jeu

**Files:**
- Modify: `projet-corrige/SNAKE/GestionGraphismes.c`, `GestionGraphismes.h`

**Interfaces:**
- Produces: `SP_Gestion_Graphismes(int etatMenu)` qui dessine selon l'état, et les
  sous-programmes de dessin du stade, du serpent et de la pomme.
- Consumes: les globales du jeu, le moteur Outils de dessin.

- [ ] **Étape 1 :** câbler le dispatch pour tous les états, Accueil, Paramétrage,
  couleurs, Jeu.
- [ ] **Étape 2 :** écrire le dessin du stade, du serpent et de la pomme en portant
  `jeu_demo.c`. Tenir compte du bug connu de couleur de cercle, fixer la couleur
  soi-même.
- [ ] **Étape 3 :** `bash build.sh`, attendu compile.
- [ ] **Étape 4 :** commit.

### Tâche A8 : boucle de jeu dans main

**Files:**
- Modify: `projet-corrige/SNAKE/main.c`

**Interfaces:**
- Produces: la boucle gère tous les états. En `MENU_JEU`, elle lit le clavier via
  `SP_Gestion_Clavier`, avance le jeu via `Update_Jeu`, dessine, et gère la fin de
  partie. Les autres états routent leurs événements vers le bon gestionnaire.
- Consumes: tout ce qui précède.

- [ ] **Étape 1 :** câbler les événements par état, et l'appel jeu en `MENU_JEU`.
- [ ] **Étape 2 :** appeler l'initialisation de partie à l'entrée du jeu.
- [ ] **Étape 3 :** `bash build.sh`, attendu compile.
- [ ] **Étape 4 :** commit.

### Tâche A9 : capstone, le jeu se lance et se joue

**Files:**
- Modify si besoin pour un mode auto de preuve, sans toucher la logique.

**Interfaces:**
- Produces: la preuve que le projet assemblé est jouable.

- [ ] **Étape 1 :** `bash build.sh`, lancer `snake`, jouer quelques pas en auto ou
  piloter des événements clavier injectés, capturer une image ou un gif du serpent
  qui bouge et mange.
- [ ] **Étape 2 :** vérifier visuellement, serpent visible, déplacement, croissance.
- [ ] **Étape 3 :** commit, joindre la capture au rapport.

---

## PHASE B — Parcours projet dans la plateforme

Cette phase se précisera au grain fin une fois la Phase A figée, car les
frontières exactes des fichiers et des trous des starters en dépendent. Tâches et
interfaces cadrées dès maintenant.

### Tâche B1 : racines de contenu multiples et sélecteur de parcours

**Files:** Modify `chemins.py`, `atelier_snake.py`, déplacer le contenu actuel vers
`contenu/hybride/`.
**Interfaces:** Produces, `chemins.contenu_racine(nom)` qui renvoie le dossier du
parcours. `atelier_snake.py` accepte `--parcours projet|perso|hybride`, défaut un
petit menu de choix au lancement.
- [ ] Test, lancer avec chaque valeur charge le bon parcours. Smoketest vert.

### Tâche B2 : espace de travail projet persistant

**Files:** Create `espace_projet.py`.
**Interfaces:** Produces, `EspaceProjet` avec `initialiser()` qui copie le squelette
projet dans un dossier de session, `lire_fichier(nom)`, `ecrire_fichier(nom, code)`,
`reinitialiser()`. Le squelette source est le projet avec les trous, le corrigé
sert au mode démo.
- [ ] Test, écrire un fichier puis le relire rend le même contenu. Réinitialiser
  restaure le squelette.

### Tâche B3 : porte logique sur l'espace

**Files:** Modify `executeur.py`.
**Interfaces:** Produces, `porte_logique(etape, code, espace)` qui pose le `code` dans
le fichier de l'étape au sein de l'espace, compile avec le harnais de l'étape,
exécute, et renvoie un `Resultat` dont le code de sortie fait foi.
- [ ] Test, le corrigé d'une étape passe sa porte, le starter ne la passe pas.

### Tâche B4 : compiler et jouer le projet

**Files:** Modify `executeur.py`.
**Interfaces:** Produces, `construire_et_jouer_projet(espace)` qui lance `build.sh`
sur l'espace puis ouvre `snake` depuis l'espace. Renvoie l'erreur de compilation
si le build échoue.
- [ ] Test, sur un espace pré-rempli avec les corrigés, le build réussit et le
  binaire existe. Lancement vérifié à l'écran.

### Tâche B5 : mode projet dans la fenêtre

**Files:** Modify `fenetre.py`.
**Interfaces:** En parcours projet, l'éditeur charge le fichier de l'étape depuis
l'espace, la sauvegarde écrit dans l'espace, un bouton « Compiler et jouer » appelle
B4. La porte d'une étape appelle B3. Le capstone a pour porte le build réussi.
- [ ] Test, smoketest du mode projet. Charger le corrigé d'une étape puis ouvrir la
  suivante conserve l'accumulation dans l'espace.

### Tâche B6 : contenu des étapes projet

**Files:** Create `contenu/projet/` avec un dossier par étape A2 à A9, plus le jalon 0,
chacun avec `meta.json` (dont `fichier_edite`), `enonce.md`, le harnais de porte, et
le corrigé issu de la Phase A. `contenu/projet/parcours.json` dans l'ordre du plan.
**Interfaces:** Consomme les fichiers finis de la Phase A comme corrigés, et leurs
versions à trou comme starters.
- [ ] Test, le parcours se charge, chaque étape s'ouvre, le sélftest projet passe
  toutes les portes avec les corrigés.

### Tâche B7 : vérification de bout en bout en démo

**Files:** none, vérification.
**Interfaces:** Prouve l'objectif. En mode démo projet, charger tous les corrigés
remplit l'espace, « Compiler et jouer » build et lance un Snake jouable.
- [ ] Test, dérouler la démo, capturer le jeu lancé depuis l'espace rempli.

---

## Auto-revue
- Couverture spec, Phase A couvre le corrigé jouable, Phase B couvre l'espace
  persistant, les portes, le sélecteur de parcours, le capstone. Conforme.
- Pas de placeholder dans la Phase A, chaque tâche a un test exécutable ou un build
  vérifié. La Phase B est cadrée en interfaces, à détailler après la Phase A, ce qui
  est annoncé explicitement.
- Cohérence des noms, `SP_Initialisation_Partie`, `Update_Jeu`, `SP_Gestion_Graphismes`,
  `porte_logique`, `construire_et_jouer_projet`, `EspaceProjet`, repris tels quels
  entre tâches.
