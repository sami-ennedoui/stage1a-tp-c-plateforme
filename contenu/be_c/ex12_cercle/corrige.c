#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Exercice 12 du BE : calcul des parametres d'un cercle a partir du rayon. */

/* declaration globale d'une constante PI */
#define PI 3.14159

/* declaration d'un nouveau type de variable (cf exo 3) */
typedef struct cercle {
    float rayon;
    float diametre;
    float aire;
    float perimetre;
} type_cercle;

/* Saisie de la valeur du rayon au clavier. R est un pointeur, on modifie
   directement la variable du main. On redemande tant que R <= 0. */
void SP_SAISIE_RAYON(float* R)
{
    *R = 0; /* on initialise a 0 pour entrer au moins une fois dans la boucle */

    while (*R <= 0) {
        printf("Entrer la valeur du rayon du cercle: ");
        scanf("%f", R); /* R est deja une adresse, on l'utilise directement */
        if (*R <= 0) {
            printf("Erreur: le rayon doit etre > 0\n");
        }
    }
}

/* Calcul des parametres du cercle a partir de son rayon. c est un pointeur,
   on accede aux champs avec -> ou avec le point sur (*c). */
void SP_CALCUL_RAYON(type_cercle* c)
{
    c->perimetre = 2 * PI * c->rayon;
    (*c).diametre = 2 * (*c).rayon;
    c->aire = PI * (*c).rayon * c->rayon;
}

/* Affichage des parametres du cercle. c est passe par valeur, on accede aux
   champs avec le point. %.Kf choisit K chiffres apres la virgule. */
void SP_AFFICH_PARAM(type_cercle c)
{
    printf("Le rayon du cercle est %f\n", c.rayon);
    printf("Le diametre du cercle est %.1f\n", c.diametre);
    printf("Le perimetre du cercle est %.2f\n", c.perimetre);
    printf("L'aire du cercle est %.3f\n", c.aire);
}

int main(void)
{
    type_cercle mon_cercle;
    SP_SAISIE_RAYON(&(mon_cercle.rayon)); /* on donne l'adresse du champ a modifier */
    SP_CALCUL_RAYON(&mon_cercle);         /* on donne l'adresse de la structure */
    SP_AFFICH_PARAM(mon_cercle);
    return 0;
}
