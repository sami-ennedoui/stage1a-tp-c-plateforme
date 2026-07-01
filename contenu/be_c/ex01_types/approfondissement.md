# Approfondissement (débloqué une fois l'exercice validé)

Le corrigé officiel du BE va un peu plus loin que l'énoncé de base. Deux points à explorer.

1. La taille des types. Affiche le nombre d'octets de chaque type avec `sizeof`, par exemple `printf("un int fait %d octets\n", (int)sizeof(int));`. Tu verras char = 1, short = 2, int = 4, float = 4, double = 8.

2. La troncature du char. Un `char` ne tient que sur un octet, donc il ne code qu'une valeur entre -128 et 127. Range 320 dans un `char` et affiche-le avec `%d` : tu obtiens 64. Le compilateur ne garde que les huit bits de poids faible, car 320 vaut 1 0100 0000 en binaire et on ne garde que 0100 0000, qui vaut 64.
