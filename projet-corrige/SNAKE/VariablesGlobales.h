#ifndef COULEURS_H_INCLUDED
#define COULEURS_H_INCLUDED

#include "MesTypes.h"
#include "Bibliotheque_header/TypeBoiteSaisie.h"
#include "Bibliotheque_header/TypeBouton.h"
#include "Bibliotheque_header/TypeZoneTexte.h"
//===============================================================
// Déclaration des Fenetres necessaires à l'application
//==============================================================*/

extern SDL_Window*      window                         ;
extern SDL_Renderer*    renderer                       ;

//===============================================================
// Déclaration des Boutons utilisés
//==============================================================*/

extern type_Bouton ListeBouton_Menu_Acceuil[3] ;

//===============================================================
// Déclaration des zones de texte utilisés
//==============================================================*/

extern type_ZoneTexte texteAccueil           ;

//===============================================================
// Déclaration des textures utilisées
//==============================================================*/

extern SDL_Texture*     TEXTURE_FOND_ACCEUIL            ;

#endif // COULEURS_H_INCLUDED
