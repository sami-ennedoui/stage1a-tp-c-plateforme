# S3, parcourir un tableau

Dans le projet Snake, le corps du serpent est un tableau de cases. Travailler sur un tableau, c'est presque toujours le parcourir avec une boucle et un indice.

Tu dois écrire `maximum`, qui reçoit un tableau de n entiers et renvoie le plus grand. Tu pars du premier élément comme meilleur candidat, puis tu compares les suivants un par un.

Le piège : ne pars pas de zéro comme meilleur candidat. Si tous les nombres sont négatifs, zéro serait un faux maximum. Pars de la vraie première valeur du tableau, `tab[0]`.

La porte : quand `maximum` trouve le bon élément, y compris sur un tableau entièrement négatif et sur un tableau d'un seul élément, le test sort en succès.
