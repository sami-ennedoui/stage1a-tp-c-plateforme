/* S3 corrigé. Implémentation seule, le main et les vérifications sont dans tests.c. */
#include "s3_tableaux.h"

int longueur(const char chaine[]) {
    int n = 0;
    while (chaine[n] != '\0') {   /* on s'arrête sur le caractère de fin */
        n++;
    }
    return n;
}
