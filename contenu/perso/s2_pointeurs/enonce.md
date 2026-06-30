# S2, permuter trois variables par adresse

C'est l'exercice 13 du BE, le passage par adresse. Tu dois écrire une procédure `permuter_valeur` qui reçoit trois entiers et fait tourner leurs valeurs. La première prend la valeur de la troisième, la troisième prend celle de la deuxième, et la deuxième prend l'ancienne valeur de la première.

Comme la procédure doit modifier les variables de l'appelant, elle reçoit leurs adresses, des pointeurs, et travaille avec l'étoile pour atteindre les valeurs derrière.

Indice : garde d'abord la première valeur dans une variable temporaire, sinon tu l'écrases ; puis décale les autres et pose la temporaire à la fin.

La porte : avec val_a, val_b et val_c valant 3, 5 et 1, on doit obtenir 1, 3 et 5, exactement le test du sujet. Quand c'est le cas, le test sort en succès.
