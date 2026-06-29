#include "s2_pointeurs.h"

int main(void) {
    int a = 3, b = 5, c = 1;
    permuter_valeur(&a, &b, &c);
    if (a != 1 || b != 3 || c != 5) {
        printf("FAIL: pour (3,5,1) on attend (1,3,5), lu (%d,%d,%d)\n", a, b, c);
        return 1;
    }

    int x = 10, y = 20, z = 30;
    permuter_valeur(&x, &y, &z);
    if (x != 30 || y != 10 || z != 20) {
        printf("FAIL: pour (10,20,30) on attend (30,10,20), lu (%d,%d,%d)\n", x, y, z);
        return 1;
    }

    printf("TOUT PASSE\n");
    return 0;
}
