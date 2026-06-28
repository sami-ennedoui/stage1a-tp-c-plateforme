#include <SDL3/SDL.h>

#include "MesTypes.h"
#include "Bibliotheque_header/TypeBoiteSaisie.h"
#include "Bibliotheque_header/TypeBouton.h"
#include "Bibliotheque_header/TypeZoneTexte.h"

//===============================================================
// D�claration des Fenetres necessaires � l'application
//==============================================================*/

SDL_Window*      window                         ;
SDL_Renderer*    renderer                       ;

//===============================================================
// D�claration des Boutons utilis�s
//==============================================================*/

type_Bouton ListeBouton_Menu_Acceuil[3] ;

//===============================================================
// D�claration des zones de texte utilis�s
//==============================================================*/

type_ZoneTexte texteAccueil ;

//===============================================================
// D�claration des textures utilis�es
//==============================================================*/

SDL_Texture*     TEXTURE_FOND_ACCEUIL            ;

//===============================================================
// Definition des variables de l'etat du jeu Snake
//==============================================================*/

type_serpent serpent ;

type_point pomme ;

int score ;

int partie_terminee ;
