
#include <SDL3/SDL.h>
#include <SDL3_ttf/SDL_ttf.h>
#include <SDL3_image/SDL_image.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "ConfigurationJeu.h"
#include "MesTypes.h"
#include "VariablesGlobales.h"

#include "Bibliotheque_header/OutilsDessin.h"
#include "Bibliotheque_header/OutilsBoiteSaisie.h"
#include "Bibliotheque_header/OutilsCouleur.h"
#include "Bibliotheque_header/OutilsZoneTexte.h"
#include "InitialisationJeu.h"


/*=======================================================================
   sur_le_corps
   Indique si la case (cx, cy) est occupee par le corps du serpent.
   depuis : index de depart dans le tableau corps (0 = toute la longueur,
            1 = on ignore la tete -- utile apres avancement).
   Renvoie 1 si la case est occupee, 0 sinon.
========================================================================*/
int sur_le_corps(int cx, int cy, int depuis) {

    for (int i = depuis; i < serpent.taille; i++) {
        if ((int)serpent.corps[i].x == cx && (int)serpent.corps[i].y == cy)
            return 1;
    }
    return 0;

}


/*=======================================================================
   SP_Nouvelle_Pomme
   Tire une case aleatoire dans la grille jusqu'a en trouver une qui
   n'est pas sur le corps du serpent, puis y place la pomme.
========================================================================*/
void SP_Nouvelle_Pomme(void) {

    do {
        pomme.x = (float)(rand() % NOMBRE_CELLULE_LARGEUR);
        pomme.y = (float)(rand() % NOMBRE_CELLULE_HAUTEUR);
    } while (sur_le_corps((int)pomme.x, (int)pomme.y, 0));

}


/*=======================================================================
   SP_Initialisation_Partie
   Prepare une nouvelle partie :
   - le serpent part au centre de la grille, LONGUEUR_DEPART segments, tete
     a droite (corps[0]) et corps qui s'etend vers la gauche, direction
     initiale a droite ;
   - score et partie_terminee sont remis a zero ;
   - une premiere pomme est posee hors du corps.

   On ne prend pas TAILLE_INITIALE comme longueur de depart : valant 20 sur une
   grille 20 par 20, le serpent remplirait une ligne entiere et toucherait le
   mur des le premier pas. Un serpent court au centre est jouable, comme dans la
   reference jeu_demo.c.
========================================================================*/
void SP_Initialisation_Partie(void) {

    /* A TOI. Prepare une nouvelle partie :
         - donne au serpent une longueur de depart courte, LONGUEUR_DEPART,
         - place le serpent au centre de la grille, tete en corps[0] et corps qui
           s'etend vers la gauche, direction initiale a droite,
         - remets score et partie_terminee a zero,
         - pose une premiere pomme hors du corps avec SP_Nouvelle_Pomme.
       Tu peux t'inspirer de init_serpent et nouvelle_pomme dans jeu_demo.c. */

}
