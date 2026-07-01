# Exercice 7, les structures de contrôle

C'est l'exercice 7 du BE. Il porte sur les structures de contrôle du C : les boucles et les tests. Tu écris un petit jeu qui fait deviner un nombre.

Le programme cache un nombre fixé à l'avance, ici 56. Il demande une proposition à l'utilisateur, la lit avec `scanf`, puis compare. Si le nombre proposé est plus grand que le nombre caché, il affiche `C'est plus petit`. S'il est plus petit, il affiche `C'est plus grand`. Tant que l'utilisateur n'a pas trouvé, le programme redemande une proposition.

Pour redemander jusqu'à la bonne réponse, sers-toi d'une boucle `do while` : le corps s'exécute au moins une fois, puis se répète tant que le nombre proposé est différent du nombre caché. À l'intérieur, un test `if ... else if` choisit le bon message. Compte aussi le nombre d'essais dans une variable que tu incrémentes à chaque tour.

Quand la bonne valeur est trouvée, le programme sort de la boucle et affiche le nombre trouvé et le nombre d'essais.

Le jeu est interactif. La porte lui envoie les propositions 50, puis 75, puis 56. Avec un nombre caché à 56, cela donne d'abord `C'est plus grand`, puis `C'est plus petit`, puis la victoire en 3 essais.

La porte vérifie que le programme affiche bien le titre, les deux indices `C'est plus grand` et `C'est plus petit` dans le bon ordre, et qu'il annonce la victoire en 3 essais.
