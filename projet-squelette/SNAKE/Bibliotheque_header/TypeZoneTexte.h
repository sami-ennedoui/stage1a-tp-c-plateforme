#ifndef TYPEZONETEXTE_H_INCLUDED
#define TYPEZONETEXTE_H_INCLUDED

typedef struct {

 float x ;
 float y ;
 float taillePolice ;
 SDL_Surface *textSurface ;
 SDL_Texture *textTexture ;
 TTF_Font* font;

} type_ZoneTexte ;

#endif // TYPEZONETEXTE_H_INCLUDED
