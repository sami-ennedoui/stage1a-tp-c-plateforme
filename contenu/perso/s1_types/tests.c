#include "s1_types.h"
#include <math.h>

static int proche(double x, double y) {
    return fabs(x - y) < 1e-6;
}

int main(void) {
    if (!proche(moyenne(2, 2, 2), 2.0)) {
        printf("FAIL: moyenne(2,2,2) devrait valoir 2.0, lu %f\n", moyenne(2, 2, 2));
        return 1;
    }
    if (!proche(moyenne(1, 2, 2), 5.0 / 3.0)) {
        printf("FAIL: moyenne(1,2,2) devrait valoir 1.6667, lu %f\n", moyenne(1, 2, 2));
        return 1;
    }
    if (!proche(moyenne(0, 0, 1), 1.0 / 3.0)) {
        printf("FAIL: moyenne(0,0,1) devrait valoir 0.3333, lu %f\n", moyenne(0, 0, 1));
        return 1;
    }
    printf("TOUT PASSE\n");
    return 0;
}
