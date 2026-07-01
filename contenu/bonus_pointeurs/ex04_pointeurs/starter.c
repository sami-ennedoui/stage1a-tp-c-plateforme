#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*============================================*/
/* Exercice 4 ==> Les pointeurs               */
/*============================================*/

int main(void)
{
    int val = 123;
    int* p_val = NULL;

    double val_double = 2.354;
    double* p_val_double;

    /* À toi d'écrire le programme.
       1. Affiche le contenu de val et son adresse (&val).
       2. Affiche le contenu de p_val et son adresse : au depart p_val vaut 0.
       3. Fais pointer p_val sur val avec p_val = &val, puis ecris *p_val = 12
          et affiche val, qui doit maintenant valoir 12.
       4. Incremente p_val d'une case et explique le +4 octets pour un int.
       5. Fais pointer p_val_double sur val_double, incremente-le d'une case
          et explique le +8 octets pour un double. */

    return 0;
}
