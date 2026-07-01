# Exercice 12 — les paramètres d'un cercle

`#define PI 3.1416` et un type `type_cercle` (struct à 4 champs `float`).
Trois sous-programmes :

- `SP_SAISIE_RAYON(float*)` : lit le rayon (redemande tant qu'il est ≤ 0)
- `SP_CALCUL_RAYON(type_cercle*)` : diamètre = 2 × rayon, périmètre = 2 × PI × rayon,
  aire = PI × rayon² (accès aux champs avec `->`)
- `SP_AFFICH_PARAM(type_cercle)` : affiche rayon, diamètre (`%.1f`),
  périmètre (`%.2f`), aire (`%.3f`)

Entrée fournie : `1`. Sortie attendue (extraits) :

- `Le diametre du cercle est 2.0`
- `Le perimetre du cercle est 6.28`
- `L'aire du cercle est 3.142`

But : structures, pointeur vers structure, découpage en sous-programmes.
