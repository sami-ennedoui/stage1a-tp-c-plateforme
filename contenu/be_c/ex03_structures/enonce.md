# Exercice 3, les structures de variables

C'est l'exercice 3 du BE. Tu découvres la structure, une façon de regrouper plusieurs valeurs liées sous un seul nom. Avec `typedef struct` tu crées un nouveau type `type_cercle` qui contient quatre champs de type `float` : le rayon, le diamètre, l'aire et le périmètre d'un cercle.

Dans le `main`, déclare une variable `mon_cercle` de ce type. Fixe son rayon à 5, puis calcule ses autres champs. Le diamètre vaut deux fois le rayon. L'aire vaut 3.1416 multiplié par le rayon au carré. Le périmètre vaut 3.1416 multiplié par le diamètre. Tu accèdes à chaque champ avec le point, par exemple `mon_cercle.rayon`.

Affiche ensuite les quatre champs avec `printf` et le format `%f`. Avec un rayon de 5 tu obtiens une aire de 78.540001 et un périmètre de 31.416000.

Demande alors un nouveau rayon au clavier et lis-le avec `scanf("%f", &(mon_cercle.rayon))`. Recalcule le diamètre, l'aire et le périmètre à partir de ce nouveau rayon, puis affiche encore une fois les quatre champs. Ici le programme reçoit 10, donc l'aire recalculée vaut 314.160004.

La porte vérifie les valeurs du premier cercle, rayon 5 et aire 78.540001, ainsi que celles obtenues après lecture du nouveau rayon, rayon 10 et aire 314.160004.
