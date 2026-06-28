#include <math.h>
#include <SDL3/SDL.h>
#include <SDL3_ttf/SDL_ttf.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "ConfigurationJeu.h"
#include "MesTypes.h"
#include "VariablesGlobales.h"

#include "Bibliotheque_header/TypeBoiteSaisie.h"
#include "Bibliotheque_header/OutilsBoiteSaisie.h"
#include "Bibliotheque_header/OutilsDessin.h"
#include "Bibliotheque_header/OutilsZoneTexte.h"
#include "Bibliotheque_header/OutilsBouton.h"
#include "Bibliotheque_header/OutilsCouleur.h"

#include "InitialisationJeu.h"
#include "GestionJeu.h"


/*=======================================================================
     SP de gestion du clavier
     Surveille l'activité du clavier. Quand un évènement SDL_EVENT_KEY_DOWN
     est détecté ( Appuie sur une touche ) , on cherche quel touche est
     sollicitée parmi {UP, DOWN, LEFT, RIGHT}. On a choisit ici le code
     suivant pour chaque touche :

     UP = 0 / DOWN = 1 / LEFT = 2 / RIGHT = 3

     Les test des directions utilisent :

     typedef enum {UP, DOWN, LEFT, RIGHT} Direction; ( dans MesTypes.h )

     Cela permet de manipuler les labels UP, DOWN, LEFT, RIGHT au lieu des
     {0,1,2,3}. L'écriture du code est alors facilitée

     Le SP retourne donc le code de la touche qui vient d'être appuyée.
     S'il n'y a pas d'appuie, le SP renvoie -1
========================================================================*/

int SP_Gestion_Clavier(SDL_Event event) {

int direction = -1  ;


    switch (event.key.key)  {

    case SDLK_UP:       direction = UP ; break;

    case SDLK_DOWN:     direction = DOWN ; break;

    case SDLK_LEFT:     direction = LEFT ;  break;

    case SDLK_RIGHT:    direction = RIGHT ;  break;


}

return(direction) ;

}


void Update_Jeu()
{


}



