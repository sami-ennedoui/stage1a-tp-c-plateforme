# Exercice 6, les tableaux (suite)

C'est l'exercice 6 du BE. Il continue sur les tableaux, cette fois avec une chaîne de caractères. En C une chaîne est simplement un tableau de `char` terminé par un caractère spécial, le caractère nul.

Déclare un tableau de caractères initialisé avec le mot `Salut` et affiche son contenu avec le format `%s`. Affiche aussi l'adresse du tableau. Comme pour un tableau d'entiers, le nom du tableau vaut l'adresse de sa première case.

Demande ensuite à l'utilisateur d'entrer une nouvelle chaîne, lis-la avec `scanf` et le format `%s`, puis affiche-la. Attention, on écrit `scanf("%s", chaine)` et pas `&chaine`. Comme `chaine` est déjà un tableau, son nom est déjà une adresse.

Le point d'attention est le même que pour l'exercice précédent. Si l'utilisateur tape un mot plus long que la place réservée, `scanf` écrit quand même au delà du tableau, dans une zone mémoire non prévue. C'est encore un débordement de tableau, un piège classique en C.

Dans la plateforme, la saisie clavier est fixée à l'avance, le programme reçoit le mot `Hello`.

La porte vérifie que la chaîne de départ est bien `Salut` et que la chaîne saisie, `Hello`, est bien relue et réaffichée.
