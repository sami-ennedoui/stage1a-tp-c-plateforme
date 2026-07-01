# Exercice 2, les opérateurs

C'est l'exercice 2 du BE. Tu écris un programme complet qui déclare deux entiers, `a` initialisé à 21 et `b` initialisé à 17, puis qui montre le résultat des différentes familles d'opérateurs du C sur ces deux valeurs.

Commence par les opérateurs relationnels. Affiche le résultat de `a != b`, de `a == b`, de `a > b` et de `a < b`. Chacun rend 1 quand la comparaison est vraie et 0 quand elle est fausse.

Passe ensuite aux opérateurs logiques. Affiche `a && b`, le ET logique, `a || b`, le OU logique, et `!b`, la négation. Ici une valeur non nulle compte comme vraie, donc `a && b` et `a || b` valent 1, et `!b` vaut 0.

Termine par les opérateurs bit à bit, qui travaillent sur la représentation binaire des nombres. Affiche `a & b`, le ET bit à bit, `a | b`, le OU bit à bit, et `a ^ b`, le OU exclusif bit à bit. Avec 21 et 17 tu obtiens 17, 21 et 4.

Sers-toi de `printf` avec `%d` pour afficher chaque résultat. Reprends la mise en forme du corrigé pour tes messages.

La porte vérifie que les opérateurs donnent les bons résultats, en particulier `a != b` qui vaut 1, `a == b` qui vaut 0, le ET bit à bit qui vaut 17 et le OU exclusif qui vaut 4.
