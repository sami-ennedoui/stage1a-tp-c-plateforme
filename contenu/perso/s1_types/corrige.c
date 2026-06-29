/* S1 corrigé. Implémentation seule, le main et les vérifications sont dans tests.c. */
#include "s1_types.h"

int valeur_dans_char(int n) {
    char c = n;     /* n est rangé sur un seul octet, les bits en trop sont perdus */
    return c;       /* relu, par exemple 320 redonne 64 */
}
