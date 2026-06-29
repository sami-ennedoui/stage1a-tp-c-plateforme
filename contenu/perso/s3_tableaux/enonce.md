# S3, la longueur d'une chaîne et le zéro de fin

C'est l'exercice 9 du BE, les tableaux de caractères. Une chaîne comme "Salut" est un tableau de caractères, et le C ajoute tout seul un caractère spécial `\0` à la fin pour marquer où elle s'arrête. C'est pour ça que "Salut", cinq lettres, occupe six cases.

Tu dois écrire `longueur`, qui renvoie le nombre de caractères d'une chaîne, sans compter ce `\0`. Tu parcours le tableau case par case et tu t'arrêtes quand tu tombes sur `\0`.

Indice : un compteur à zéro, et une boucle qui avance tant que la case courante n'est pas `\0`.

La porte : quand `longueur` renvoie 5 pour "Salut", l'exemple du sujet, et la bonne valeur pour d'autres chaînes, le test sort en succès.
