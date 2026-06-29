#include "p1.h"

int main(void) {
    int etat = MENU_ACCUEIL;

    changer_par_valeur(etat);
    if (etat != MENU_ACCUEIL) {
        printf("FAIL: le passage par valeur a modifie l'appelant\n");
        return 1;
    }

    changer_par_pointeur(&etat);
    if (etat != MENU_PARAMETRAGE) {
        printf("FAIL: le passage par pointeur n'a pas change l'etat, lu %d\n", etat);
        return 1;
    }

    printf("TOUT PASSE\n");
    return 0;
}
