
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
   - le serpent est place horizontalement sur la ligne centrale de la
     grille, TAILLE_INITIALE segments, tete a l'extremite droite
     (corps[0]), regardant a droite ;
   - score et partie_terminee sont remis a zero ;
   - une premiere pomme est posee hors du corps.

   Avec TAILLE_INITIALE = NOMBRE_CELLULE_LARGEUR = 20, le serpent occupe
   toute la ligne du milieu : corps[0].x = 19, corps[19].x = 0.
========================================================================*/
void SP_Initialisation_Partie(void) {

    srand((unsigned int)time(NULL));

    serpent.taille = TAILLE_INITIALE;
    serpent.dir    = RIGHT;

    for (int i = 0; i < serpent.taille; i++) {
        serpent.corps[i].x = (float)(NOMBRE_CELLULE_LARGEUR - 1 - i);
        serpent.corps[i].y = (float)(NOMBRE_CELLULE_HAUTEUR / 2);
    }

    score           = 0;
    partie_terminee = 0;

    SP_Nouvelle_Pomme();

}
