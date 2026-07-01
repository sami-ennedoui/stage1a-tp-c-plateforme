#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Equation du second degre du BE : calcul des racines d'un trinome
   a*x*x + b*x + c = 0, avec quatre sous-programmes. */

/* Prototypes des sous-programmes */
float calculer_determinant(float, float, float);
void Calculer_Racines(float, float, float, float*, float*, float*, float*, float*);
void Afficher_racines(float, float, float, float, float);
void Saisir_coefficients(float*, float*, float*);

int main(void)
{
    /* Declaration des variables du main */
    float val_a, val_b, val_c, val_d, val_s1r, val_s1i, val_s2r, val_s2i;

    Saisir_coefficients(&val_a, &val_b, &val_c);
    Calculer_Racines(val_a, val_b, val_c, &val_d, &val_s1r, &val_s1i, &val_s2r, &val_s2i);
    Afficher_racines(val_d, val_s1r, val_s1i, val_s2r, val_s2i);

    return 0;
}

/* Calcul du determinant du trinome : d = b*b - 4*a*c. */
float calculer_determinant(float a, float b, float c)
{
    float d;
    d = b * b - 4 * a * c;
    return d;
}

/* Calcul des deux racines du trinome. On range le determinant et les parties
   reelle et imaginaire de chaque racine dans les variables pointees. */
void Calculer_Racines(float a, float b, float c, float* d,
                      float* s1r, float* s1i, float* s2r, float* s2i)
{
    *d = calculer_determinant(a, b, c);

    printf(" Le determninant de l'equation vaut = %e\n", *d);

    if (*d > 0) {
        *s1r = -b / (2 * a) - sqrt(*d) / (2 * a);
        *s2r = -b / (2 * a) + sqrt(*d) / (2 * a);
        *s1i = 0;
        *s2i = 0;
    } else if (*d == 0) {
        *s1r = -b / (2 * a);
        *s2r = *s1r;
        *s1i = 0;
        *s2i = 0;
    } else {
        *s1r = -b / (2 * a);
        *s2r = -b / (2 * a);
        *s1i = -sqrt(-*d) / (2 * a);
        *s2i = sqrt(-*d) / (2 * a);
    }
}

/* Saisie des coefficients au clavier. On redemande a tant qu'il vaut 0. */
void Saisir_coefficients(float* a, float* b, float* c)
{
    do {
        printf("Entrez a = \n");
        scanf("%f", a);
        if (*a == 0) printf("Erreur !!! a doit etre different de 0 \n ");
    } while (*a == 0);

    printf("Entrez b = \n");
    scanf("%f", b);

    printf("Entrez c = \n");
    scanf("%f", c);
}

/* Affichage des racines. Reelles si le determinant est positif ou nul,
   complexes sinon. */
void Afficher_racines(float d, float s1r_p, float s1i_p, float s2r_p, float s2i_p)
{
    if (d >= 0)
        printf("Les solutions sont réelles et sont s1=%f et s2=%f. \n", s1r_p, s2r_p);
    else
        printf("Les solutions sont complexes et sont s1 =%f+(%f)j et s2 = %f+(%f)j ",
               s2r_p, s1i_p, s2r_p, s2i_p);
}
