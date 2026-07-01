# Exercice 11, les sous-programmes

C'est l'exercice 11 du BE. Tu continues sur les sous-programmes, cette fois avec des paramètres en entrée et en sortie. Le thème est la permutation de valeurs.

Quand une procédure doit modifier les variables du programme principal, le passage par valeur ne suffit pas, la procédure ne reçoit qu'une copie. Il faut passer les adresses des variables et travailler avec des pointeurs. La procédure reçoit alors les adresses et modifie directement les cases mémoire d'origine.

Écris une procédure `permutation` qui reçoit les adresses de trois entiers `val_a`, `val_b` et `val_c`, et qui permute leurs valeurs de façon circulaire. Après l'appel, l'ancienne valeur de `val_c` passe dans `val_a`, l'ancienne valeur de `val_a` passe dans `val_b`, et l'ancienne valeur de `val_b` passe dans `val_c`. Sers-toi d'une variable temporaire pour ne rien perdre.

Dans le programme principal, initialise `a` à 3, `b` à 5 et `c` à 1. Affiche les trois valeurs, appelle la procédure en envoyant les adresses avec l'opérateur `&`, puis affiche de nouveau. Tu dois passer de `3 5 1` à `1 3 5`.

La porte vérifie que le programme affiche `AVANT PERMUTATION  3 5 1` puis `APRES PERMUTATION  1 3 5`.
