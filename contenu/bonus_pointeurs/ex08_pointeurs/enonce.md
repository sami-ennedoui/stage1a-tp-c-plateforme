# Exercice 8, passage par valeur et par adresse

C'est l'exercice 8 du BE. Il montre la différence entre passer un paramètre par valeur et le passer par adresse, avec des pointeurs.

Tu écris une fonction `var_fonction` qui reçoit quatre paramètres : deux pointeurs `int *i` et `int *j`, et deux entiers `int k` et `int l`. À l'intérieur, elle déclare deux variables locales `u = 1` et `v = 2`. Elle affiche les adresses de ses paramètres et de ses variables locales avec le format `%p`, puis elle écrit `u` dans la case pointée par `i`, `v` dans la case pointée par `j`, et affecte aussi `k` et `l`.

Dans le `main`, tu déclares quatre variables `a = -1`, `b = -2`, `c = -3`, `d = -4`. Tu affiches leurs valeurs, puis leurs adresses. Tu appelles ensuite `var_fonction(&a, &b, c, d)`. Tu passes `a` et `b` par adresse, mais `c` et `d` par valeur.

Après l'appel, réaffiche les quatre valeurs. Le point de l'exercice est là. Comme `i` et `j` sont des pointeurs vers `a` et `b`, l'écriture `*i = u` et `*j = v` modifie vraiment `a` et `b` : ils valent maintenant 1 et 2. En revanche `k` et `l` ne sont que des copies de `c` et `d`, donc les modifier dans la fonction ne change rien dans le `main` : `c` et `d` valent toujours -3 et -4.

Les adresses affichées avec `%p` changent à chaque exécution, c'est normal. Ce qui compte, ce sont les valeurs.

La porte vérifie les valeurs de départ `a = -1 b = -2` et `c = -3 d = -4`, puis qu'après l'appel `a = 1 b = 2` grâce au passage par adresse.
