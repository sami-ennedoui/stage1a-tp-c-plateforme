
#include <SDL3_ttf/SDL_ttf.h>
#include <SDL3/SDL.h>
#include <stdio.h>
#include <string.h>

//#include "../MesVariablesGlobales.h"
//#include "../MesTypes.h"

#include "../Bibliotheque_header/TypeZoneTexte.h"

extern SDL_Renderer* renderer ;

void SP_Creation_Zone_Texte (type_ZoneTexte* zoneTexte,char* nomPolice,float taillePolice,float x,float y) {

    char source[100]="polices/";

    strcat(source,nomPolice ) ;

    strcat(source,".ttf" ) ;

    zoneTexte->taillePolice = taillePolice ;
    zoneTexte->font = TTF_OpenFont(source,zoneTexte->taillePolice);

    if (zoneTexte->font == NULL) {
    printf("Erreur chargement police : %s\n", SDL_GetError());
    }
    //zoneTexte->textSurface = TTF_RenderText_Blended(zoneTexte->font, text, strlen(text),textColor);
    //zoneTexte->textTexture = SDL_CreateTextureFromSurface(renderer, zoneTexte->textSurface);

    zoneTexte->x = x ;
    zoneTexte->y = y ;

    //TTF_CloseFont(zoneTexte->font) ;
}

void SP_Dessiner_Zone_Texte (type_ZoneTexte zoneTexte , char* text , SDL_Color textColor ) {

    zoneTexte.textSurface = TTF_RenderText_Blended(zoneTexte.font, text, strlen(text),textColor);
    zoneTexte.textTexture = SDL_CreateTextureFromSurface(renderer, zoneTexte.textSurface);

    int textWidth =  zoneTexte.textSurface->w;
    int textHeight = zoneTexte.textSurface->h;

    SDL_FRect renderQuad = { zoneTexte.x, zoneTexte.y , textWidth, textHeight };
    SDL_RenderTexture(renderer, zoneTexte.textTexture, NULL, &renderQuad);

}

