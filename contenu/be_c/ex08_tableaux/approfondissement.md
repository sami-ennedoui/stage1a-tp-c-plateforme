# Approfondissement (débloqué une fois l'exercice validé)

L'énoncé te demande de déclarer un tableau de 5 cases, puis d'écrire volontairement en dehors de ces 5 cases pour observer ce qui se passe.

Le corrigé fait un choix prudent. Il déclare en réalité un tableau plus grand que nécessaire, 16 cases au lieu de 5, tout en ne se servant vraiment que des 5 premières. Pourquoi ce détour ? Parce que le C ne vérifie jamais les bornes d'un tableau. Écrire dans `tab[10]` alors que le tableau ne fait que 5 cases est un débordement : le programme peut sembler marcher, planter sans prévenir, ou corrompre une autre variable, selon ce qui se trouve juste après en mémoire. En sur-dimensionnant le tableau à 16 cases, on garde une marge, l'écriture dans la case 10 tombe encore dans la zone réservée et ne casse rien, ce qui permet d'illustrer le point sans crash aléatoire.

Le message à retenir : ce n'est pas parce qu'un accès hors des 5 cases utiles n'a pas fait planter le programme qu'il est correct. Le danger reste entier, il est juste caché par la réserve de place. En C, c'est à toi de garantir que tu restes dans les bornes, le langage ne le fera jamais pour toi.

Pour aller plus loin : essaie d'écrire très loin, par exemple `tab[10000] = 1`, et regarde le programme s'arrêter avec une erreur de segmentation. C'est le débordement qui se manifeste enfin, cette fois hors de toute marge.
