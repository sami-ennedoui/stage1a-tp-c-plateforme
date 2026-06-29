/* S4 corrigé. Implémentation seule, le main et les vérifications sont dans tests.c. */
#include "s4_sousprog.h"

int carre(int x) {
    return x * x;
}

int somme_carres(int n) {
    int total = 0;
    for (int i = 1; i <= n; i++) {
        total = total + carre(i);   /* on réutilise carre, on ne réécrit pas i*i */
    }
    return total;
}
