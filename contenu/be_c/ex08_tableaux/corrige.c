#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*============================================*/
/* Exercice 5 ==> Les tableaux                */
/*============================================*/

int main(void)
{
    /* Le tableau utile a 5 cases : 1, 5, 10, 15, 20.
       On reserve quelques cases de plus derriere pour pouvoir montrer,
       sans planter le programme, ce qui se passe quand on ecrit hors des bornes. */
    int tab[16] = {1, 5, 10, 15, 20};

    printf(" Le tableau est stocke a l'adresse %p . C'est l'adresse de la premiere case du tableau \n", (void*)tab);

    printf(" \n Adresses et valeurs des cases du tableau \n");

    printf("Adresse de la case 0 = %p - Valeur de la case [0] = %i \n", (void*)&tab[0], tab[0]);
    printf("Adresse de la case 1 = %p - Valeur de la case [1] = %i \n", (void*)&tab[1], tab[1]);
    printf("Adresse de la case 2 = %p - Valeur de la case [2] = %i \n", (void*)&tab[2], tab[2]);
    printf("Adresse de la case 3 = %p - Valeur de la case [3] = %i \n", (void*)&tab[3], tab[3]);
    printf("Adresse de la case 4 = %p - Valeur de la case [4] = %i \n", (void*)&tab[4], tab[4]);

    /* Ecriture au dela des 5 cases utiles. Le C ne verifie pas les bornes :
       il laisse ecrire, mais on ecrase une zone memoire non prevue. DANGER. */
    tab[10] = 23;
    printf(" \n On vient d'ecrire 23 dans la case 10, hors des 5 cases utiles. Le C n'a rien signale. DANGER \n");

    return 0;
}
