#include "s4_sousprog.h"
#include <math.h>

static int proche(double x, double y) {
    return fabs(x - y) < 1e-6;
}

int main(void) {
    if (!proche(calculer_y(4, 3, 2), 11.0)) {
        printf("FAIL: calculer_y(4,3,2) devrait valoir 11, lu %f\n", calculer_y(4, 3, 2));
        return 1;
    }
    if (!proche(calculer_y(0, 5, 100), 5.0)) {
        printf("FAIL: calculer_y(0,5,100) devrait valoir 5, lu %f\n", calculer_y(0, 5, 100));
        return 1;
    }
    if (!proche(calculer_y(2, -1, 3), 5.0)) {
        printf("FAIL: calculer_y(2,-1,3) devrait valoir 5, lu %f\n", calculer_y(2, -1, 3));
        return 1;
    }
    printf("TOUT PASSE\n");
    return 0;
}
