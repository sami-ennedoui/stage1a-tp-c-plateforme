#include <stdio.h>
#include <stdlib.h>

/* À toi de dessiner le rectangle de l'exercice 5.
   - Demande et lis le nombre de lignes puis le nombre de colonnes avec scanf.
   - Avec deux boucles for imbriquées, la boucle externe pour les lignes et
     la boucle interne pour les colonnes, affiche un tiret « - » par colonne.
   - Passe à la ligne à la fin de chaque ligne. */

int main(void)
{
    int lignes, colonnes;

    printf("Nombre de lignes ?\n");
    scanf("%d", &lignes);
    printf("Nombre de colonnes ?\n");
    scanf("%d", &colonnes);

    return 0;
}
