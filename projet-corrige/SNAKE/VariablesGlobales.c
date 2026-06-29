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
type_Bouton ListeBouton_Menu_Parametrage[4] ;
type_Bouton ListeBouton_Menu_Couleur_Snake[5] ;
type_Bouton ListeBouton_Menu_Couleur_Stade[5] ;
type_Bouton ListeBouton_Menu_Couleur_Bord[5] ;

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

/* Couleurs du jeu, modifiables depuis les menus Parametrage.
   Valeurs par defaut : palette verte originale de jeu_demo.c. */
SDL_Color couleur_serpent = {70,  200, 90,  255} ;
SDL_Color couleur_stade   = {40,  90,  50,  255} ;
SDL_Color couleur_bord    = {90,  140, 90,  255} ;

type_serpent serpent ;

type_point pomme ;

int score ;

int partie_terminee ;
