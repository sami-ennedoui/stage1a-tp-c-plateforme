# Équation du second degré

Résous `a*x² + b*x + c = 0` avec 4 sous-programmes appelés depuis le `main` :

- `Saisir_coefficients(float*, float*, float*)` : lit `a`, `b`, `c` (redemande `a`
  tant qu'il vaut 0)
- `calculer_determinant(a, b, c)` : renvoie `d = b*b - 4*a*c`
- `Calculer_Racines(...)` : affiche `d`, puis calcule les racines selon son signe
  (positif : réelles distinctes ; nul : double ; négatif : complexes)
- `Afficher_racines(...)` : annonce des solutions réelles ou complexes

Inclure `<math.h>` pour `sqrt`. Entrée fournie : `a = 1`, `b = -3`, `c = 2`.
Sortie attendue : « Les solutions sont réelles et sont s1=1.000000 et s2=2.000000. »

But : découpage en sous-programmes, pointeurs de sortie, `math.h`.
