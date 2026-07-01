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
    float val_a, val_b, val_c, val_d, val_s1r, val_s1i, val_s2r, val_s2i;

    Saisir_coefficients(&val_a, &val_b, &val_c);
    Calculer_Racines(val_a, val_b, val_c, &val_d, &val_s1r, &val_s1i, &val_s2r, &val_s2i);
    Afficher_racines(val_d, val_s1r, val_s1i, val_s2r, val_s2i);

    return 0;
}

/* A completer : d = b*b - 4*a*c. */
float calculer_determinant(float a, float b, float c)
{
    return 0;
}

/* A completer : ranger le determinant et les deux racines dans les variables
   pointees, en traitant les trois cas d > 0, d == 0 et d < 0. */
void Calculer_Racines(float a, float b, float c, float* d,
                      float* s1r, float* s1i, float* s2r, float* s2i)
{
    *d = 0;
    *s1r = 0;
    *s1i = 0;
    *s2r = 0;
    *s2i = 0;
}

/* A completer : demander a, b, c au clavier, redemander a tant qu'il vaut 0. */
void Saisir_coefficients(float* a, float* b, float* c)
{
    *a = 1;
    *b = 0;
    *c = 0;
}

/* A completer : afficher les racines, reelles ou complexes selon le signe
   du determinant. */
void Afficher_racines(float d, float s1r_p, float s1i_p, float s2r_p, float s2i_p)
{
}
