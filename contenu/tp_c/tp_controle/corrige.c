#include <stdio.h>

int main(void) {
    float a = 1.5, b = 0.5, c = 0.6;
    int choix;
    int continuer = 1;

    do {
        printf("Valeurs : a = %f, b = %f, c = %f\n", a, b, c);
        printf("Que voulez-vous faire ?\n1. Modifier a\n2. Modifier b\n3. Modifier c\n");
        scanf("%d", &choix);

        float nouvelle;
        switch (choix) {
            case 1:
                printf("Nouvelle valeur de a : ");
                scanf("%f", &nouvelle);
                a = nouvelle;
                break;
            case 2:
                printf("Nouvelle valeur de b : ");
                scanf("%f", &nouvelle);
                b = nouvelle;
                break;
            case 3:
                printf("Nouvelle valeur de c : ");
                scanf("%f", &nouvelle);
                c = nouvelle;
                break;
            default:
                printf("Choix invalide.\n");
        }

        printf("Apres modification : a = %f, b = %f, c = %f\n", a, b, c);
        printf("Continuer ? 1 pour oui, 0 pour non : ");
        scanf("%d", &continuer);
    } while (continuer == 1);

    return 0;
}
