#ifndef HARNAIS_JALON1_H
#define HARNAIS_JALON1_H
#include <SDL3/SDL.h>
#include "MesTypes.h"

/* Le sous-programme que tu écris, dans GestionMenuParametrage.c. */
void SP_Gestion_Evenements_MENU_PARAMETRAGE(SDL_Event e, int* p_etatMenu);

/* Fourni par le harnais : fait comme si le bouton donné était sous le clic.
   Passe -1 pour un clic en dehors de tout bouton. */
void simuler_clic(int bouton);
#endif
