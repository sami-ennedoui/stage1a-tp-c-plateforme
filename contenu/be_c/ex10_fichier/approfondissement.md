# Approfondissement (débloqué une fois l'exercice validé)

L'énoncé se contente d'ouvrir le fichier avec `fopen`, d'y écrire le tableau, puis de fermer. Le corrigé ajoute deux gestes que l'énoncé ne demande pas, mais qui font la différence entre un programme jouet et un programme sérieux.

Le premier geste est de tester le retour de `fopen`. Cette fonction rend un pointeur sur le fichier ouvert, mais elle peut échouer : disque plein, dossier interdit à l'écriture, nom de fichier invalide. En cas d'échec, elle rend `NULL`. Si tu ne testes rien et que tu écris quand même dans un pointeur `NULL` avec `fprintf`, le programme plante avec une erreur de segmentation. Le corrigé écrit donc juste après l'ouverture un test du genre `if (p_fichier == NULL) { ... return 1; }` qui affiche un message d'erreur et arrête proprement le programme avec un code de retour non nul. Le `return 1` signale à l'extérieur que quelque chose s'est mal passé.

Le second geste est le message de confirmation affiché à l'écran une fois l'écriture réussie. Il rassure l'utilisateur et, dans la plateforme, il donne à la porte quelque chose à lire, puisque le vrai résultat est parti dans le fichier.

Le réflexe à garder : toute opération qui touche l'extérieur, un fichier, le réseau, la mémoire demandée au système, peut échouer, et un programme robuste teste toujours si elle a réussi avant de continuer.

Pour aller plus loin : ouvre en mode `"r"` un fichier qui n'existe pas et vérifie que `fopen` rend bien `NULL`, ton test le rattrape alors proprement.
