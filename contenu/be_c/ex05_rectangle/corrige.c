#include <stdio.h>
#include <stdlib.h>

/*=====================================================*/
/* Exercice 5 : les structures de controle.            */
/* Dessiner un rectangle de tirets avec des boucles    */
/* for, a partir d'un nombre de lignes et de colonnes  */
/* donne par l'utilisateur.                            */
/*=====================================================*/

int main(void)
{
    int lignes, colonnes;
    int i, j;

    printf("Nombre de lignes ?\n");
    scanf("%d", &lignes);
    printf("Nombre de colonnes ?\n");
    scanf("%d", &colonnes);

    for (i = 0; i < lignes; i++) {
        for (j = 0; j < colonnes; j++) {
            printf("-");
        }
        printf("\n");
    }

    return 0;
}
