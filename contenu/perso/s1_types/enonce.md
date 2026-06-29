# S1, les types et la division qui ment

Quand tu écris `7 / 2` en C, tu n'obtiens pas 3.5 mais 3. Entre deux entiers, la division jette tout ce qui suit la virgule. C'est une source d'erreurs classique, et elle revient dès qu'on calcule une moyenne, une vitesse ou une position.

Tu dois écrire `moyenne`, qui reçoit trois entiers et renvoie leur moyenne sous forme de réel. Le piège est exactement celui du dessus. Si tu divises la somme, un entier, par 3, un autre entier, le résultat reste entier.

Indice : il suffit qu'un seul des deux nombres de la division soit un réel pour que tout le calcul passe en réel.

La porte : quand `moyenne` renvoie la vraie valeur réelle pour plusieurs jeux de nombres, le test sort en succès.
