# Exercice 1, les types de variables

C'est l'exercice 1 du BE. Tu écris un programme complet qui déclare une variable de chaque type de base du C, un `short`, un `int`, un `char`, un `float` et un `double`, et qui les initialise. Revois les slides 8 à 10 du cours pour les types.

Affiche ensuite la taille de chaque type avec `sizeof` et `%d`, sous la forme `La taille d'un char est 1 octet(s)`.

Le point intéressant est le `char`. Il ne tient que sur un octet, donc il ne code qu'une valeur entre -128 et 127. Initialise un `char` à 320 et affiche sa valeur avec `%d`. Le compilateur ne garde que les huit derniers bits, et tu obtiens 64.

Pour l'affichage, sers-toi de `printf` avec le bon format pour chaque type. Revois les slides 23 à 25, `%c`, `%f`, `%i`, `%d`, `%e`.

La porte vérifie les tailles des types et que le `char` initialisé à 320 donne bien 64.
