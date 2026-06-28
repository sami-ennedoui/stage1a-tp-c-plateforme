# Jalon 1, le menu Paramétrage

Tu as l'accueil comme exemple, dans `GestionMenuAcceuil.c`. Écris le menu Paramétrage
sur le même modèle. Deux sous-programmes.

`SP_Structure_Menu_Parametrage` crée les quatre boutons dans `ListeBouton_Menu_Parametrage`,
avec `SP_Creation_Bouton` : couleur du serpent, couleur du fond, couleur du bord, retour.

`SP_Gestion_Evenements_MENU_PARAMETRAGE` lit le bouton cliqué avec `SP_Surveillance_Bouton`,
puis change `*p_etatMenu` vers le bon état. Souviens-toi de P1, tu as un pointeur, c'est
l'état de l'appelant que tu changes.

Ici, tu écris aussi ton test. Le harnais te donne `simuler_clic(bouton)` pour faire comme
si un bouton donné était cliqué, et le prototype du sous-programme. Écris des
vérifications dans `test_eleve`, du genre : après `simuler_clic(0)` et un appel, l'état doit
valoir `MENU_COULEUR_SNAKE`.

La plateforme juge d'abord ton test, sans te montrer comment. Un test qui se contente de
vérifier que l'état a changé est trop faible. Quand ton test est jugé solide, il devient
la porte de ton propre code. Le bouton Lancer le jeu ouvre une fenêtre avec tes boutons.
