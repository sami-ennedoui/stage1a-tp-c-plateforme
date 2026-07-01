#include <stdio.h>
#include <stdlib.h>

/* Exercice 6 du BE : les sous-programmes sur un rectangle.
   Les dimensions sont fixées dans le code, il n'y a pas de saisie clavier. */

/* SP_AFFICHE : affiche la largeur et la longueur. Passage par valeur. */
void SP_AFFICHE(int Larg, int Long)
{
    /* À toi d'afficher « Largeur = ..., Longueur = ... ». */
}

/* SP_CALCUL_AIRE : calcule l'aire et la renvoie au programme principal. */
int SP_CALCUL_AIRE(int Larg, int Long)
{
    /* À toi de renvoyer Larg * Long. */
    return 0;
}

/* SP_MODIF_RECTANGLE : modifie les dimensions. Passage par ADRESSE.
   Pense à afficher les adresses reçues pour vérifier que ce sont les bonnes,
   puis change les dimensions en Larg = 6 et Long = 10. */
void SP_MODIF_RECTANGLE(int *Larg, int *Long)
{
    /* À toi de vérifier les adresses et de modifier les valeurs pointées. */
}

/* SP_CALCUL_AIR_PERIMETRE : calcule l'aire et le périmètre, renvoyés par adresse. */
void SP_CALCUL_AIR_PERIMETRE(int Larg, int Long, int *Aire, int *Perimetre)
{
    /* À toi de remplir *Aire et *Perimetre. */
}

int main(void)
{
    int Larg = 4, Long = 7;
    int Aire, Perimetre;

    SP_AFFICHE(Larg, Long);

    Aire = SP_CALCUL_AIRE(Larg, Long);
    printf("Aire = %d\n", Aire);

    printf("Adresse de Larg = %p\n", (void *)&Larg);
    printf("Adresse de Long = %p\n", (void *)&Long);

    SP_MODIF_RECTANGLE(&Larg, &Long);

    SP_AFFICHE(Larg, Long);
    Aire = SP_CALCUL_AIRE(Larg, Long);
    printf("Nouvelle aire = %d\n", Aire);

    SP_CALCUL_AIR_PERIMETRE(Larg, Long, &Aire, &Perimetre);
    printf("Aire = %d, Perimetre = %d\n", Aire, Perimetre);

    return 0;
}
