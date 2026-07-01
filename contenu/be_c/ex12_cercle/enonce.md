# Exercice 12, les paramètres d'un cercle

C'est l'exercice 12 du BE. Tu écris un programme complet qui calcule les paramètres d'un cercle à partir de son rayon.

Commence par définir une constante `PI` avec `#define`, puis un type de structure `type_cercle` avec `typedef struct`. Cette structure regroupe quatre champs `float` : le rayon, le diamètre, l'aire et le périmètre.

Le programme se découpe en trois sous-programmes.

Le premier, `SP_SAISIE_RAYON`, demande le rayon au clavier et le range dans la variable pointée. Il reçoit un `float*`, donc il modifie directement la variable du `main`. Tant que le rayon saisi est négatif ou nul, il affiche une erreur et redemande la saisie.

Le deuxième, `SP_CALCUL_RAYON`, reçoit un `type_cercle*` et remplit les champs diamètre, aire et périmètre à partir du rayon. Le diamètre vaut deux fois le rayon, le périmètre vaut `2 * PI * rayon`, l'aire vaut `PI * rayon * rayon`. Comme le paramètre est un pointeur, tu accèdes aux champs avec la flèche `->`, ou avec le point sur `(*c)`.

Le troisième, `SP_AFFICH_PARAM`, reçoit la structure par valeur et affiche les quatre champs. Le diamètre est affiché avec une décimale, le périmètre avec deux, l'aire avec trois. On utilise `%.1f`, `%.2f` et `%.3f`.

Le `main` déclare un `type_cercle`, appelle la saisie sur l'adresse du champ rayon, puis le calcul sur l'adresse de la structure, puis l'affichage.

La porte lance ton programme avec un rayon de 1, et vérifie que le diamètre affiché vaut 2.0, le périmètre 6.28 et l'aire 3.142.
