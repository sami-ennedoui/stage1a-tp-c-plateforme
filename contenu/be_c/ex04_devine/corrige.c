#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*============================================*/
/* Exercice 7 : les structures de controle.   */
/* Devinez un nombre entre 0 et 100.          */
/* Un test if imbrique dans une boucle do while. */
/*============================================*/

int main(void)
{
    int nombre_a_trouver = 56, nombre_propose;
    int essai = 0;

    printf("===========================================\n");
    printf(" Devinez un nombre entre 0 et 100 \n");
    printf("===========================================\n");

    do {
        printf(" Entrez votre proposition \n");
        scanf("%d", &nombre_propose);
        essai++;

        if (nombre_propose > nombre_a_trouver)
            printf("C'est plus petit \n ");
        else if (nombre_propose < nombre_a_trouver)
            printf("C'est plus grand \n ");
    } while (nombre_a_trouver != nombre_propose);

    printf("Gagné !!! Vous avez trouvé %d en %d essais \n ", nombre_a_trouver, essai);

    return 0;
}
