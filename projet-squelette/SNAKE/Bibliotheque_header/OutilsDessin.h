#ifndef OUTILSDESSIN_H_INCLUDED
#define OUTILSDESSIN_H_INCLUDED

#include <SDL3/SDL.h>
#include <SDL3_image/SDL_image.h>
#include <SDL3_ttf/SDL_ttf.h>
#include <stdio.h>
#include <math.h>

#include "../VariablesGlobales.h"

SDL_Texture* SP_Creation_Texture_Rectangle( int , int , SDL_Color ) ;
void SP_Dessiner_Texture(SDL_Texture* , int  , int  , int  , int )  ;
SDL_Surface* SP_Charger_PNG_Dans_surface (char* );
void SP_Copier_Texture_Dans_Texture ( float  , float  , SDL_Texture*  , SDL_Texture*  ) ;
SDL_Texture* SP_Creation_Texture_Depuis_Image (char* , int ,int ) ;
int SP_Test_Couleur_Egal(SDL_Color , SDL_Color ) ;

SDL_Texture* SP_Creation_Cercle_Dans_Texture_Carre(float radius, int tailleCarre , SDL_Color couleur) ;
SDL_Texture* SP_Creer_Rectangle_Dans_Texture(int , int , SDL_Color );

void SP_Dessiner_Cercle_Texture( float , float , float  , SDL_Color  ) ;
void SP_Nettoyer_Ecran (SDL_Color ) ;
void SP_Nettoyer_Texture (SDL_Texture* texture , SDL_Color couleur) ;

void Mise_A_jour_Fenetre () ;

#endif
