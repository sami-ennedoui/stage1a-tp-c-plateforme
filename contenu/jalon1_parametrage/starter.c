/* Jalon 1. Écris le menu Paramétrage par analogie avec GestionMenuAcceuil.c.
   Quatre boutons à créer, et la gestion des clics qui change l'état du menu. */
#include <SDL3/SDL.h>
#include <stdio.h>

#include "MesTypes.h"
#include "ConfigurationJeu.h"
#include "Bibliotheque_header/TypeBouton.h"
#include "Bibliotheque_header/OutilsBouton.h"
#include "Bibliotheque_header/OutilsCouleur.h"

/* La liste des boutons du menu Paramétrage. */
type_Bouton ListeBouton_Menu_Parametrage[4];

void SP_Structure_Menu_Parametrage(void) {
    /* À TOI. Crée les 4 boutons avec SP_Creation_Bouton, comme dans l'accueil :
       couleur serpent, couleur fond, couleur bord, retour. */
}

void SP_Gestion_Evenements_MENU_PARAMETRAGE(SDL_Event e, int* p_etatMenu) {
    /* À TOI. Récupère le bouton cliqué avec SP_Surveillance_Bouton, puis change
       *p_etatMenu vers le bon état selon le bouton. */
}
