/* S2 corrigé. Implémentation seule, le main et les vérifications sont dans tests.c. */
#include "s2_pointeurs.h"

void echanger(int* a, int* b) {
    int tmp = *a;   /* on garde la valeur de a avant de l'écraser */
    *a = *b;
    *b = tmp;
}
