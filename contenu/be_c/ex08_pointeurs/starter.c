#include <stdio.h>
#include <stdlib.h>

/* À toi de compléter.
   Écris var_fonction(int *i, int *j, int k, int l) : elle doit écrire
   *i = 1 et *j = 2 (passage par adresse), et affecter k et l localement
   (passage par valeur, sans effet visible dans le main).
   Puis dans le main, déclare a, b, c, d, affiche leurs valeurs,
   appelle var_fonction(&a, &b, c, d) et réaffiche les valeurs. */

void var_fonction(int *i, int *j, int k, int l)
{
    /* à compléter */
}

int main(void)
{
    int a = -1, b = -2, c = -3, d = -4;

    printf(" a = %d b = %d \n", a, b);
    printf(" c = %d d = %d \n", c, d);

    /* Il manque l'appel à var_fonction et le réaffichage des valeurs. */

    return 0;
}
