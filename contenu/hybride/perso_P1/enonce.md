# P1, le pointeur qui change l'état

Dans le projet Snake, un sous-programme doit changer l'état du menu de celui qui
l'appelle. Sa signature ressemble à `SP_Gestion_Evenements_MENU_ACCUEIL(SDL_Event, int*)`.
Le deuxième paramètre est un `int*`, un pointeur. On isole ce mécanisme hors de SDL.

Tu as deux fonctions. `changer_par_valeur` reçoit une copie, elle ne peut rien changer
chez l'appelant, c'est normal. À toi d'écrire `changer_par_pointeur` pour que la variable
de l'appelant devienne `MENU_PARAMETRAGE`.

Indice : tu reçois l'adresse de la variable. Pour atteindre la variable derrière l'adresse,
utilise l'étoile.

La porte : quand `changer_par_pointeur` modifie bien l'appelant et que `changer_par_valeur`
le laisse intact, le test sort en succès.
