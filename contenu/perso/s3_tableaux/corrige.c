/* S3 corrigé. Implémentation seule, le main et les vérifications sont dans tests.c. */
#include "s3_tableaux.h"

int maximum(const int tab[], int n) {
    int meilleur = tab[0];               /* le premier élément est le candidat de départ */
    for (int i = 1; i < n; i++) {
        if (tab[i] > meilleur) {
            meilleur = tab[i];
        }
    }
    return meilleur;
}
