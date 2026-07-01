# Approfondissement (débloqué une fois l'exercice validé)

L'énoncé du BE tient en une phrase, il te renvoie aux algorithmes déjà corrigés sur Moodle. Le corrigé, lui, fait tout le travail que cette phrase cache. Il vaut la peine de regarder ce qu'il ajoute, parce que c'est là que se trouve le vrai apprentissage.

Le corrigé découpe le problème en quatre sous-programmes plutôt que d'entasser tout dans le `main`. La saisie contrôle que `a` n'est pas nul, sinon l'équation n'est plus du second degré et la division par `2*a` exploserait. Le calcul du déterminant est isolé dans sa propre fonction, ce qui rend le code lisible et réutilisable. Le calcul des racines gère les trois cas du discriminant : positif pour deux racines réelles distinctes, nul pour une racine double, négatif pour deux racines complexes conjuguées. Ce dernier cas est le plus riche, il faut ranger séparément la partie réelle et la partie imaginaire de chaque racine, ce qui explique pourquoi le sous-programme reçoit autant de pointeurs. L'affichage, enfin, choisit son message selon le signe du déterminant.

Deux idées à retenir. La première, un problème un peu long se découpe en sous-programmes qui ont chacun un seul rôle. C'est plus facile à écrire, à tester et à corriger que d'un bloc. La seconde, il faut toujours penser aux cas limites, ici le discriminant négatif et le coefficient `a` nul, sinon le programme est faux ou plante sur une entrée pourtant légitime.

Pour aller plus loin : relance le programme avec `a = 1`, `b = 0`, `c = 1`, dont le discriminant vaut -4, et vérifie que ton affichage bascule bien vers les solutions complexes.
