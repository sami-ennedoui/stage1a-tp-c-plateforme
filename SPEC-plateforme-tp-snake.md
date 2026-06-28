# Spec — Plateforme du TP Snake en C

Date : 2026-06-28
Emplacement du code : `~/scratch-stage1a/snake-sdl/plateforme/` (hors du vault, c'est un prototype d'expérience).

## 1. But

Une application de bureau où un étudiant de 1A travaille le TP Snake en C avec l'aide
d'une IA, sans jamais croire l'IA sur parole. Le cœur du stage tient en une phrase : une
IA écrit du code vite, il a l'air juste, la compétence c'est de le mettre à l'épreuve.
La plateforme rend ce geste concret. Elle fait compiler et exécuter du vrai code, elle
ouvre la vraie fenêtre du jeu, elle bride l'aide de l'IA au début et la débride à mesure
que l'étudiant prouve qu'il a compris.

Le résultat déjà validé du stage guide tout le reste : la preuve à l'écran bat la
croyance. Donc rien n'est acquis tant que ce n'est pas exécuté.

## 2. Périmètre de la v1

Tranche verticale, pas tout le contenu. La plateforme complète de bout en bout, branchée
sur deux étapes seulement :

- `perso_P1`, le pointeur IN/OUT en C pur, en mode test fourni.
- `jalon1_parametrage`, le menu Paramétrage du projet Snake, en mode test à écrire.

Les corrigés et les tests de ces deux étapes existent déjà et passent, dans
`~/scratch-stage1a/snake-sdl/TP-build/`. La v1 réutilise ce matériau. Avec une étape de
chaque mode, la tranche verticale prouve les deux pipelines de test d'un coup.

Hors périmètre v1, repoussé en v2 et après : les étapes P2, P3 et les jalons 2 à 7, le
verdict IA optionnel en plus de la porte déterministe, le déploiement multi-poste.

## 3. Principe d'architecture : le contenu est de la donnée

La plateforme ne connaît aucune étape en dur. Une étape du TP est un dossier de données
sous `contenu/`. Ajouter une étape plus tard, c'est déposer un dossier, jamais rouvrir le
code de l'application. C'est ce qui rend la stratégie « tranche verticale puis on remplit »
réellement peu coûteuse.

### 3.1 Modèle d'une étape

Un dossier `contenu/<id_etape>/` contient un `meta.json` et des fichiers selon le mode.

`meta.json` :

```json
{
  "id": "jalon1_parametrage",
  "titre": "Jalon 1 — Menu Paramétrage",
  "type": "jalon",                 // "perso" | "jalon"
  "mode": "test_a_ecrire",         // "test_fourni" | "test_a_ecrire"
  "recette": "jalon_test",         // "perso" | "jalon_test"  (recette de compilation de la porte)
  "cran_debloque": 2,              // le cran de débridage que cette étape débloque une fois passée
  "noeud_cours": "Décomposition fonctionnelle, paramétrage",
  "fichier_edite": "GestionMenuParametrage.c"
}
```

Fichiers présents selon le mode :

- mode `test_fourni` : `enonce.md`, `starter.c`, `corrige.c`, `tests.c`.
- mode `test_a_ecrire` : `enonce.md`, `starter.c`, `corrige.c`, `corrige_buggue.c`, plus
  un `stubs.c` si la recette en a besoin pour compiler hors SDL. L'étudiant produit
  lui-même son `test_eleve.c`, il n'est pas livré.

`corrige.c` n'est jamais montré à l'étudiant. Il sert au tuteur comme contexte, au filtre
de solution, et à juger les tests que l'étudiant écrit.

## 4. Les deux modes de test et la porte de preuve

La porte de preuve d'une étape est toujours un résultat déterministe d'exécution, jamais
un avis. L'IA n'ouvre aucune porte, elle aide seulement.

### 4.1 Mode test fourni (étapes perso)

L'étudiant remplit `starter.c`. La plateforme compile son code avec `tests.c`, exécute, et
lit le code de sortie du programme. Sortie nulle, tout passe, la porte s'ouvre. C'est le
cas de `perso_P1`, où l'étudiant découvre le concept du pointeur et n'a pas encore à
écrire de test.

### 4.2 Mode test à écrire (jalons du projet)

L'étudiant écrit le code et, en plus, écrit son propre test. Un test faible passe sur
n'importe quel code, donc on ne peut pas faire confiance au test tel quel. La plateforme
le juge d'abord, en deux temps cachés :

1. Compiler `corrige.c` avec `test_eleve.c`, exécuter. Le test doit PASSER. S'il échoue,
   le test accuse à tort un code correct, message « ton test rejette un code correct ».
2. Compiler `corrige_buggue.c` avec `test_eleve.c`, exécuter. Le test doit ÉCHOUER, c'est
   à dire attraper le bug planté. S'il passe, message « ton test laisse passer un bug,
   renforce-le », sans jamais dire lequel.

Un test qui passe l'étape 1 et échoue à l'étape 2 est reconnu solide. Alors seulement la
plateforme lance `test_eleve.c` contre le code de l'étudiant, et ce résultat est la vraie
porte de son code. C'est le cas de `jalon1_parametrage`.

Le bug planté de `corrige_buggue.c` est écrit à la main, une faute logique plausible. Pour
le jalon 1, par exemple, deux associations clic vers état échangées.

## 5. Débridage de l'IA, débloqué par les portes

L'IA tutrice a quatre crans :

- N0, elle explique le concept seulement, jamais le code de l'étape.
- N1, elle peut donner un squelette ou une analogie, pas la solution.
- N2, elle peut proposer un candidat que l'étudiant doit justifier ou vérifier.
- N3, libre.

L'étudiant démarre à N0. Passer la porte d'une étape débloque le cran indiqué par
`cran_debloque`. L'étudiant peut redescendre sous le cran débloqué pour moins d'aide, il
ne peut jamais monter au-dessus tant qu'il n'a pas prouvé. C'est la thèse de la Vision A,
l'aide se mérite par la preuve.

Le tuteur est un bouton « Demander de l'aide ». Le prompt envoyé au moteur dépend du cran
courant. Par-dessus le prompt, un filtre déterministe masque dans la réponse les lignes
qui donneraient la solution de l'étape, repérées à partir du corrigé. Le bridage n'est pas
qu'une consigne au modèle, c'est aussi ce garde-fou structurel.

## 6. Les deux couches de preuve, le test et le jeu

Pour un jalon, deux boutons distincts :

- Tester, qui lance la porte de preuve décrite en section 4 et rend un résultat
  déterministe. C'est elle qui fait foi.
- Lancer le jeu, qui compile le vrai projet avec le fichier de l'étudiant à la place du
  sien et ouvre la vraie fenêtre SDL. L'étudiant voit son code bouger à l'écran. Cette
  couche est la récompense visible, pas la porte.

Pour une étape perso, pas de jeu, seulement Compiler et Tester sur un programme C autonome.

## 7. Recettes de compilation

Trois recettes, encapsulées dans `executeur.py`, désignées par `meta.json` :

- `perso` : `gcc` sur le code de l'étudiant plus `tests.c`, sans projet, sans SDL.
- `jalon_test` : `gcc` sur le fichier visé, ou le corrigé, ou le corrigé buggé, plus le
  test, plus `stubs.c` qui bouchonne les fonctions Outils et SDL. Pas de SDL, c'est la
  logique pure qu'on teste, comme le fait déjà `test_jalon1_logique.c`.
- `jalon_jeu` : la compilation complète du projet avec `pkg-config sdl3 sdl3-ttf sdl3-image`,
  le fichier de l'étudiant inséré dans une copie de travail du projet. Cette recette ne
  vient pas du champ `recette` du `meta.json`, elle est déclenchée par le bouton Lancer le
  jeu pour toute étape de type jalon.

La plateforme travaille sur une copie du projet, jamais sur l'archive d'origine. La copie
de référence est celle déjà en place dans `~/scratch-stage1a/snake-sdl/linux-build/SNAKE/`.

Protocole de réussite d'un test : le programme de test sort avec un code nul si tout
passe, non nul sinon, et imprime des lignes lisibles à côté. L'exécuteur se fie au code de
sortie comme signal de vérité et affiche les lignes. Un `printf` de débogage ne casse donc
pas le protocole.

## 8. Interface

Une seule fenêtre PyQt6.

- À gauche, la liste des étapes avec leur état, verrouillée, en cours, faite, l'étape
  courante en surbrillance. C'est la carte du cours.
- Au centre haut, l'énoncé de l'étape en markdown rendu.
- Au centre, l'éditeur du fichier starter avec coloration C. En mode test à écrire, un
  second onglet ou volet pour le `test_eleve.c`.
- En bas, une console qui montre la sortie du compilateur et le résultat des tests, sans
  rien cacher. L'erreur du compilateur est elle-même pédagogique, le bug de casse
  `mesTypes.h` et la dérive SDL2 vers SDL3 se lisent là.
- Les boutons Compiler, Tester, et Lancer le jeu pour un jalon.
- Le panneau Tuteur, avec l'indicateur de cran courant et le bouton Demander de l'aide.

## 9. Découpage du code

Chaque pièce a une responsabilité unique et se teste seule, sans écran.

- `modele_etape.py` : charge une étape depuis son dossier de données. Expose `Etape` et
  `charger_parcours(dossier_contenu) -> list[Etape]` ordonnée.
- `executeur.py` : compile et exécute, rend un résultat. Aucune UI. Expose
  `porte_perso(etape, code_eleve)`, `juger_test(etape, test_eleve)` qui rend si le test est
  solide, `porte_jalon(etape, code_eleve, test_eleve)`, et `lancer_jeu(etape, code_eleve)`.
  Les trois recettes de compilation vivent ici.
- `tuteur_ia.py` : fabrique le prompt selon le cran, appelle le moteur IA en sous-processus,
  applique le filtre de solution. Aucune UI. Moteur interchangeable par variable
  d'environnement, `claude -p` par défaut.
- `progression.py` : charge et sauve `progression.json`, gère le déverrouillage des étapes
  et le cran disponible.
- `fenetre.py` : la fenêtre PyQt6 qui câble tout. Les appels au moteur IA tournent dans un
  fil séparé pour ne pas figer la fenêtre.
- `contenu/perso_P1/` et `contenu/jalon1_parametrage/` : les données des deux étapes de la v1.
- `atelier_snake.py` : le point d'entrée, plus les modes `--selftest` et `--smoketest`.

## 10. État et progression

Un `progression.json` retient les étapes faites et le plus haut cran atteint, d'une
session à l'autre. Au lancement, la plateforme rouvre sur l'état sauvegardé.

```json
{ "etapes_faites": ["perso_P1"], "cran_max": 1 }
```

## 11. Robustesse

- Erreur de compilation, affichée telle quelle dans la console, jamais masquée.
- Test qui dépasse un délai, processus tué et signalé.
- Moteur IA absent, le bouton d'aide le dit, tout le reste, compiler, tester, lancer,
  marche quand même.
- Échec du lancement du jeu, la sortie d'erreur est montrée.

## 12. Stratégie de vérification

On ne s'arrête pas au « ça compile ». On exécute le comportement réel.

- `--selftest`, sans écran : pour chaque étape, le corrigé passe sa porte, et une version
  cassée échoue. En mode test à écrire, on vérifie en plus qu'un test de référence solide
  passe le corrigé et attrape le bug planté, et qu'un test mou est bien rejeté.
- Test du filtre : le filtre masque la solution et laisse passer le reste.
- `--smoketest` : la fenêtre se construit sans s'afficher.
- Vérification manuelle : lancer l'appli, faire P1 puis Jalon 1, confirmer que passer la
  porte de P1 débloque N1 puis celle du jalon débloque N2, et que Lancer le jeu ouvre bien
  la fenêtre SDL.

## 13. Ce qui reste intact

L'archive d'origine du projet Snake ne bouge pas, avec ses bugs gardés pour le TP. La
plateforme travaille sur la copie de build. Le matériau déjà vérifié de `TP-build/` est
réutilisé, pas réécrit.

## Annexe A — Catalogue des tests de référence et bugs plantés

Source : l'ancien projet Snake console de Picot et Rhahla, qui spécifiait chaque
sous-programme par un triplet pré-condition, post-condition, scénario de test. Ce sont des
spécifications papier, transcrites ici en assertions exécutables. L'ancien projet n'a pas
de SDL, sa logique est pure, donc ces tests ne dépendent d'aucun affichage, ce qui colle à
la recette `jalon_test`.

Chaque entrée donne le concept, le test de référence solide attendu au `--selftest`, et le
bug planté que le `corrige_buggue.c` porte. Un test solide passe le corrigé et attrape le
bug, un test mou laisse le bug passer.

### A.1 Menu Paramétrage (jalon 1, mode test à écrire, étape de la v1)

Le sous-programme associe le bouton cliqué à un état de menu.

- Test de référence : clic sur le bouton 0 mène à l'état attendu, clic 1 à un autre, clic 3
  au retour, et un clic hors bouton, indice -1, laisse l'état inchangé.
- Bug planté : deux associations clic vers état échangées. Le test épingle chaque
  association et attrape l'échange. Un test qui vérifie seulement que l'état a changé le rate.

### A.2 Déplacement de la tête (concept P3, d'après SP_MVT_PASSIF)

Pré, tête en (10,10), direction droite. Post, tête en (11,10).

- Test de référence : après `avancer`, `corps[0].x == 11 && corps[0].y == 10`.
- Bug planté : dx et dy inversés, ou la tête avance de deux cases.

### A.3 Décalage du corps (cœur de P3, d'après SP_EVOLUTION_SNAKE)

Corps `{(5,5),(4,5),(3,5)}`, on avance à droite, attendu `{(6,5),(5,5),(4,5)}`. Chaque
élément prend la place de son voisin côté tête.

- Test de référence : comparer chaque case du corps après `avancer`, pas seulement la tête.
- Bug planté : la boucle de décalage tourne dans le mauvais sens, `for(i=0;i<n;i++)`, ce
  qui recopie la tête sur tout le corps. Le test qui compare chaque case l'attrape, le test
  qui ne regarde que la tête le laisse passer.
- Cas vitrine retenu pour la présentation tuteurs, voir la note en bas. C'est l'erreur
  classique du tableau décalé, visible à l'écran, le serpent s'effondre sur sa tête.

### A.4 Allongement (d'après SP_ALLONGE_SNAKE)

Taille 5, on mange une pomme, attendu taille 6, l'ancienne queue conservée.

- Test de référence : `taille == 6` après ingestion, et la case ajoutée n'écrase aucune
  case existante.
- Bug planté : le `taille++` oublié, ou la nouvelle case écrase une case du corps.

### A.5 Collision et fin de partie (d'après SP_GAME_OVER)

- Test de référence : tête au bord, fin vraie. Tête sur son propre corps, fin vraie. Tête
  au milieu sans contact, fin fausse.
- Bug planté : le test du mur en `<` au lieu de `<=`, un décalage d'une case qui laisse la
  tête sortir sans déclencher la fin.

Note présentation tuteurs : illustrer le geste du stage avec le cas A.3. Il montre d'un
seul exemple l'erreur que l'IA écrit volontiers, un test faible qui la laisse passer face à
un test fort qui l'attrape, et une preuve à l'écran nette. La rédaction de la présentation
est faite plus tard, après la plateforme.
