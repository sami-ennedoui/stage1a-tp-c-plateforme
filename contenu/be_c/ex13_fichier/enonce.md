# Exercice 13, écriture dans un fichier texte

C'est l'exercice 13 du BE. Tu écris un programme complet qui range les valeurs d'un tableau dans un fichier texte.

Déclare un tableau `int tab[4]` initialisé avec quatre valeurs, par exemple `{3, 12, 7, 25}`. Déclare aussi un pointeur sur fichier `FILE* p_fichier` et une petite chaîne `char nom_fichier[10]` pour le nom du fichier.

Demande le nom du fichier à l'utilisateur avec `printf` puis `scanf("%s", nom_fichier)`. Ouvre ensuite ce fichier en écriture avec `fopen(nom_fichier, "w")`. Le mode `"w"` crée le fichier ou l'écrase s'il existe déjà.

Parcours le tableau avec une boucle `for` et écris chaque case dans le fichier avec `fprintf`. Sur la même idée que `printf`, mais le premier argument est le pointeur sur fichier. Écris une ligne par case, sous la forme `tab[0] = 3`.

Ferme le fichier avec `fclose` quand la boucle est finie. Un fichier ouvert doit toujours être fermé.

Ce programme écrit dans un fichier, pas à l'écran. Pour que la porte puisse vérifier ton travail, affiche à la fin une ligne de confirmation avec `printf`, exactement `Fichier resultats.txt ecrit.`. Cette confirmation est le seul texte que la porte lit, car elle ne regarde que la sortie à l'écran.

La porte lance ton programme avec le nom `resultats.txt`, et vérifie que la confirmation `Fichier resultats.txt ecrit.` apparaît bien à l'écran après une exécution sans erreur.
