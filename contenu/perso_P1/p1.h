#ifndef P1_H
#define P1_H
#include <stdio.h>

/* Les états du menu, comme l'enum du projet Snake. */
enum { MENU_ACCUEIL, MENU_PARAMETRAGE, MENU_JEU, QUITTER };

void changer_par_valeur(int etat);
void changer_par_pointeur(int* p_etat);
#endif
