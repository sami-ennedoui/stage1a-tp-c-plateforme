#include "s1_types.h"

int main(void) {
    if (valeur_dans_char(64) != 64) {
        printf("FAIL: 64 tient dans un char, on devrait relire 64, lu %d\n", valeur_dans_char(64));
        return 1;
    }
    if (valeur_dans_char(320) != 64) {
        printf("FAIL: 320 range dans un char devrait donner 64, lu %d\n", valeur_dans_char(320));
        return 1;
    }
    if (valeur_dans_char(256) != 0) {
        printf("FAIL: 256 range dans un char devrait donner 0, lu %d\n", valeur_dans_char(256));
        return 1;
    }
    if (valeur_dans_char(300) != 44) {
        printf("FAIL: 300 range dans un char devrait donner 44, lu %d\n", valeur_dans_char(300));
        return 1;
    }
    printf("TOUT PASSE\n");
    return 0;
}
