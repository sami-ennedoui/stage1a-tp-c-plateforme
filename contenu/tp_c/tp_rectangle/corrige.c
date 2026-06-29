#include <stdio.h>

int main(void) {
    int lignes, colonnes;

    printf("Nombre de lignes : ");
    scanf("%d", &lignes);
    printf("Nombre de colonnes : ");
    scanf("%d", &colonnes);

    for (int i = 0; i < lignes; i++) {
        for (int j = 0; j < colonnes; j++) {
            printf("-");
        }
        printf("\n");
    }

    return 0;
}
