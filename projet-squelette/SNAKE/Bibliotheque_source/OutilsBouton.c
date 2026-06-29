
#include <stdio.h>

#include <SDL3_ttf/SDL_ttf.h>
#include <SDL3/SDL.h>

#include "../Bibliotheque_header/TypeBoiteSaisie.h"
#include "../Bibliotheque_header/TypeBouton.h"

extern SDL_Renderer* renderer ;

 void SP_Creation_Bouton_Texture(type_Bouton *button,float x, float y,float h, float w,SDL_Texture *texture)
{
    button->rect.x = x;
    button->rect.y = y;
    button->rect.w = w;
    button->rect.h = h;

    button->textTexture = texture;

    button->textRect.x = x;
    button->textRect.y = y;
    button->textRect.w = w;
    button->textRect.h = h;
}


void SP_Creation_Bouton (type_Bouton *button, char* nomPolice,float taillePolice,float x,float y,float w,float h,char* text,SDL_Color textColor,SDL_Color backGroundColor)
{


    button->rect.h=h;
    button->rect.w=w;
    button->rect.x=x;
    button->rect.y=y;
    button->label=text;     // Texte du bouton
    button->textColor = textColor;       // Couleur du texte
    button->backGroundColor = backGroundColor;      // Couleur de fond du bouton

    TTF_Font*        font       ;

    char source[100]="polices/";

    strcat(source,nomPolice ) ;

    strcat(source,".ttf" ) ;
    // Charger une police

    font = TTF_OpenFont(source,taillePolice);

    if (font == NULL) {
    printf("Erreur chargement police : %s\n", SDL_GetError());
    }

    // Créer la surface et la texture pour le texte du bouton
    button->textSurface = TTF_RenderText_Blended(font, button->label, strlen(button->label) , button->textColor);
    button->textTexture = SDL_CreateTextureFromSurface(renderer, button->textSurface);
    SDL_DestroySurface(button->textSurface);  // Libérer la surface après la création de la texture

    if (button->textTexture) {
        // Calculer la position pour centrer le texte dans le bouton
        float textWidth = 0, textHeight = 0;
        SDL_GetTextureSize(button->textTexture, &textWidth, &textHeight);
        SDL_FRect textRect = {
            button->rect.x + (button->rect.w - textWidth) / 2,  // Centrer horizontalement
            button->rect.y + (button->rect.h - textHeight) / 2, // Centrer verticalement
            (float)textWidth,
            (float)textHeight
        };

        button->textRect = textRect ;

    }

    TTF_CloseFont(font);

}

void SP_Dessiner_Bouton(type_Bouton button) {

        // Dessiner le rectangle du bouton avec la couleur de fond
        SDL_SetRenderDrawColor(renderer, button.backGroundColor.r, button.backGroundColor.g, button.backGroundColor.b, button.backGroundColor.a);
        SDL_RenderFillRect(renderer, &button.rect);

        // Dessiner le texte sur le bouton
        SDL_RenderTexture(renderer, button.textTexture, NULL, &(button.textRect));


}

/*====================================================================================
 SP de vérification d'un bouton.
 Si la souris est sur la zone graphique d'un bouton, renvoie 1 , sinon renvoie 0
=====================================================================================*/

int checkButtonClick(SDL_FRect buttonRect, int mouseX, int mouseY) {
    // Vérifie si la souris est dans les limites du bouton
    return (mouseX >= buttonRect.x && mouseX <= (buttonRect.x + buttonRect.w) &&
            mouseY >= buttonRect.y && mouseY <= (buttonRect.y + buttonRect.h));
}


/*====================================================================================
 SP de gestion des boutons. Manipule des types Bouton
 boutonToCheck  ==> adresse du tableau contenant les boutons à surveiller
 nbBouton       ==> nombre de boutons à surveiller

 Retoune l'indice du tableau correspondant au numéro du bouton qui a été clické
 Rappel : les éléments d'un tableau commencent à 0 en Langage C
=====================================================================================*/

int SP_Surveillance_Bouton(SDL_Event e,type_Bouton* boutonToCheck,int nbBouton){

int boutonClicked = -1 ;

    if (e.type == SDL_EVENT_MOUSE_BUTTON_DOWN) {

            int mouseX = e.button.x;
            int mouseY = e.button.y;

            for (int i =0 ; i<nbBouton ; i++ ) {

            if (checkButtonClick(boutonToCheck[i].rect, mouseX, mouseY) )

                    boutonClicked = i;


            }

        }

return(boutonClicked) ;
}


