# Exercice 4, les pointeurs

C'est l'exercice 4 du BE. Tu écris un programme complet qui manipule des pointeurs. Un pointeur est une variable qui contient l'adresse d'une autre variable en mémoire.

Déclare un entier `val` initialisé à 123 et un pointeur sur entier `p_val`. Déclare aussi un `double` `val_double` et un pointeur sur double `p_val_double`. Affiche d'abord le contenu de `val` et son adresse, puis le contenu de `p_val` et son adresse. Au départ `p_val` vaut 0 car il pointe sur `NULL`.

Fais ensuite pointer `p_val` sur `val`, avec `p_val = &val`. À partir de là, écrire `*p_val = 12` modifie directement le contenu de `val`. Tu affiches `val` et tu vois qu'il vaut maintenant 12.

Le dernier point montre l'arithmétique des pointeurs. Quand tu ajoutes 1 à un pointeur, l'adresse n'augmente pas de 1 mais de la taille du type pointé. Sur un pointeur d'`int` l'adresse augmente de 4 octets. Sur un pointeur de `double` elle augmente de 8 octets. Le programme l'affiche et l'explique.

Les adresses affichées changent à chaque exécution, c'est normal, seule leur logique compte.

La porte vérifie que `val` vaut 123 au départ, que `p_val` vaut 0 avant d'être initialisé, que `val` passe bien à 12, et que les explications sur les +4 et +8 octets sont présentes.
