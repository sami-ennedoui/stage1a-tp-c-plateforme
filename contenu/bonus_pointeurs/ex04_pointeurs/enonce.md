# Exercice 4 — les pointeurs

Un pointeur contient l'adresse d'une variable. Écris un programme qui :

- déclare `int val = 123` et `int *p_val` (à `NULL`) ; affiche leur contenu
  et leur adresse — « de val est 123 », « de p_val est 0 »
- fait `p_val = &val` puis `*p_val = 12`, et réaffiche `val`
  — « de val est maintenant 12 »
- montre l'arithmétique des pointeurs : `+1` avance de la taille du type pointé,
  « +4 » pour un `int`, « 8 octets » pour un `double »

Les adresses changent à chaque exécution, c'est normal.
But : adresse, déréférencement `*`, arithmétique des pointeurs.
