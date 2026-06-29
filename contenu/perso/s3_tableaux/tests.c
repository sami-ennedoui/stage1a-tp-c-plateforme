#include "s3_tableaux.h"

int main(void) {
    int a[] = {3, 12, 7, 25, 1};
    if (maximum(a, 5) != 25) {
        printf("FAIL: maximum attendu 25, lu %d\n", maximum(a, 5));
        return 1;
    }

    int b[] = {-4, -9, -2, -30};   /* tout négatif : piège du candidat à zéro */
    if (maximum(b, 4) != -2) {
        printf("FAIL: maximum attendu -2, lu %d\n", maximum(b, 4));
        return 1;
    }

    int c[] = {42};
    if (maximum(c, 1) != 42) {
        printf("FAIL: maximum attendu 42, lu %d\n", maximum(c, 1));
        return 1;
    }

    printf("TOUT PASSE\n");
    return 0;
}
