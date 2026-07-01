#include <stdio.h>

/* Exercice 1 du BE : les types de base et leur taille. */

int main(void)
{
    short var_short = 10;
    char var_char = 320;      /* ne tient pas sur un octet, sera tronque */
    float var_float = 3.40e30;
    int var_int = 260;
    double var_double = 63;

    printf(" La taille d'un short est %d octet(s) \n", (int)sizeof(var_short));
    printf(" La taille d'un char est %d octet(s) \n", (int)sizeof(var_char));
    printf(" La taille d'un float est %d octet(s) \n", (int)sizeof(var_float));
    printf(" La taille d'un double est %d octet(s) \n", (int)sizeof(var_double));
    printf(" La taille d'un int est %d octet(s) \n", (int)sizeof(var_int));

    /* Un char signe code une valeur de -128 a 127. 320 vaut (1 0100 0000) en binaire,
       on ne garde que les 8 bits de poids faible, (0100 0000) = 64. */
    printf(" Si var_char [-128 ; +127 ] est initialisee a 320 , on obtient %d \n", var_char);

    return 0;
}
