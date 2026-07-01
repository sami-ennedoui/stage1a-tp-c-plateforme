# Exercice 9, les sous-programmes

C'est l'exercice 9 du BE. Tu découvres les sous-programmes avec une fonction qui rend une valeur. Le thème est l'équation d'une droite.

Une droite s'écrit `y = a * x + b`. Le coefficient `a` est le coefficient directeur, le coefficient `b` est l'ordonnée à l'origine. Connaissant `a`, `b` et une abscisse `x`, on veut calculer l'ordonnée `y`.

Écris une fonction `calcul_ordonnee` qui reçoit `a`, `b` et `x`, calcule `a * x + b` et rend le résultat au programme principal. Les trois paramètres sont en entrée, la fonction rend la valeur avec `return`.

Dans le programme principal, initialise `a` à 4, `b` à 3 et `x` à 2. Appelle la fonction, récupère la valeur rendue dans une variable, puis affiche l'ordonnée avec `printf`. Avec ces valeurs, tu obtiens `y = 4 * 2 + 3 = 11`.

La porte vérifie que le programme affiche l'ordonnée `y = 11.000000` pour `x = 2.000000`.
