# Initialisation de la partie

Tu écris `SP_Initialisation_Partie` dans `InitialisationJeu.c`. Ce sous-programme prépare une nouvelle partie.

Le serpent part au centre de la grille, avec une longueur courte, `LONGUEUR_DEPART`. La tête est `corps[0]` et le corps s'étend vers la gauche. La direction initiale va vers la droite. Tu remets `score` et `partie_terminee` à zéro, puis tu poses une première pomme hors du corps avec `SP_Nouvelle_Pomme`.

Tu peux t'inspirer de `init_serpent` et `nouvelle_pomme` dans le fichier de référence `jeu_demo.c`. La porte vérifie la longueur de départ, la position centrale de la tête, et que la pomme est bien dans la grille et hors du serpent.
