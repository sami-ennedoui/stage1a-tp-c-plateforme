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
     Surveille l'activite du clavier. Quand un evenement SDL_EVENT_KEY_DOWN
     est detecte ( Appuie sur une touche ) , on cherche quel touche est
     sollicitee parmi {UP, DOWN, LEFT, RIGHT}. On a choisi ici le code
     suivant pour chaque touche :

     UP = 0 / DOWN = 1 / LEFT = 2 / RIGHT = 3

     Les tests des directions utilisent :

     typedef enum {UP, DOWN, LEFT, RIGHT} Direction; ( dans MesTypes.h )

     Cela permet de manipuler les labels UP, DOWN, LEFT, RIGHT au lieu des
     {0,1,2,3}. L'ecriture du code est alors facilitee

     Le SP retourne donc le code de la touche qui vient d'etre appuyee.
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


/*=======================================================================
   SP_Avancer_Serpent
   Effectue un pas de jeu sans aucun rendu graphique.

   Principe (porte de avancer dans jeu_demo.c) :
     1. Calcul du deplacement (dx, dy) selon la direction courante.
     2. Decalage du tableau corps : chaque element prend la place de son
        voisin cote tete (concept P3 du cours).
     3. Avancement de la tete (corps[0]) d'une cellule.
     4. Detection des collisions :
          - sortie de la grille -> partie_terminee = 1, renvoie 0
          - tete sur le corps   -> partie_terminee = 1, renvoie 0
     5. Si la tete atteint la pomme :
          - on rallonge d'un segment (l'ancienne queue reprend sa place)
          - score++
          - nouvelle pomme posee hors du corps
     6. Renvoie 1 si le serpent est vivant.
========================================================================*/

int SP_Avancer_Serpent(void) {

    /* A TOI. Ecris ici un pas de jeu, sans rien dessiner, en t'inspirant de la
       fonction avancer de jeu_demo.c et du concept de decalage de tableau vu en
       cours :
         - calcule le deplacement selon serpent.dir,
         - decale le corps, chaque segment prend la place du precedent cote tete,
         - avance la tete d'une cellule,
         - detecte la sortie de grille et la collision avec le corps, et dans ce
           cas pose partie_terminee a 1 puis renvoie 0,
         - si la tete atteint la pomme, rallonge le serpent, incremente score et
           pose une nouvelle pomme.
       Renvoie 1 tant que le serpent est vivant. */
    return 1;

}


void Update_Jeu(void)
{


}
