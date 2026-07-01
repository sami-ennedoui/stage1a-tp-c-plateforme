#include <stdio.h>
#include <stdlib.h>

/* Exercice 9 du BE : les sous-programmes.
   Equation d'une droite y = a * x + b. */

/* nom : calcul_ordonnee
   semantique : calcul de la coordonnee y connaissant x
   parametres :
   a : IN reel, valeur du coefficient directeur
   b : IN reel, valeur de l'ordonnee a l'origine
   x : IN reel, valeur de l'abscisse
   pre-condition : a, b et x initialises
   Tests : a=4, b=3, x=2, solution y = 11 */
int calcul_ordonnee(float a, float b, float x)
{
    float y;

    y = a * x + b;

    return (y);
}

/* Programme principal
   Tests : a=4, b=3, x=2, solution y = 11 */
int main(void)
{
    float val_a = 4, val_b = 3, val_x = 2;
    float val_y;

    val_y = calcul_ordonnee(val_a, val_b, val_x);

    printf("L'ordonnée pour x = %f vaut y = %f \n", val_x, val_y);

    return 0;
}
