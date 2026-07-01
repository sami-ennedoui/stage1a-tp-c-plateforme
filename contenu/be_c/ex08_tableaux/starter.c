#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*============================================*/
/* Exercice 5 ==> Les tableaux                */
/*============================================*/

int main(void)
{
    /* Le tableau utile a 5 cases. Les cases en trop servent a montrer
       sans planter ce qui se passe quand on ecrit hors des bornes. */
    int tab[16] = {1, 5, 10, 15, 20};

    /* À toi d'écrire le programme.
       1. Affiche l'adresse du tableau (tab), c'est l'adresse de sa premiere case.
       2. Pour chaque case de 0 a 4, affiche son adresse (&tab[i]) et sa valeur.
          Verifie que d'une case a la suivante l'adresse augmente de 4 octets.
       3. Ecris tab[10] = 23 pour montrer que le C laisse ecrire hors des bornes,
          et affiche un message de DANGER. */

    return 0;
}
