# Exercice 8 — passage par valeur / par adresse

Écris une fonction `var_fonction(int *i, int *j, int k, int l)` qui écrit `1`
dans `*i` et `2` dans `*j`. Dans le `main` :

- déclare `a = -1, b = -2, c = -3, d = -4` et affiche-les
  — « a = -1 b = -2 », « c = -3 d = -4 »
- appelle `var_fonction(&a, &b, c, d)` puis réaffiche
  — « a = 1 b = 2 »

`a` et `b` sont passés par adresse (donc modifiés), `c` et `d` par valeur
(donc inchangés).
But : par adresse la fonction modifie l'original, par valeur non.
