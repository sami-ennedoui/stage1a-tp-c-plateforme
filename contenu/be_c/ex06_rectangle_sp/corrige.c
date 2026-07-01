#include <stdio.h>
#include <stdlib.h>

/*=====================================================*/
/* Exercice 6 : les sous-programmes.                   */
/* Un rectangle (Larg, Long) manipule par plusieurs    */
/* sous-programmes : affichage, calcul d'aire,         */
/* modification par adresse, aire et perimetre.        */
/*=====================================================*/

/* Affiche la largeur et la longueur du rectangle.
   Passage par valeur, le sous-programme ne modifie rien. */
void SP_AFFICHE(int Larg, int Long)
{
    printf("Largeur = %d, Longueur = %d\n", Larg, Long);
}

/* Calcule l'aire du rectangle et la renvoie au programme principal. */
int SP_CALCUL_AIRE(int Larg, int Long)
{
    return Larg * Long;
}

/* Modifie les dimensions du rectangle. Les variables sont en IN/OUT,
   donc passage par ADRESSE avec des pointeurs. */
void SP_MODIF_RECTANGLE(int *Larg, int *Long)
{
    /* On verifie que les adresses recues sont les bonnes. */
    printf("Dans SP_MODIF_RECTANGLE, adresse de Larg = %p\n", (void *)Larg);
    printf("Dans SP_MODIF_RECTANGLE, adresse de Long = %p\n", (void *)Long);

    *Larg = 6;
    *Long = 10;
}

/* Calcule a la fois l'aire et le perimetre. L'aire et le perimetre
   sont renvoyes au programme principal par adresse. */
void SP_CALCUL_AIR_PERIMETRE(int Larg, int Long, int *Aire, int *Perimetre)
{
    *Aire = Larg * Long;
    *Perimetre = 2 * (Larg + Long);
}

int main(void)
{
    int Larg = 4, Long = 7;
    int Aire, Perimetre;

    SP_AFFICHE(Larg, Long);

    Aire = SP_CALCUL_AIRE(Larg, Long);
    printf("Aire = %d\n", Aire);

    /* On affiche les adresses des variables Larg et Long. */
    printf("Adresse de Larg = %p\n", (void *)&Larg);
    printf("Adresse de Long = %p\n", (void *)&Long);

    /* Variables en IN/OUT donc on envoie des ADRESSES au sous-programme. */
    SP_MODIF_RECTANGLE(&Larg, &Long);

    /* Nouvelles dimensions et nouvelle aire. */
    SP_AFFICHE(Larg, Long);
    Aire = SP_CALCUL_AIRE(Larg, Long);
    printf("Nouvelle aire = %d\n", Aire);

    SP_CALCUL_AIR_PERIMETRE(Larg, Long, &Aire, &Perimetre);
    printf("Aire = %d, Perimetre = %d\n", Aire, Perimetre);

    return 0;
}
