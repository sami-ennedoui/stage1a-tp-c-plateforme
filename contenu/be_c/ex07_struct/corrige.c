#include <stdio.h>
#include <stdlib.h>

/*=====================================================*/
/* Exercice 7 : les structures de variables.           */
/* Un nouveau type rectangle avec typedef struct,      */
/* puis des sous-programmes pour l'afficher et le      */
/* modifier en mettant a jour aire et perimetre.       */
/*=====================================================*/

/* Nouveau type de variable : un rectangle decrit par sa longueur,
   sa largeur, son aire et son perimetre. */
typedef struct rectangle {
    int longueur;
    int largeur;
    int aire;
    int perimetre;
} rectangle;

/* Affiche l'ensemble des champs du rectangle. */
void SP_AFFICHE(rectangle r)
{
    printf("Longueur = %d, Largeur = %d, Aire = %d, Perimetre = %d\n",
           r.longueur, r.largeur, r.aire, r.perimetre);
}

/* Modifie la largeur et la longueur du rectangle et met a jour
   l'aire et le perimetre. Le rectangle est modifie sur place,
   donc passage par adresse. */
void SP_MODIF_RECTANGLE(rectangle *r, int nouvelle_largeur, int nouvelle_longueur)
{
    r->largeur = nouvelle_largeur;
    r->longueur = nouvelle_longueur;
    r->aire = r->longueur * r->largeur;
    r->perimetre = 2 * (r->longueur + r->largeur);
}

int main(void)
{
    /* Declaration d'une variable de type rectangle et initialisation
       de la largeur et de la longueur. */
    rectangle mon_rectangle1;
    mon_rectangle1.longueur = 7;
    mon_rectangle1.largeur = 4;

    /* A partir de la largeur et de la longueur, on remplit l'aire et le perimetre. */
    mon_rectangle1.aire = mon_rectangle1.longueur * mon_rectangle1.largeur;
    mon_rectangle1.perimetre = 2 * (mon_rectangle1.longueur + mon_rectangle1.largeur);

    SP_AFFICHE(mon_rectangle1);

    /* Modification, puis verification avec SP_AFFICHE. */
    SP_MODIF_RECTANGLE(&mon_rectangle1, 6, 10);
    SP_AFFICHE(mon_rectangle1);

    return 0;
}
