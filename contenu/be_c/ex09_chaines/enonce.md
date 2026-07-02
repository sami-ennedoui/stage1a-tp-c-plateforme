# Exercice 9, les tableaux de caractères

C'est l'exercice 9 du BE. Il continue sur les tableaux, cette fois avec une chaîne de caractères.

1. Déclare un tableau de 6 `char` et initialise-le avec une chaîne de caractères `char chaine[6]="Salut"`. Le calculateur insère automatiquement le caractère `\0` dans la case 5 (`[0]=S, [1]=a, [2]=l, [3]=u, [4]=t, [5]=\0`) pour indiquer la fin de la chaîne de caractères. Il faut donc prévoir dans la taille du tableau une case de plus pour ce caractère spécial.
2. Affiche la chaîne de caractères en utilisant `%s` dans la fonction `printf`.
3. Affiche l'adresse à laquelle est stocké le tableau.
4. Réalise une interaction clavier pour changer la chaîne de caractères stockée (`scanf` avec un `%s`).

Comme pour un tableau d'entiers, le nom du tableau vaut l'adresse de sa première case.

Dans la plateforme, la saisie clavier est fixée à l'avance, le programme reçoit le mot `Hello`.

La porte vérifie l'affichage de la chaîne de départ puis de la chaîne saisie. Ta sortie doit contenir exactement ces lignes (recopie les libellés tels quels ; le reste, invites et saisie, est libre) :

```
La chaine contient = Salut
Veuillez entrer une nouvelle chaine
La nouvelle chaine contient = Hello
```
