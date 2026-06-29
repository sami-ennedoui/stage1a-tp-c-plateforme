#include "s3_tableaux.h"

int main(void) {
    if (longueur("Salut") != 5) {
        printf("FAIL: longueur(\"Salut\") devrait valoir 5, lu %d\n", longueur("Salut"));
        return 1;
    }
    if (longueur("") != 0) {
        printf("FAIL: longueur(\"\") devrait valoir 0, lu %d\n", longueur(""));
        return 1;
    }
    if (longueur("a") != 1) {
        printf("FAIL: longueur(\"a\") devrait valoir 1, lu %d\n", longueur("a"));
        return 1;
    }
    if (longueur("Bonjour") != 7) {
        printf("FAIL: longueur(\"Bonjour\") devrait valoir 7, lu %d\n", longueur("Bonjour"));
        return 1;
    }
    printf("TOUT PASSE\n");
    return 0;
}
