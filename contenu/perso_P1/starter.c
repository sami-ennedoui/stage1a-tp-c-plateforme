/* P1. Implémente changer_par_pointeur pour que l'état de l'appelant change vraiment. */
#include "p1.h"

void changer_par_valeur(int etat) {
    etat = MENU_PARAMETRAGE;   /* perdu au retour, c'est voulu, pour montrer le contraste */
}

void changer_par_pointeur(int* p_etat) {
    /* À TOI. Tu reçois l'ADRESSE de la variable de l'appelant, pas sa valeur.
       Fais que cette variable devienne MENU_PARAMETRAGE. */
}
