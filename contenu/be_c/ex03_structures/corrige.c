#include <stdio.h>

/* Exercice 3 du BE : les structures de variables, le mot-clé struct. */

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

    /* Calcul des paramètres de mon_cercle avec un rayon de 5 */
    mon_cercle.rayon = 5.0;
    mon_cercle.diametre = 2 * mon_cercle.rayon;
    mon_cercle.aire = 3.1416 * mon_cercle.rayon * mon_cercle.rayon;
    mon_cercle.perimetre = 3.1416 * mon_cercle.diametre;

    /* Affichage des paramètres de mon_cercle */
    printf(" ==== Parametres de cercle =====\n");
    printf(" rayon = %f \n", mon_cercle.rayon);
    printf(" Diametre = %f \n", mon_cercle.diametre);
    printf(" Aire = %f \n", mon_cercle.aire);
    printf(" Perimetre = %f \n", mon_cercle.perimetre);

    /* Saisie d'un nouveau rayon */
    printf("\n Rentrez la nouvelle valeur du rayon \n");
    scanf("%f", &(mon_cercle.rayon));

    /* Calcul des paramètres de mon_cercle avec le nouveau rayon */
    mon_cercle.diametre = 2 * mon_cercle.rayon;
    mon_cercle.aire = 3.1416 * mon_cercle.rayon * mon_cercle.rayon;
    mon_cercle.perimetre = 3.1416 * mon_cercle.diametre;

    /* Affichage des paramètres de mon_cercle */
    printf(" ==== Parametres de cercle =====\n");
    printf(" rayon = %f \n", mon_cercle.rayon);
    printf(" Diametre = %f \n", mon_cercle.diametre);
    printf(" Aire = %f \n", mon_cercle.aire);
    printf(" Perimetre = %f \n", mon_cercle.perimetre);

    return 0;
}
