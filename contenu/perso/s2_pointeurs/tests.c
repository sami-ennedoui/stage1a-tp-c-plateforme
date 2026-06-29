#include "s2_pointeurs.h"

int main(void) {
    int x = 3, y = 7;
    echanger(&x, &y);
    if (x != 7 || y != 3) {
        printf("FAIL: apres echange x=%d y=%d, attendu x=7 y=3\n", x, y);
        return 1;
    }

    int a = -1, b = -1;
    echanger(&a, &b);   /* deux valeurs égales, rien ne doit casser */
    if (a != -1 || b != -1) {
        printf("FAIL: echange de valeurs egales casse, a=%d b=%d\n", a, b);
        return 1;
    }

    int u = 0, v = 100;
    echanger(&u, &v);
    if (u != 100 || v != 0) {
        printf("FAIL: apres echange u=%d v=%d, attendu u=100 v=0\n", u, v);
        return 1;
    }

    printf("TOUT PASSE\n");
    return 0;
}
