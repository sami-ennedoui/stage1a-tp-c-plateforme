# Exercice 3 — les structures

Crée un type `type_cercle` (`typedef struct`) à 4 champs `float` : rayon,
diamètre, aire, périmètre. Écris un programme qui :

- déclare `mon_cercle`, fixe son rayon à `5` et calcule les autres champs
  (diamètre = 2 × rayon, aire = 3.1416 × rayon², périmètre = 3.1416 × diamètre)
- affiche les 4 champs (`%f`) — ex. « rayon = 5.000000 », « Aire = 78.540001 »
- lit un nouveau rayon au clavier (`scanf("%f", &(mon_cercle.rayon))`),
  recalcule et réaffiche

Entrée fournie : `10` → « rayon = 10.000000 », « Aire = 314.160004 ».
But : regrouper des valeurs liées, accès à un champ avec le point `.`.
