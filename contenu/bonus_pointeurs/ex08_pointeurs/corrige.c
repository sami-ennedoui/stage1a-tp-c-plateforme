#include <stdio.h>
#include <stdlib.h>

/* Exercice 8 : passage par valeur et par adresse.
   i et j sont des pointeurs (passage par adresse), k et l des entiers (passage par valeur). */

void var_fonction(int *i, int *j, int k, int l)
{
    int u = 1, v = 2;

    printf("\n Adresse des variables internes var_fonction \n");
    printf(" i = %p j = %p \n", (void *)i, (void *)j);
    printf(" &k = %p &l = %p \n", (void *)&k, (void *)&l);
    printf(" &u = %p &v = %p \n", (void *)&u, (void *)&v);

    *i = u;
    *j = v;
    k = u;
    l = v;
}

int main(void)
{
    int a = -1, b = -2, c = -3, d = -4;

    printf("\n valeur des variables en entree du programme principal \n");
    printf(" a = %d b = %d \n", a, b);
    printf(" c = %d d = %d \n", c, d);

    printf("\n adresses des variables \n");
    printf(" &a = %p &b = %p \n", (void *)&a, (void *)&b);
    printf(" &c = %p &d = %p \n", (void *)&c, (void *)&d);

    var_fonction(&a, &b, c, d);

    printf("\n valeur des variables en sortie de var_fonction \n");
    printf(" a = %d b = %d \n", a, b);
    printf(" c = %d d = %d \n", c, d);

    printf("\n");

    return 0;
}
