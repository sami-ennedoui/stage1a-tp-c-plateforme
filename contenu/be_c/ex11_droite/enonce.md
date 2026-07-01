# Exercice 11, les sous-programmes

C'est l'exercice 11 du BE. Tu découvres les sous-programmes avec une fonction qui rend une valeur.

Réalise un sous-programme permettant de calculer, à partir d'une équation du type `y = a*x + b`, la valeur `y` connaissant `x`. La définition complète du sous-programme est donnée ci-dessous. Illustre son utilisation dans un programme principal.

```
//============================================================
// nom :  fonction calculer_y
// sémantique : calcul de la coordonnée y connaissant x
// paramètres :
// a  : IN réel – valeur du coefficient directeur
// b : IN réel – valeur du de l'ordonnée à l'origine
// x : IN réel – valeur de l'abscisse
// y : OUT réel - valeur de l'ordonnée
// pré-condition : a, b et x initialisés
// post-condition : aucune
//============================================================
// Tests : a=4, b=3, x=2, solutions y = 11
// ============================================================

FONCTION calculer_y  (a,b,x ( IN) : réel ) RETOURNE réel y

Variable y : reel

DEBUT Algorithme

y = a * x + b

Retourner y

FIN Algorithme
```

Dans le programme principal, initialise `a` à 4, `b` à 3 et `x` à 2. Appelle la fonction, récupère la valeur rendue dans une variable, puis affiche l'ordonnée. Avec ces valeurs, tu obtiens `y = 4 * 2 + 3 = 11`.

La porte vérifie que le programme affiche l'ordonnée `y = 11.000000` pour `x = 2.000000`.
