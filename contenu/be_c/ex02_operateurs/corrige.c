#include <stdio.h>

/* Exercice 2 du BE : les opérateurs relationnels, logiques et bit à bit. */

int main(void)
{
    /* Déclaration de variables avec initialisation */
    int a = 21;
    int b = 17;

    /* Opérateurs relationnels */
    printf(" ===== Operateurs relationnelles =====\n");
    printf("a = %d , b= %d , Resultat de a different de b = %d \n", a, b, a != b);
    printf("a = %d , b= %d , Resultat de a egal b = %d \n", a, b, a == b);
    printf("a = %d , b= %d , Resultat de a > b = %d \n", a, b, a > b);
    printf("a = %d , b= %d , Resultat de a < b = %d \n", a, b, a < b);

    printf("\n");

    /* Opérateurs logiques */
    printf(" ===== Operateurs logiques =====\n");
    printf("a = %d , b= %d , Resultat de a ET  b = %d \n", a, b, a && b);
    printf("a = %d , b= %d , Resultat de a OU  b = %d \n", a, b, a || b);
    printf("a = %d ,  Resultat de non a = %d \n", a, !b);

    printf("\n");

    /* Opérateurs bit à bit */
    printf(" ===== Operateurs bit a bit =====\n");
    printf("a = %d , b= %d , Resultat de a ET BIT A BIT  b = %d \n", a, b, a & b);
    printf("a = %d , b= %d , Resultat de a OU BIT A BIT  b = %d \n", a, b, a | b);
    printf("a = %d , b= %d , Resultat de a OU EXCLUSIF BIT A BIT  b = %d \n", a, b, a ^ b);

    printf("\n");

    return 0;
}
