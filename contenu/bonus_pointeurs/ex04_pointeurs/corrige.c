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

    printf(" \n Le contenu ( ou valeur ) de val est %d \n", val);
    printf(" L'adresse ou val est stocke dans la memoire est %d \n", &val);

    printf(" \n Le contenu ( ou valeur ) de p_val est %d \n", p_val);
    printf(" L'adresse ou p_val est stocke dans la memoire est %d \n", &p_val);

    /* Un pointeur non initialise ne pointe sur rien de valide.
       Ecrire *p_val avant de l'initialiser planterait le programme. */

    /* p_val pointe maintenant sur l'adresse de val */
    p_val = &val;

    /* On accede au contenu de l'adresse pointee par p_val avec l'etoile.
       Comme p_val pointe sur val, on modifie val, qui passe de 123 a 12. */
    *p_val = 12;

    printf("\n  Le contenu ( ou valeur ) de val est maintenant %d \n", val);

    /* Incrementation du pointeur sur un int */
    printf(" \n  Avant incrementation du pointeur sur un int , p_val = %d \n", p_val);

    p_val = p_val + 1;

    printf(" \n Apres incrementation du pointeur sur un int, p_val = %d \n", p_val);
    printf(" \n L'adresse avant incrementation est augmentee de +4 car un int est codé sur 4 octets \n");

    p_val_double = &val_double;

    printf(" \n Avant incrementation du pointeur sur un double, p_val_double = %d \n", p_val_double);

    p_val_double = p_val_double + 1;

    printf(" \n Apres incrementation , du pointeur sur un double p_val = %d \n", p_val_double);
    printf(" \n L'adresse avant incrementation est augmentee de +8 car un double est code sur 8 octets \n");

    return 0;
}
