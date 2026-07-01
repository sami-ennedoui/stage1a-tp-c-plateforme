#include <stdio.h>

/* Déclaration d'un nouveau type de variable */
typedef struct cercle {
    float rayon;
    float diametre;
    float aire;
    float perimetre;
} type_cercle;

int main(void)
{
    /* Déclaration d'une nouvelle variable de type type_cercle nommée mon_cercle */
    type_cercle mon_cercle;

    /* À toi d'écrire le programme.
       Fixe mon_cercle.rayon à 5, puis calcule diametre, aire et perimetre.
       Affiche les quatre champs avec printf et %f.
       Demande un nouveau rayon au clavier avec scanf("%f", &(mon_cercle.rayon)).
       Recalcule diametre, aire et perimetre, puis réaffiche les quatre champs. */

    return 0;
}
