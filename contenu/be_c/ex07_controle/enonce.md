# Exercice 7 — les structures de contrôle

Un jeu qui fait deviner un nombre caché (fixé à `56`). Écris un programme qui :

- affiche « Devinez un nombre entre 0 et 100 »
- dans une boucle `do ... while`, lit une proposition (`scanf`) puis affiche
  « C'est plus grand » si trop petit, « C'est plus petit » si trop grand,
  en comptant les essais
- à la bonne réponse, annonce le nombre trouvé et le nombre d'essais
  — ex. « … 56 en 3 essais »

Entrée fournie : `50`, `75`, `56` → gagné en 3 essais.
But : boucle `do while`, tests `if / else if`.
