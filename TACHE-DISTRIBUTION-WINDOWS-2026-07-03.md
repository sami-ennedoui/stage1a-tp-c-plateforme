# Tâche distribution pour le Claude Windows, 2026-07-03

Écrit depuis le poste Linux. Problème réel remonté par Sami, plus une décision de sa
part. Watchdog Linux réarmé sur ta branche, réponds par commit.

## Le problème

Sami a essayé de lancer l'atelier sur un **PC de l'école, sans droits admin**. Tout le
`diagnostic.bat` renvoie des échecs. Diagnostic posé et confirmé par Sami : il n'avait
que le **dépôt git** sur ce PC, pas le bundle. Or le dépôt ne contient ni `TP-C-perso.exe`
ni `w64devkit`, seulement le source et les scripts. La charge utile de ~800 Mo n'a jamais
été sur git, elle n'existe que sur son PC perso. Donc rien à exécuter sur le PC école.
Ce n'est pas un bug de code, c'est un trou de distribution.

Au passage, le `README.md` à la racine du dépôt induit en erreur : il dit « Python et gcc
sont déjà fournis dans ce dossier », ce qui est vrai dans le bundle mais faux dans le
dépôt. Quelqu'un qui parcourt le dépôt croit avoir un dossier lançable.

## La décision de Sami

Distribution par **Release GitHub**. Un zip du bundle exécutable, publié en Release du
dépôt, qu'il téléchargera au navigateur sur le PC école en étant connecté à son compte
GitHub (dépôt privé, donc téléchargeable avec son login, sans gh sur la machine école).

## À faire

1. **Fabriquer un zip prêt à lancer** du bundle assemblé : `TP-C-perso.exe`, `w64devkit`,
   `lancer.bat`, `diagnostic.bat`, le contenu `be_c`, et le README utilisateur convivial
   à la racine du zip. Vérifie sur ton poste qu'en extrayant ce zip dans un dossier neuf
   puis en double-cliquant `lancer.bat`, la fenêtre s'ouvre. C'est le test qui compte.

2. **Publier la Release** sur le dépôt via `gh release create` (tu es le seul avec gh
   authentifié et le bundle en local). Un tag simple, par ex. `v0.1-demo`. Attache le zip
   comme asset. Rends-moi l'URL de la Release et la taille finale du zip.

3. **Corriger le `README.md` racine du dépôt** pour ne plus tromper : il doit dire que le
   dépôt est le **source**, que pour *utiliser* l'atelier on télécharge le bundle prêt à
   lancer depuis les Releases, et que pour le *reconstruire* on suit `RECONSTRUCTION.md`.
   Garde le README convivial actuel (celui destiné à l'utilisateur) **dans le zip**, à la
   racine du bundle, là où « Python et gcc sont fournis dans ce dossier » est vrai.

4. **Secondaire, apprécié mais pas bloquant** : élaguer `w64devkit` pour alléger le
   téléchargement, retirer gdb, gfortran, les docs, les outils inutiles, en gardant gcc,
   as, ld et les en-têtes/libs C. **Mais seulement après avoir vérifié que les 14
   exercices de `be_c` compilent toujours à travers la porte.** Ne casse pas la chaîne
   d'outils pour gagner des Mo. Si tu n'es pas sûr, publie d'abord le zip complet qui
   marche, on élaguera après.

## Réserve honnête à garder en tête

Même une fois le zip téléchargé et extrait sur le PC école, on ne sait pas encore si la
politique de sécurité de l'école laisse tourner un exe non signé sans admin. C'est le
prochain palier, on le testera quand Sami aura le bundle en main. Ta tâche ici, c'est
juste de rendre le bundle récupérable et lançable depuis une machine normale.

Pousse sur ta branche quand la Release est en ligne, mon watchdog me préviendra.
