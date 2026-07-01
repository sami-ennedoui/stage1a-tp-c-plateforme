# Exercice 10, écriture dans un fichier en mode texte

C'est l'exercice 10 du BE. Il porte sur l'écriture dans un fichier en mode texte.

1. Réalise un programme capable d'enregistrer dans un fichier texte, dont le nom sera demandé à l'utilisateur, le contenu d'un tableau sous la forme :

```
tab[0] = xx
tab[1] = xx
tab[2] = xx
tab[3] = xx
```

2. Vérifie la présence du fichier sur le disque de ta machine et ouvre-le avec un éditeur de texte pour contrôler son contenu.

Déclare un tableau `int tab[4]` initialisé avec quatre valeurs, un pointeur sur fichier `FILE* p_fichier` et une petite chaîne pour le nom du fichier. Demande le nom avec `printf` puis `scanf("%s", nom_fichier)`. Ouvre le fichier en écriture avec `fopen(nom_fichier, "w")`. Le mode `"w"` crée le fichier ou l'écrase s'il existe déjà. Parcours le tableau avec une boucle `for` et écris chaque case avec `fprintf`, une ligne par case. Ferme le fichier avec `fclose` quand la boucle est finie.

Ce programme écrit dans un fichier, pas à l'écran. Pour que la porte puisse vérifier ton travail, affiche à la fin une ligne de confirmation avec `printf`, exactement `Fichier resultats.txt ecrit.`. Cette confirmation est le seul texte que la porte lit, car elle ne regarde que la sortie à l'écran.

La porte lance ton programme avec le nom `resultats.txt`, et vérifie que la confirmation `Fichier resultats.txt ecrit.` apparaît bien à l'écran après une exécution sans erreur.
