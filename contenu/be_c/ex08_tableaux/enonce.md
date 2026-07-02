# Exercice 8, les tableaux

C'est l'exercice 8 du BE. Il porte sur les tableaux en C.

1. Déclare un tableau de 5 nombres entiers et initialise-le.
2. Affiche l'adresse à laquelle est stocké le tableau. Affiche les adresses de toutes les cases du tableau ainsi que les valeurs contenues dans les emplacements 0 à 4.
3. Essaie de remplir une case qui est en dehors de l'espace du tableau. Que se passe-t-il ?

Le nom du tableau vaut l'adresse de sa première case. Les cases se suivent en mémoire : d'une case à la suivante l'adresse augmente de 4 octets, la taille d'un `int`. Les cases d'un tableau sont donc contiguës.

Le troisième point est un avertissement. En C rien ne vérifie que tu restes dans les bornes du tableau. Tu peux écrire dans une case au-delà des 5 cases utiles. Le langage te laisse faire sans rien signaler, mais tu écris alors dans une zone mémoire qui ne t'appartient pas. C'est une source classique de bugs. DANGER.

Les adresses affichées changent à chaque exécution, c'est normal, seule leur progression compte.

La porte vérifie la valeur de la case 0, celle de la case 4, et le signalement du danger. Ta sortie doit contenir exactement ces lignes (les adresses affichées, elles, sont libres) :

```
Valeur de la case [0] = 1
Valeur de la case [4] = 20
DANGER
```
