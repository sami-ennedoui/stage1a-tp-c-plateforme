# Exercice 5 — les tableaux

Un tableau de 5 `int` : `{1, 5, 10, 15, 20}`. Écris un programme qui :

- affiche l'adresse du tableau, puis pour chaque case son adresse et sa valeur
  — « Valeur de la case [0] = 1 », …, « Valeur de la case [4] = 20 »
- fait remarquer que les cases se suivent en mémoire (+4 octets à chaque case)
- signale le risque d'écrire hors des bornes (affiche « DANGER »)

Les adresses changent à chaque exécution.
But : tableau contigu en mémoire, débordement.
