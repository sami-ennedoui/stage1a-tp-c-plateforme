#ifndef TYPEBOUTON_H_INCLUDED
#define TYPEBOUTON_H_INCLUDED

// Structure pour le bouton

typedef struct {
    SDL_FRect rect;                 // Rectangle du bouton
    char *label;                    // Texte du bouton
    SDL_Color textColor;            // Couleur du texte
    SDL_Color backGroundColor;      // Couleur de fond du bouton
    SDL_Surface *textSurface ;
    SDL_Texture *textTexture ;
    SDL_FRect textRect ;

} type_Bouton;

#endif // TYPEBOUTON_H_INCLUDED
