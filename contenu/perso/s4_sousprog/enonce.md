# S4, un sous-programme qui en appelle un autre

Un sous-programme s'écrit une fois et se réutilise. C'est tout l'intérêt, tu ne réécris pas le même calcul à plusieurs endroits.

La fonction `carre` est déjà écrite, elle renvoie le carré d'un nombre. Tu dois écrire `somme_carres`, qui renvoie 1 fois 1, plus 2 fois 2, et ainsi de suite jusqu'à n fois n. Plutôt que de recopier le calcul du carré dans ta boucle, appelle `carre`.

Indice : une boucle de 1 à n, et à chaque tour tu ajoutes `carre(i)` à un total que tu as mis à zéro au départ.

La porte : quand `somme_carres` donne le bon total pour plusieurs valeurs de n, le test sort en succès.
