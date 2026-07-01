# Exercice 7, les structures de variables

C'est l'exercice 7 du BE. Il porte sur les structures de variables du C, avec `struct` et `typedef`. Tu construis ton propre type pour décrire un rectangle.

Construire un nouveau type de variable nommé `rectangle` à l'aide d'une structure permettant de stocker les informations relatives à la description du précédent rectangle : longueur, largeur, aire, périmètre.

Déclarer une nouvelle variable de type rectangle nommée `mon_rectangle1` dans le programme principal et initialiser les valeurs de la largeur et de la longueur.

A partir de la connaissance de la largeur et de la longueur, remplir les champs aire et périmètre de votre variable `mon_rectangle1`.

Réaliser un sous-programme SP_AFFICHE permettant d'afficher l'ensemble des champs de la variable `mon_rectangle1` (longueur, largeur, aire, périmètre).

Réaliser un sous-programme SP_MODIF_RECTANGLE permettant de modifier la largeur et la longueur du rectangle et de mettre à jour les valeurs de l'air et du périmètre. Vous utiliserez alors dans votre programme principal SP_AFFICHE pour vérifier que les modifications ont été effectuées.

Pour que le test soit reproductible, les dimensions sont fixées dans le code, sans saisie clavier. Le rectangle de départ a une longueur de 7 et une largeur de 4, donc une aire de 28 et un périmètre de 22. SP_MODIF_RECTANGLE le modifie en une largeur de 6 et une longueur de 10, ce qui donne une aire de 60 et un périmètre de 32.

La porte vérifie que le programme affiche d'abord `Longueur = 7, Largeur = 4, Aire = 28, Perimetre = 22`, puis, après modification, `Longueur = 10, Largeur = 6, Aire = 60, Perimetre = 32`.
