#ifndef COULEURS_H_INCLUDED
#define COULEURS_H_INCLUDED

#include "MesTypes.h"
#include "Bibliotheque_header/TypeBoiteSaisie.h"
#include "Bibliotheque_header/TypeBouton.h"
#include "Bibliotheque_header/TypeZoneTexte.h"
//===============================================================
// D�claration des Fenetres necessaires � l'application
//==============================================================*/

extern SDL_Window*      window                         ;
extern SDL_Renderer*    renderer                       ;

//===============================================================
// D�claration des Boutons utilis�s
//==============================================================*/

extern type_Bouton ListeBouton_Menu_Acceuil[3] ;

//===============================================================
// D�claration des zones de texte utilis�s
//==============================================================*/

extern type_ZoneTexte texteAccueil           ;

//===============================================================
// D�claration des textures utilis�es
//==============================================================*/

extern SDL_Texture*     TEXTURE_FOND_ACCEUIL            ;

//===============================================================
// Declaration des variables de l'etat du jeu Snake
//==============================================================*/

/* Le serpent : corps, taille courante et direction. */
extern type_serpent serpent ;

/* Position de la pomme sur la grille. */
extern type_point pomme ;

/* Score courant (nombre de pommes mangees). */
extern int score ;

/* Vaut 1 quand une collision a mis fin a la partie, 0 sinon. */
extern int partie_terminee ;

#endif // COULEURS_H_INCLUDED
