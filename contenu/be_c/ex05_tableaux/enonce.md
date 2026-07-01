# Exercice 5, les tableaux

C'est l'exercice 5 du BE. Tu écris un programme complet qui manipule un tableau d'entiers.

Déclare un tableau de 5 cases initialisé avec les valeurs 1, 5, 10, 15 et 20. Affiche d'abord l'adresse du tableau lui-même. Le nom du tableau vaut l'adresse de sa première case. Affiche ensuite, pour chaque case de 0 à 4, son adresse et sa valeur.

Le point intéressant est que les cases se suivent en mémoire. D'une case à la suivante l'adresse augmente de 4 octets, la taille d'un `int`. Les cases d'un tableau sont donc contiguës.

Le dernier point est un avertissement. En C rien ne vérifie que tu restes dans les bornes du tableau. Tu peux écrire dans une case au delà des 5 cases utiles, par exemple la case 10. Le langage te laisse faire sans rien signaler, mais tu écris alors dans une zone mémoire qui ne t'appartient pas. C'est une source classique de bugs. DANGER.

Les adresses affichées changent à chaque exécution, c'est normal, seule leur progression compte.

La porte vérifie que la case 0 vaut 1, que la case 4 vaut 20, et que le programme signale le danger de l'écriture hors des bornes.
