#include <stdio.h>
#include <stdlib.h>

/* Exercice 7 du BE : les structures de variables.
   Les dimensions sont fixées dans le code, il n'y a pas de saisie clavier. */

/* Nouveau type rectangle : longueur, largeur, aire, périmètre. */
typedef struct rectangle {
    int longueur;
    int largeur;
    int aire;
    int perimetre;
} rectangle;

/* SP_AFFICHE : affiche tous les champs du rectangle. */
void SP_AFFICHE(rectangle r)
{
    /* À toi d'afficher longueur, largeur, aire et périmètre. */
}

/* SP_MODIF_RECTANGLE : change largeur et longueur, puis met à jour
   aire et périmètre. Le rectangle est modifié sur place, passage par adresse. */
void SP_MODIF_RECTANGLE(rectangle *r, int nouvelle_largeur, int nouvelle_longueur)
{
    /* À toi de modifier les champs du rectangle pointé. */
}

int main(void)
{
    rectangle mon_rectangle1;
    mon_rectangle1.longueur = 7;
    mon_rectangle1.largeur = 4;

    /* À toi de remplir aire et perimetre à partir de longueur et largeur. */

    SP_AFFICHE(mon_rectangle1);

    SP_MODIF_RECTANGLE(&mon_rectangle1, 6, 10);
    SP_AFFICHE(mon_rectangle1);

    return 0;
}
