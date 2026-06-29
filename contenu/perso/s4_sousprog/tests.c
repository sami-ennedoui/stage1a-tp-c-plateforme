#include "s4_sousprog.h"

int main(void) {
    if (carre(5) != 25) {
        printf("FAIL: carre(5) devrait valoir 25, lu %d\n", carre(5));
        return 1;
    }
    if (somme_carres(1) != 1) {
        printf("FAIL: somme_carres(1) devrait valoir 1, lu %d\n", somme_carres(1));
        return 1;
    }
    if (somme_carres(3) != 14) {
        printf("FAIL: somme_carres(3) devrait valoir 14, lu %d\n", somme_carres(3));
        return 1;
    }
    if (somme_carres(5) != 55) {
        printf("FAIL: somme_carres(5) devrait valoir 55, lu %d\n", somme_carres(5));
        return 1;
    }
    printf("TOUT PASSE\n");
    return 0;
}
