#include <stdio.h>
#include <SDL3/SDL.h>
#include <SDL3_image/SDL_image.h>
#include <SDL3_ttf/SDL_ttf.h>


#include "../Bibliotheque_header/TypeBoiteSaisie.h"

extern SDL_Renderer* renderer ;

///////////////////////////////////////////////////////////////
// INPUT BOX
//////////////////////////////////////////////////////////////

void SP_Reinitialiser_boite_Saisie(type_BoiteSaisie* p_Boite_Saisie)
{

    p_Boite_Saisie->text[0] = '\0';
    p_Boite_Saisie->length = 0;  // si tu utilises un compteur de longueur

}


void Initialiser_boite_Saisie(type_BoiteSaisie* p_Boite_Saisie, float x, float y, float w, float h, char* nomPolice, int taillePolice)
{

    p_Boite_Saisie->length = 0;          // Initialisation de la longueur du texte
    p_Boite_Saisie->cursorVisible = 1;   // Le curseur est visible au départ
    p_Boite_Saisie->x = x;               // Position x de la boîte
    p_Boite_Saisie->y = y;               // Position y de la boîte
    p_Boite_Saisie->w = w;               // Largeur de la boîte
    p_Boite_Saisie->h = h;               // Hauteur de la boîte
    p_Boite_Saisie->active = 0;          // La boîte est active par défaut


    char source[100]="polices/";

    strcat(source,nomPolice ) ;

    strcat(source,".ttf" ) ;

    // Charger la police à chaque initialisation
    p_Boite_Saisie->font = TTF_OpenFont(source, taillePolice);

     if (!p_Boite_Saisie->font)
    {
        SDL_Log("Erreur chargement police: %s", SDL_GetError());
        return;
    }

    p_Boite_Saisie->text[0] = '\0';      // Initialise le texte vide

}

void Evenement_Boite_Saisie(type_BoiteSaisie *p_Boite_Saisie, SDL_Event event)
{
    if (!p_Boite_Saisie->active)
        return;

    switch (event.type)
    {
        case SDL_EVENT_KEY_DOWN:
            if (event.key.key == SDLK_RETURN)
            {
                p_Boite_Saisie->active = 0;  // fin de saisie
            }
            else if (event.key.key == SDLK_BACKSPACE && p_Boite_Saisie->length > 0)
            {
                p_Boite_Saisie->length--;
                p_Boite_Saisie->text[p_Boite_Saisie->length] = '\0'; // Assurer que la chaîne se termine correctement après un Backspace
            }
            break;

        case SDL_EVENT_TEXT_INPUT:
            if (p_Boite_Saisie->length + strlen(event.text.text) < sizeof(p_Boite_Saisie->text))  // Protection contre le débordement
            {
                strcat(p_Boite_Saisie->text, event.text.text);
                p_Boite_Saisie->length += strlen(event.text.text);
                p_Boite_Saisie->text[p_Boite_Saisie->length] = '\0';  // S'assurer que la chaîne est bien terminée après chaque ajout
            }
            break;
    }
}

void Dessiner_Boite_Saisie(type_BoiteSaisie maBoite_Saisie)
{
    SDL_FRect rect = { (float)maBoite_Saisie.x, (float)maBoite_Saisie.y, (float)maBoite_Saisie.w, (float)maBoite_Saisie.h };

    SDL_SetRenderDrawColor(renderer, 40,40,40,255);
    SDL_RenderFillRect(renderer, &rect);

    SDL_SetRenderDrawColor(renderer, 255,255,255,255);
    SDL_RenderRect(renderer, &rect);

    SDL_Color color = {255,255,255,255};

    if (maBoite_Saisie.length > 0)
    {
        SDL_Surface *surf = TTF_RenderText_Blended(maBoite_Saisie.font, maBoite_Saisie.text, 0, color);
        if (surf)
        {
            SDL_Texture *tex = SDL_CreateTextureFromSurface(renderer, surf);
            SDL_FRect textRect = { rect.x+5, rect.y + (rect.h - surf->h)/2.0f,
                                   (float)surf->w, (float)surf->h };
            SDL_RenderTexture(renderer, tex, NULL, &textRect);
            SDL_DestroySurface(surf);
            SDL_DestroyTexture(tex);

            if (maBoite_Saisie.cursorVisible)
            {
                SDL_FRect cursor = { textRect.x + textRect.w + 2, textRect.y, 2, textRect.h };
                SDL_SetRenderDrawColor(renderer, 255,255,255,255);
                SDL_RenderFillRect(renderer, &cursor);
            }
        }
    }
    else if (maBoite_Saisie.cursorVisible)
    {
        SDL_FRect cursor = { rect.x + 5, rect.y + 5, 2, rect.h - 10 };
        SDL_SetRenderDrawColor(renderer, 255,255,255,255);
        SDL_RenderFillRect(renderer, &cursor);
    }
}
