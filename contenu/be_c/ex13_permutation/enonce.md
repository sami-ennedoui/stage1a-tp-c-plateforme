# Exercice 13, les sous-programmes

C'est l'exercice 13 du BE. Tu continues sur les sous-programmes, cette fois avec un passage par adresse. Quand une procédure doit modifier les variables du programme principal, le passage par valeur ne suffit pas, la procédure ne reçoit qu'une copie. Il faut passer les adresses des variables et travailler avec des pointeurs.

Réalise une procédure mettant en œuvre un passage par adresse permettant de permuter circulairement trois entiers `val_a`, `val_b`, `val_c` qui lui sont donnés en arguments. La définition de ce sous-programme est donnée ci-dessous. Illustre l'utilisation de cette procédure dans un programme principal.

```
//============================================================
// nom :  permuter_valeur
// sémantique : permute circulairement les 3 valeurs qui lui sont envoyés
// paramètres :
// val_a : IN/OUT réel – valeur du nombre 1
// val_b : IN/OUT réel – valeur du nombre 2
// val_c : IN/OUT réel -  valeur du nombre 3
// pré-condition : val_a, val_b et val_c initialisés
// post-condition : aucune
//============================================================
// Tests : val_a =3 , val_b =5, val_c = 1  ; solutions :  val_a =1 , val_b =3, val_c = 5
//============================================================

PROCEDURE permuter_valeur   (val_a , b , c  (IN / OUT) : réel )

Variable temp : réel

DEBUT Algorithme

temp =  val_a ;
val_a =  val_c ;
val_c =  val_b ;
val_b =  temp ;

FIN Algorithme
```

Dans le programme principal, initialise `a` à 3, `b` à 5 et `c` à 1. Affiche les trois valeurs, appelle la procédure en envoyant les adresses avec l'opérateur `&`, puis affiche de nouveau. Tu dois passer de `3 5 1` à `1 3 5`.

La porte vérifie que le programme affiche `AVANT PERMUTATION  3 5 1` puis `APRES PERMUTATION  1 3 5`.
