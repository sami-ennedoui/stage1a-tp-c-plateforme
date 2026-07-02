# Exercice 12, procédure avec passage par valeur

C'est l'exercice 12 du BE. Tu écris une procédure avec passage par valeur. Une procédure est un sous-programme qui ne rend pas de valeur, son type de retour est `void`. Elle agit par ce qu'elle affiche.

Réalise une procédure, en mettant en œuvre un passage par valeur, afin de calculer et d'afficher le produit et la somme de deux valeurs entières `val_a`, `val_b`. La définition complète de ce sous-programme est donnée ci-dessous. Illustre l'utilisation de cette procédure dans un programme principal.

```
//============================================================
// nom :  procedure calculer_produit_somme
// sémantique : calcul de la somme et du produit de 2 nombres
// paramètres :
// a : IN réel – nombre 1
// b : IN réel – nombre 2
// pré-condition : a et b initialisés
// post-condition : somme et produit affichés
//============================================================
// Tests : a=3 b=2 ; solutions produit = 6 , somme  = 5
//============================================================

PROCEDURE calculer_produit_somme  ( a,b  (IN) : réel )

Variables : produit, somme : réels

DEBUT Algorithme

produit = a * b
somme = a + b

Afficher la valeur de produit
Afficher la valeur de somme

FIN Algorithme
```

Dans le programme principal, initialise `a` à 3 et `b` à 2, puis appelle la procédure. Les deux paramètres sont passés par valeur, la procédure reçoit une copie des nombres. Avec ces valeurs, la somme vaut 5 et le produit vaut 6.

La porte vérifie que le programme affiche la somme et le produit. Ton programme doit afficher exactement ces deux lignes (recopie les libellés tels quels) :

```
La somme de a+b = 5
Le produit de a*b = 6
```
