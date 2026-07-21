# Exercice 1, les types de variables

1 - Créez un programme principal où vous déclarez et initialisez une variable de type `short`, une variable de type `int`, une variable de type `char`, une variable de type `float` et une variable de type `double`. (slides 8 à 10)

2 - Affichez chaque variable avec le `printf` et le spécificateur de format qui lui correspond (`%c`, `%f`, `%i`, `%d`, `%e`). Ce sont les mêmes spécificateurs qu'on utilise avec `scanf` pour la saisie, mais ici les valeurs sont fixées dans le code : il n'y a rien à lire au clavier. (slides 23 à 25)

Affiche une ligne par variable, préfixée par le nom du type, par exemple :

```
short : 12
int : 260
char : A
float : 3.500000
double : 2.500000e+00
```

Les valeurs sont libres, choisis celles que tu veux : la porte ne vérifie pas les nombres, seulement que chaque type est affiché avec le bon format (`%d`/`%i` pour `short` et `int`, `%c` pour `char`, `%f` pour `float`, `%e` pour `double`).
