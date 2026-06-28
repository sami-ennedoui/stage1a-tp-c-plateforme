# Spec — Version « projet » de l'atelier Snake

## But
Une version « projet » de la plateforme. L'étudiant complète, dans l'ordre, les
vrais sous-programmes du projet Snake. À la fin, on compile le vrai projet et on
joue. En mode démo, on charge les corrigés et on lance le jeu tout de suite.

## Constat de départ, vérifié dans l'archive
Le projet livré est un squelette. Seul le menu Accueil est câblé dans `main.c`.
La logique du serpent n'est écrite nulle part dans la structure du projet :
`Update_Jeu` dans `GestionJeu.c` est vide, `InitialisationJeu.c` est vide, le
dispatch graphique ne gère que l'Accueil. Le seul Snake jouable est `jeu_demo.c`,
un fichier autonome avec son propre `main`, qui contourne la structure du projet.

Conséquence directe. « Jouer le jeu que l'étudiant a écrit » impose d'abord
d'écrire le jeu complet DANS la structure du projet. C'est la fondation et la
plus grosse brique. Sans elle il n'y a pas de cible vers laquelle converger.

## Architecture, un moteur et des parcours au choix
Le moteur actuel reste. La version n'est que le parcours chargé. Un sélecteur au
lancement, `--parcours projet|perso|hybride`, défaut un petit menu de choix. Le
parcours actuel, perso plus jalon, devient le parcours « hybride ». On réutilise
thème, coloration, LSP clangd, tuteur bridé, portes de preuve.

## Nouveauté clé, un espace de travail projet persistant
Aujourd'hui une étape charge un starter isolé et le teste contre des bouchons.
La version projet a besoin d'autre chose. Chaque session garde une COPIE du
projet que l'étudiant remplit étape après étape. Une étape édite un fichier réel
de cette copie, et la sauvegarde écrit le fichier. Le code s'accumule, c'est lui
qui devient le jeu final.

- Compiler et jouer : on compile toute la copie via un `build.sh` nettoyé, et on
  lance `snake` depuis la copie, car les assets sont en chemin relatif.
- Mode démo : la copie est pré-remplie avec les corrigés, le jeu est jouable
  immédiatement. Le bouton « Charger le corrigé » par étape reste comme aujourd'hui.

## Phase A, le corrigé projet jouable
Écrire un Snake complet et jouable dans la structure du projet, en s'appuyant sur
`jeu_demo.c` comme référence qui marche, porté vers les sous-programmes `SP_` et le
moteur Outils du projet.

- Menu Paramétrage, structure et événements. Déjà écrit, à intégrer.
- Menus couleur, serpent, stade, bord.
- Dispatch graphismes pour tous les états dans `SP_Gestion_Graphismes`.
- `InitialisationJeu`, création du serpent et placement de la pomme.
- `Update_Jeu` dans `GestionJeu.c`, décalage du corps qui réutilise P3, déplacement
  de la tête selon la direction, croissance sur la pomme, collision murs et soi,
  fin de partie.
- `main.c`, câbler les états manquants, Paramétrage, couleurs, Jeu, et dans l'état
  Jeu appeler `SP_Gestion_Clavier` puis `Update_Jeu` puis le rendu.
- `build.sh` nettoyé pour exclure du binaire `snake` les fichiers à `main` parasite,
  `jeu_demo.c` et `shooter.c`.
- Vérification, le jeu se compile et tourne. Preuve à l'écran via un mode auto et
  une capture.

## Phase B, le parcours projet et les portes
Chaque étape est un sous-programme réel. Le starter à trou est dérivé du corrigé en
effaçant la cible, le corrigé est le fichier rempli. Ordre pédagogique vers un jeu
jouable.

1. Jalon 0, prise en main, rencontre le bug de casse `mesTypes.h` au compilateur.
2. Menu Paramétrage, structure et événements.
3. Dispatch graphismes des menus.
4. Menus couleur, serpent, stade, bord.
5. Initialisation du jeu.
6. Déplacement du serpent, décalage du corps, réutilise P3.
7. Croissance.
8. Collision et fin de partie.
9. Boucle de jeu dans `main`, capstone, on lance et on joue.

Chaque étape garde une porte exécutable. Là où le graphique n'est pas requis, un
harnais bouchonne les fonctions Outils et exécute la logique, comme le jalon 1
existant. Le capstone, la porte est « le jeu compile et se lance ».

## Portes de preuve
- Logique sans graphique, un harnais à bouchons exécute le déplacement, la
  croissance, la collision, et vérifie par assertions.
- Capstone, build du projet complet puis lancement de `snake`.

## Vérification, exécuter et pas seulement compiler
- Phase A, lancer le jeu assemblé en mode auto, capturer une image ou un gif.
- Portes logiques, tests C exécutés réellement.
- Capstone dans la plateforme, build puis lancement de `snake`, prouvé à l'écran.

## Hors périmètre
- Les versions perso seule et hybride restent des parcours existants ou à venir,
  pas refaites ici.
- Pas de modification des libs SDL3 ni de l'archive d'origine, on travaille sur la
  copie.

## Risques
- Porter `jeu_demo.c` dans la structure `SP_` est la grosse inconnue, atténuée par
  un corrigé de référence qui marche déjà.
- Le rendu a un bug connu, `SP_Dessiner_Cercle_Texture` ignore sa couleur car la
  ligne est commentée. À garder comme piège d'audit ou à corriger selon l'étape.
