# Le pas du serpent

Tu écris `SP_Avancer_Serpent` dans `GestionJeu.c`. Ce sous-programme fait avancer le jeu d'un pas, sans rien dessiner.

Tu calcules le déplacement selon `serpent.dir`, puis tu décales le corps, chaque segment prend la place de son voisin côté tête, comme le décalage de tableau vu en cours. Tu avances la tête d'une cellule. Si la tête sort de la grille ou touche le corps, tu poses `partie_terminee` à 1 et tu renvoies 0. Si la tête atteint la pomme, tu rallonges le serpent, tu incrémentes `score`, et tu poses une nouvelle pomme. Tu renvoies 1 tant que le serpent est vivant.

La porte exécute trois vérifications, le déplacement, la croissance et la collision. Les trois doivent passer.
