# Exercice 11 — permutation (par adresse)

Écris une procédure `permutation(int *val_a, int *val_b, int *val_c)` qui décale
les valeurs en cercle : ancien `val_c` → `val_a`, ancien `val_a` → `val_b`,
ancien `val_b` → `val_c` (avec une variable temporaire).

Dans le `main` : `a = 3, b = 5, c = 1`, affiche, appelle avec les adresses (`&`),
réaffiche :

- « AVANT PERMUTATION  3 5 1 »
- « APRES PERMUTATION  1 3 5 »

But : modifier les variables du `main` via des pointeurs.
