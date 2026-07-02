# Exercice 5, les structures de contrôle

C'est l'exercice 5 du BE. Il porte sur les structures de contrôle du C, ici les boucles `for`. Tu dessines un rectangle plein en caractères.

Réaliser un programme utilisant des boucles `for` permettant de dessiner avec le caractère « - » un rectangle à partir d'un nombre de lignes et de colonnes données par l'utilisateur.

Le principe est celui de deux boucles imbriquées. Une première boucle `for` parcourt les lignes. À l'intérieur, une seconde boucle `for` parcourt les colonnes et affiche un tiret `-` à chaque colonne. À la fin de chaque ligne, tu passes à la ligne suivante.

Le programme est interactif. La porte fournit à ta place le nombre de lignes et le nombre de colonnes. Elle demande 6 lignes et 10 colonnes, comme dans l'exemple du slide, ce qui doit produire six lignes de dix tirets.

La porte vérifie les deux invites puis le rectangle. Ta sortie doit contenir exactement ces libellés d'invite, puis six lignes de dix tirets (recopie les invites telles quelles) :

```
Nombre de lignes ?
Nombre de colonnes ?
----------
----------
----------
----------
----------
----------
```
