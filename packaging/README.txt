TP C, les exercices d'introduction au langage C
===============================================

A quoi ca sert
--------------
Les 14 exercices d'introduction au langage C : types et taille des types,
operateurs, structures, pointeurs, tableaux, structures de controle,
sous-programmes, passage par adresse, lecture d'un fichier, et l'equation du
second degre. Pour chaque exercice tu ecris un petit programme complet, tu
cliques pour compiler et tester, et une porte s'ouvre quand la sortie est
correcte.

Prerequis
---------
Un Windows 64 bits. Rien d'autre a installer pour le coeur de l'atelier :
Python et le compilateur gcc sont deja dans ce dossier.

Comment lancer
--------------
  1. Decompresse ce dossier ou tu veux (le Bureau, par exemple).
  2. Double-clique sur lancer.bat.
La fenetre s'ouvre sur le premier exercice.

Si quelque chose cloche, lance d'abord diagnostic.bat : il verifie que gcc,
Python et l'affichage repondent, et affiche un message clair.

Comment ca marche, exercice par exercice
----------------------------------------
  - Lis l'enonce en haut de la fenetre.
  - Ecris ton programme dans l'editeur.
  - Clique sur "Compiler" pour voir les erreurs du compilateur (elles
    pointent la ligne et la colonne exactes).
  - Clique sur "Tester" pour franchir la porte : si elle s'ouvre, c'est
    gagne ; sinon le message t'explique ce qui manque dans ta sortie.
Les exercices sont independants : fais-les dans l'ordre que tu veux.

Quand tu valides un exercice, un niveau cache peut se debloquer : un
bandeau vert apparait sous le titre ENONCE et un approfondissement
s'ajoute au bas de l'enonce (il va un peu plus loin que la consigne).

Le tuteur IA (optionnel)
------------------------
Un bouton d'aide peut te repondre pendant un exercice, sans jamais donner la
solution toute faite : il repond court et direct, nomme ce qui cloche et le
concept en jeu, mais te laisse ecrire la correction (il masque les lignes du
corrige). Il est OPTIONNEL. Les exercices fonctionnent entierement sans lui.

Pour l'activer, il faut un outil IA en ligne de commande, installe et
connecte avec ton propre compte. Deux sont reconnus :
  - Claude Code   (commande "claude")
  - Codex         (commande "codex")
Installe et connecte celui pour lequel tu as un compte. S'il est present sur
ta machine (dans le PATH) et connecte, le tuteur s'allume tout seul au
lancement.

  - Verifier qu'il repond : ouvre un terminal et tape, selon le cas,
      claude -p "dis bonjour"
      codex exec "dis bonjour"
    Si tu obtiens une reponse, le tuteur fonctionnera.
  - Si les deux outils sont presents, Claude est choisi par defaut. Pour
    forcer l'un ou l'autre, definis la variable d'environnement ATELIER_AI
    a "claude" ou a "codex" avant de lancer lancer.bat.

Note : ces outils sont payants et n'ont pas d'essai gratuit dedie. Sans aucun
des deux, l'atelier reste pleinement utilisable, simplement sans l'aide IA.
