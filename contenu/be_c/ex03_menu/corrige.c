#include <stdio.h>
#include <stdlib.h>

/*=====================================================*/
/* Exercice 3 : les structures de controle.            */
/* Un menu switch...case pour modifier a, b ou c,      */
/* le tout dans une boucle do...while.                 */
/*=====================================================*/

int main(void)
{
    float a = 1.5, b = 0.5, c = 0.6;
    int choix;
    int continuer;

    do {
        printf("===========================================\n");
        printf("Les valeurs des variables sont :\n");
        printf("a = %.1f - b = %.1f - c = %.1f\n", a, b, c);
        printf("Que voulez vous faire ?\n");
        printf("1. Modifier a\n");
        printf("2. Modifier b\n");
        printf("3. Modifier c\n");

        scanf("%d", &choix);

        switch (choix) {
            case 1:
                printf("Nouvelle valeur de a ?\n");
                scanf("%f", &a);
                break;
            case 2:
                printf("Nouvelle valeur de b ?\n");
                scanf("%f", &b);
                break;
            case 3:
                printf("Nouvelle valeur de c ?\n");
                scanf("%f", &c);
                break;
            default:
                printf("Erreur : ce choix n'est pas propose.\n");
                break;
        }

        printf("Nouvelles valeurs : a = %.1f - b = %.1f - c = %.1f\n", a, b, c);

        printf("Voulez vous modifier une autre variable ? (1 = oui, 0 = non)\n");
        scanf("%d", &continuer);
    } while (continuer != 0);

    printf("Fin du programme.\n");

    return 0;
}
