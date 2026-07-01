#include <stdio.h>

/* Exercice 1 du BE : declarer une variable de chaque type de base et
   afficher chacune avec le format printf qui lui correspond. */

int main(void)
{
    short  var_short  = 12;
    int    var_int    = 260;
    char   var_char   = 'A';
    float  var_float  = 3.5;
    double var_double = 2.5;

    printf("short : %d\n", var_short);
    printf("int : %i\n", var_int);
    printf("char : %c\n", var_char);
    printf("float : %f\n", var_float);
    printf("double : %e\n", var_double);

    return 0;
}
