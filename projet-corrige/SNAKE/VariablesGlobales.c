#include <SDL3/SDL.h>

#include "MesTypes.h"
#include "Bibliotheque_header/TypeBoiteSaisie.h"
#include "Bibliotheque_header/TypeBouton.h"
#include "Bibliotheque_header/TypeZoneTexte.h"

//===============================================================
// Déclaration des Fenetres necessaires à l'application
//==============================================================*/

SDL_Window*      window                         ;
SDL_Renderer*    renderer                       ;

//===============================================================
// Déclaration des Boutons utilisés
//==============================================================*/

type_Bouton ListeBouton_Menu_Acceuil[3] ;

//===============================================================
// Déclaration des zones de texte utilisés
//==============================================================*/

type_ZoneTexte texteAccueil ;

//===============================================================
// Déclaration des textures utilisées
//==============================================================*/

SDL_Texture*     TEXTURE_FOND_ACCEUIL            ;
