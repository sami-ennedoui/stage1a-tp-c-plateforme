/* S1 corrigé. Implémentation seule, le main et les vérifications sont dans tests.c. */
#include "s1_types.h"

double moyenne(int a, int b, int c) {
    /* a + b + c est un entier. En divisant par 3.0, qui est un réel, tout le
       calcul passe en réel et la partie après la virgule est gardée. */
    return (a + b + c) / 3.0;
}
