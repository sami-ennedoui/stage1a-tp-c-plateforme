# Équation du second degré

C'est l'exercice du BE sur le trinôme. Tu écris un programme complet qui calcule les racines d'une équation du second degré `a*x*x + b*x + c = 0`.

À partir des algorithmes dont tu as la correction sous Moodle, programme en C cette application permettant de résoudre une équation du second ordre.

L'énoncé du BE est volontairement court et renvoie aux algorithmes Moodle. Voici le découpage attendu, en quatre sous-programmes appelés depuis le `main`.

`Saisir_coefficients` reçoit trois `float*` et demande les coefficients `a`, `b`, `c` au clavier. Comme `a` ne doit pas être nul, tu redemandes `a` tant qu'il vaut 0, avec une boucle `do ... while`.

`calculer_determinant` reçoit `a`, `b`, `c` et renvoie le déterminant `d = b*b - 4*a*c`.

`Calculer_Racines` reçoit `a`, `b`, `c` et cinq pointeurs `float*` pour ranger le déterminant et les quatre nombres qui décrivent les deux racines, partie réelle et partie imaginaire. Il commence par afficher le déterminant. Puis il traite trois cas. Si le déterminant est positif, les deux racines sont réelles et distinctes. S'il est nul, il y a une racine double. S'il est négatif, les racines sont complexes conjuguées, la partie réelle est `-b/(2*a)` et la partie imaginaire est `sqrt(-d)/(2*a)`.

`Afficher_racines` reçoit le déterminant et les quatre nombres, et affiche les racines. Si le déterminant est positif ou nul, il annonce des solutions réelles. Sinon, il annonce des solutions complexes.

N'oublie pas d'inclure `<math.h>` pour `sqrt`. Le `main` déclare les variables, appelle la saisie, puis le calcul, puis l'affichage.

La porte lance ton programme avec `a = 1`, `b = -3`, `c = 2`, ce qui donne deux racines réelles. Elle vérifie que l'affichage annonce `Les solutions sont réelles et sont s1=1.000000 et s2=2.000000.`.
