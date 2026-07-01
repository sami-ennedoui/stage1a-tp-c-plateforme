#include <stdio.h>
#include <stdlib.h>

/* Exercice 11 du BE : les sous-programmes.
   Permutation de valeurs par passage d'adresses. */

/* nom : permutation
   semantique : permute circulairement les 3 valeurs qui lui sont envoyees
   parametres :
   val_a : IN/OUT reel, valeur du nombre 1
   val_b : IN/OUT reel, valeur du nombre 2
   val_c : IN/OUT reel, valeur du nombre 3
   pre-condition : val_a, val_b et val_c initialises
   Tests : val_a=3, val_b=5, val_c=1, solutions val_a=1, val_b=3, val_c=5 */
void permutation(int *val_a, int *val_b, int *val_c)
/* Variables en IN/OUT donc utilisation des pointeurs */
{
    int temp;

    /* À toi de permuter circulairement les valeurs pointées, avec temp.
       Objectif : l'ancien val_c va dans val_a, l'ancien val_a dans val_b,
       l'ancien val_b dans val_c. */
    temp = 0;
}

/* Programme principal
   Tests : val_a=3, val_b=5, val_c=1, solutions val_a=1, val_b=3, val_c=5 */
int main(void)
{
    int a = 3, b = 5, c = 1;

    printf(" AVANT PERMUTATION  %d %d %d\n", a, b, c);

    /* Variables en IN/OUT donc on envoie des ADRESSES au sous-programme */
    permutation(&a, &b, &c);

    printf(" APRES PERMUTATION  %d %d %d\n", a, b, c);

    return 0;
}
