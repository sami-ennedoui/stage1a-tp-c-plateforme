/* P1 corrigé. Implémentation seule, le main et les vérifications sont dans tests.c. */
#include "p1.h"

/* Passage par VALEUR : la fonction reçoit une copie, la modification est perdue. */
void changer_par_valeur(int etat) {
    etat = MENU_PARAMETRAGE;
}

/* Passage par POINTEUR : la fonction reçoit l'adresse, donc *p_etat modifie
   bien la variable de l'appelant. C'est la signature de p_etatMenu du projet. */
void changer_par_pointeur(int* p_etat) {
    *p_etat = MENU_PARAMETRAGE;
}
