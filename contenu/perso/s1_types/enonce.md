# S1, les types et la taille d'un octet

C'est l'exercice 1 du BE, les types de variables. Un `char` ne tient que sur un octet, huit bits, et ne peut représenter que des valeurs de -128 à 127. Si tu y ranges un nombre trop grand, il ne garde que les huit derniers bits. Le sujet le montre avec 320, qui une fois rangé dans un `char` se relit 64.

Tu dois écrire `valeur_dans_char`, qui range l'entier `n` dans un `char` puis renvoie ce qu'on relit. Pour un `n` plus grand que ce qu'un octet peut tenir, la valeur change, et c'est tout l'intérêt de l'exercice.

Indice : il suffit de ranger `n` dans une variable de type `char`, puis de la renvoyer. Le C fait la troncature tout seul.

La porte : quand `valeur_dans_char` renvoie la bonne valeur tronquée pour plusieurs nombres, dont 320 qui donne 64, le test sort en succès.
