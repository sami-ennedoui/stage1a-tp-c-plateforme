# Exercice 13 — écrire dans un fichier

Écris un programme qui :

- déclare `int tab[4] = {3, 12, 7, 25}` et un `FILE *p_fichier`
- demande un nom de fichier (`scanf("%s", nom_fichier)`) et l'ouvre en écriture
  (`fopen(nom, "w")`)
- écrit chaque case dans le fichier avec `fprintf` (une ligne « tab[0] = 3 »),
  puis referme avec `fclose`
- affiche à l'écran, à la fin, exactement : `Fichier resultats.txt ecrit.`

Entrée fournie : `resultats.txt`. La porte ne lit que l'écran, d'où cette ligne
de confirmation.
But : `fopen` / `fprintf` / `fclose`.
