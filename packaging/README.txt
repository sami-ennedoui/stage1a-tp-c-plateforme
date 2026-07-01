TP C, quatre seances pour apprendre les bases du C
==================================================

A quoi ca sert
--------------
Quatre courtes seances, guidees, pour decouvrir les bases du langage C :
  1. les types et la taille d'un octet (le debordement d'un char) ;
  2. le passage par adresse avec des pointeurs ;
  3. les chaines de caracteres et le zero de fin ;
  4. un premier sous-programme qui renvoie une valeur.
Tu ecris une fonction, tu cliques pour compiler et tester : une porte
s'ouvre quand ta reponse est juste.

Prerequis
---------
Un Windows 64 bits. Rien d'autre a installer pour le coeur de l'atelier :
Python et le compilateur gcc sont deja dans ce dossier.

Comment lancer
--------------
  1. Decompresse ce dossier ou tu veux (le Bureau, par exemple).
  2. Double-clique sur lancer.bat.
La fenetre s'ouvre sur la premiere seance.

Si quelque chose cloche, lance d'abord diagnostic.bat : il verifie que gcc,
Python et l'affichage repondent, et affiche un message clair.

Comment ca marche, seance par seance
------------------------------------
  - Lis l'enonce en haut de la fenetre.
  - Complete la fonction dans l'editeur.
  - Clique sur "Compiler et tester". Si la porte s'ouvre, c'est gagne ;
    sinon le message t'explique ce qui ne va pas.
Les seances sont independantes : fais-les dans l'ordre que tu veux.

Le tuteur IA (optionnel)
------------------------
Un bouton d'aide peut te repondre pendant une seance, sans jamais donner la
solution toute faite : il reste socratique et masque les lignes du corrige.
Il est OPTIONNEL. Les quatre seances fonctionnent entierement sans lui.

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
