#include <stdio.h>
#include <math.h>

int main(void) {
    double a, b, c;

    printf("Equation a*x*x + b*x + c = 0\n");
    printf("a = ");
    scanf("%lf", &a);
    printf("b = ");
    scanf("%lf", &b);
    printf("c = ");
    scanf("%lf", &c);

    double delta = b * b - 4 * a * c;

    if (delta > 0) {
        double x1 = (-b + sqrt(delta)) / (2 * a);
        double x2 = (-b - sqrt(delta)) / (2 * a);
        printf("Deux solutions reelles : x1 = %f, x2 = %f\n", x1, x2);
    } else if (delta == 0) {
        double x = -b / (2 * a);
        printf("Une solution double : x = %f\n", x);
    } else {
        printf("Pas de solution reelle.\n");
    }

    return 0;
}
