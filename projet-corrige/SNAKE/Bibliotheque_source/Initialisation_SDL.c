#include <SDL3/SDL.h>
#include <SDL3_ttf/SDL_ttf.h>
#include <SDL3_image/SDL_image.h>
#include <stdio.h>

#include "../ConfigurationJeu.h"

extern SDL_Window* window ;
extern SDL_Renderer* renderer ;

/*=================================================================================================
 SP d'initialisation de la fenetre graphique

 Utilise les variables globales suivantes ( définies dans "MesTypes.h" ) :

SDL_Window*      window
SDL_Renderer*    renderer

Ce sont ces variables qui seront utilisées dans tous le projet pour les opérations graphiques

===============================================================================================*/

void SP_Initialisation_SDL() {

     if (SDL_Init(SDL_INIT_VIDEO) == 0) {
        printf("Erreur SDL_Init: %s\n", SDL_GetError());

    }

    if (TTF_Init() == 0) {
        printf("Erreur d'initialisation de SDL_ttf \n");
        SDL_Quit();

    }

    window = SDL_CreateWindow("Texture avec Cercle (SDL3)", FENETRE_LARGEUR, FENETRE_HAUTEUR, 0);
    if (!window) {
        printf("Erreur SDL_CreateWindow: %s\n", SDL_GetError());
        SDL_Quit();

    }

    renderer = SDL_CreateRenderer(window, 0);

    if (!renderer) {
        printf("Erreur SDL_CreateRenderer: %s\n", SDL_GetError());
        SDL_DestroyWindow(window);
        SDL_Quit();

    }

    SDL_StartTextInput(window) ;

}

void SP_Quitter_SDL() {

SDL_StopTextInput(window);
SDL_Quit();

}
