# Exercice 3, les structures de contrôle

C'est l'exercice 3 du BE. Il porte sur les structures de contrôle du C, ici un `switch ... case` piloté par un menu, le tout répété par une boucle `do ... while`.

Réaliser un programme, mettant en œuvre un switch …case, permettant à un utilisateur, à partir d'un menu de choix, de modifier une variable parmi 3 variables a, b et c.

Les valeurs des variables sont : a = 1.5 - b = 0.5 - c = 0.6

Que voulez vous faire ?

1. Modifier a
2. Modifier b
3. Modifier c

Si l'utilisateur répond par un choix non proposé, afficher un message d'erreur. Après la modification, affichez les nouvelles valeurs des variables. Dans un second temps, rajouterez une boucle do … while pour demander à l'utilisateur s'il désire ou non modifier une autre variable.

Le programme est interactif. La porte joue un scénario complet à ta place. Elle choisit d'abord de modifier a et lui donne la valeur 9.9, puis demande à continuer. Elle tape ensuite le choix 5, qui n'est pas proposé, pour déclencher le message d'erreur. Elle continue, modifie b avec la valeur 8.8, puis répond qu'elle ne veut plus rien modifier, ce qui arrête la boucle.

La porte vérifie que le programme affiche les valeurs de départ `a = 1.5 - b = 0.5 - c = 0.6`, que la modification de a donne bien `a = 9.9`, que le choix invalide déclenche le message `Erreur : ce choix n'est pas propose.`, que la modification de b donne `a = 9.9 - b = 8.8 - c = 0.6`, et que le programme se termine par `Fin du programme.`.
