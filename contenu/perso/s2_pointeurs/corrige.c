/* S2 corrigé. Implémentation seule, le main et les vérifications sont dans tests.c. */
#include "s2_pointeurs.h"

void permuter_valeur(int* val_a, int* val_b, int* val_c) {
    int temp = *val_a;   /* on met de côté la première valeur avant de l'écraser */
    *val_a = *val_c;
    *val_c = *val_b;
    *val_b = temp;
}
