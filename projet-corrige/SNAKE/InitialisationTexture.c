#include <SDL3/SDL.h>
#include <SDL3_ttf/SDL_ttf.h>
#include <SDL3_image/SDL_image.h>
#include <stdio.h>

#include "ConfigurationJeu.h"
#include "VariablesGlobales.h"

#include "Bibliotheque_header/OutilsDessin.h"
#include "Bibliotheque_header/OutilsCouleur.h"

//====================================================================================================
// SP d'initialisation des textures . Ce sous-programme charge une image PNG dans une texture
// qui pourra être utilisé à tout moment pour faire de dessin dans le renderer.
// Exemple d'utilisation  :
// TEXTURE_FOND_ACCEUIL        = SP_Creation_Texture_Depuis_Image("jungle.png",FENETRE_HAUTEUR,FENETRE_HAUTEUR);
//====================================================================================================

void SP_Initialisation_Textures() {

TEXTURE_FOND_ACCEUIL = SP_Creation_Texture_Depuis_Image("jungle.png",FENETRE_LARGEUR,FENETRE_HAUTEUR) ;

}
