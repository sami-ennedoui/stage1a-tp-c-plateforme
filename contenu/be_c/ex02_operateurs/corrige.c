#include <stdio.h>

/* Exercice 2 du BE : les operateurs relationnels, logiques et bit a bit,
   avec a = 17 et b = 21. */

int main(void)
{
    int a = 17;
    int b = 21;

    printf("a = %d, b = %d\n\n", a, b);

    printf("a > b = %d\n", a > b);
    printf("a < b = %d\n", a < b);
    printf("a == b = %d\n", a == b);
    printf("a != b = %d\n\n", a != b);

    printf("a && b = %d\n", a && b);
    printf("a || b = %d\n", a || b);
    printf("!a = %d\n", !a);
    printf("!b = %d\n\n", !b);

    printf("a & b = %d\n", a & b);
    printf("a | b = %d\n", a | b);
    printf("a ^ b = %d\n", a ^ b);

    return 0;
}
