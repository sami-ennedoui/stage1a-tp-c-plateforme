# Exercice 6, les sous-programmes

C'est l'exercice 6 du BE. Il porte sur les sous-programmes, avec le passage par valeur et le passage par adresse. Le support est un rectangle.

On considère un rectangle de largeur `int Larg` et de longueur `int Long`.

Réalisez un sous programme SP_AFFICHE permettant d'afficher la largeur et la longueur de ce rectangle.

On rajoute dans le programme principal une variable `int Aire` qui devra contenir l'aire du rectangle. Réalisez un sous programme SP_CALCUL_AIRE permettant de calculer l'air du rectangle et de renvoyer l'info vers le programme principal. Affichez cette aire depuis le programme principal.

On veut réaliser un sous programme SP_MODIF_RECTANGLE permettant de modifier les dimensions du rectangle. Le sous-programme doit avoir un droit de modification sur ces variables (IN/OUT) donc il faut utiliser un passage par adresse.

- Afficher dans le programme principal les adresses des variables `Larg` et `Long`.
- Ecrire le sous-programme SP_MODIF_RECTANGLE pour qu'il puisse recevoir et manipuler les adresses de Larg et Long et vérifier par un affichage dans ce sous-programme que les adresses reçues sont les bonnes.
- Effectuer le calcul de l'aire.

Utiliser votre sous-programme SP_AFFICHE dans le programme principal pour afficher les nouvelles dimensions et SP_CALCUL_AIRE pour calculer la nouvelle aire du rectangle.

On rajoute dans le programme principal une variable `int Perimetre`. Réalisez un sous programme SP_CALCUL_AIR_PERIMETRE permettant de calculer à la fois l'air et le périmètre du rectangle. Affichez ces infos depuis le programme principal.

Pour que le test soit reproductible, les dimensions sont fixées dans le code, sans saisie clavier. Le rectangle de départ mesure Larg = 4 et Long = 7, donc une aire de 28. SP_MODIF_RECTANGLE le modifie en Larg = 6 et Long = 10, ce qui donne une aire de 60 et un périmètre de 32. Les adresses sont affichées comme le demande l'énoncé, mais elles changent à chaque exécution et ne sont donc pas vérifiées par la porte.

La porte vérifie que le programme affiche d'abord `Largeur = 4, Longueur = 7` et `Aire = 28`, puis, après modification par adresse, `Largeur = 6, Longueur = 10`, `Nouvelle aire = 60` et enfin `Aire = 60, Perimetre = 32`.
