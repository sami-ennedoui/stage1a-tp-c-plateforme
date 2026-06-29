#include <SDL3/SDL.h>
#include <SDL3_image/SDL_image.h>
#include <SDL3_ttf/SDL_ttf.h>
#include <stdio.h>
#include <math.h>

#include "../ConfigurationJeu.h"

extern SDL_Renderer* renderer ;


SDL_Texture* SP_Creation_Texture_Rectangle( int largeur_texture, int hauteur_texture, SDL_Color couleur_fond)
{
    SDL_Texture* texture = SDL_CreateTexture( renderer, SDL_PIXELFORMAT_RGBA8888, SDL_TEXTUREACCESS_TARGET, largeur_texture, hauteur_texture  );

    if (!texture) {
        printf(" SP_Creation_Texture : Erreur SDL_CreateTexture: %s\n", SDL_GetError());
        return NULL;
    }

    // Activer le blending (important pour l'alpha)
    SDL_SetTextureBlendMode(texture, SDL_BLENDMODE_BLEND);

    // Rendu dans la texture
    SDL_SetRenderTarget(renderer, texture);

    // Remplir le fond avec la couleur demandée
    SDL_SetRenderDrawColor(
        renderer,
        couleur_fond.r,
        couleur_fond.g,
        couleur_fond.b,
        couleur_fond.a
    );
    SDL_RenderClear(renderer);

    // Retour au rendu normal (fenêtre)
    SDL_SetRenderTarget(renderer, NULL);

    return texture;
}

void SP_Dessiner_Texture(SDL_Texture* texture , int x , int y , int largeur_texture , int hauteur_texture) {

    SDL_FRect dstRect;

    dstRect.x = (float)(x);  // position x dans la grille
    dstRect.y = (float)(y);              // position y
    dstRect.w = (float)(largeur_texture);
    dstRect.h = (float)(hauteur_texture) ;
    SDL_RenderTexture(renderer, texture, NULL, &dstRect);

}




SDL_Surface* SP_Charger_PNG_Dans_surface (char* nom_fichier_image)
{
    char destination[100]="images/";
    strcat(destination,nom_fichier_image) ;

    SDL_Surface* surface = IMG_Load(destination);

    if (!surface) SDL_Log("IMG_Load Error: %s", SDL_GetError());

    // SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surf);
    // SDL_DestroySurface(surf);

    // SDL_RenderTexture(renderer, texture, NULL, NULL);

     return(surface) ;
}

SDL_Texture* SP_Creation_Texture_Depuis_Image (char* nom_fichier_image, int largeur_texture,int hauteur_texture) {


    SDL_Surface* surface = SP_Charger_PNG_Dans_surface(nom_fichier_image)     ;

    SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface );
    SDL_DestroySurface(surface);

    if (!texture) {
        printf(" SP_Charger_Image_Dans_Texture : Erreur SDL_CreateTexture: %s\n", SDL_GetError());
        SDL_DestroyRenderer(renderer);
        //SDL_DestroyWindow(window);
        SDL_Quit();
    }

    // 2. Activer le blending pour la transparence
    SDL_SetTextureBlendMode(texture, SDL_BLENDMODE_BLEND);

    // 3. Dessiner le cercle dans la texture
    SDL_SetRenderTarget(renderer, texture);

    // Fond transparent
    SDL_SetRenderDrawColor(renderer, 0,0,0,0);
    SDL_RenderClear(renderer);

    // Dessiner image dans texture
    SDL_FRect dest = { 0 ,0 ,largeur_texture,hauteur_texture };
    SDL_RenderTexture(renderer, texture, NULL, &dest);

    // 4. Revenir au rendu sur la fenêtre
    SDL_SetRenderTarget(renderer, NULL);

    return texture ;

}


void SP_Copier_Texture_Dans_Texture ( float x , float y , SDL_Texture* texture_cible , SDL_Texture* texture_source ) {


    float w ;
    float h ;

    SDL_GetTextureSize(texture_source, &w, &h);


    SDL_FRect dstRect;
    dstRect.w = w;  // largeur de la cellule
    dstRect.h = h;  // hauteur de la cellule


    SDL_SetRenderTarget(renderer, texture_cible );

    dstRect.x = x;  // position x dans la grille
    dstRect.y = y;              // position y
    SDL_RenderTexture(renderer, texture_source, NULL, &dstRect);

    // Revenir au rendu sur la fenêtre
    SDL_SetRenderTarget(renderer, NULL);


}







int SP_Test_Couleur_Egal(SDL_Color c1, SDL_Color c2) {
    return (c1.r == c2.r && c1.g == c2.g && c1.b == c2.b && c1.a == c2.a);
}


/*===================================================================================
 SP pour nettoyer l'écran avec la couleur choisie
 color      ==> Couleur de remplissage de l'écran
=====================================================================================*/

void SP_Nettoyer_Ecran (SDL_Color couleur) {

        SDL_SetRenderDrawColor(renderer, couleur.r, couleur.g,couleur.b,couleur.a);
        SDL_RenderClear(renderer);

}

/*===================================================================================
 SP pour nettoyer l'écran avec la couleur choisie
 color      ==> Couleur de remplissage de l'écran
=====================================================================================*/

void Mise_A_jour_Fenetre () {

    SDL_RenderPresent(renderer);

}


/*===================================================================================
 SP pour nettoyer l'écran avec la couleur choisie
 color      ==> Couleur de remplissage de l'écran
=====================================================================================*/

void SP_Nettoyer_Texture (SDL_Texture* texture , SDL_Color couleur) {

SDL_SetRenderTarget(renderer, texture);  // cibler la texture
SDL_SetRenderDrawColor(renderer, couleur.r, couleur.g,couleur.b,couleur.a);
SDL_RenderClear(renderer);
SDL_SetRenderTarget(renderer, NULL);
}

/*===================================================================================
 Dessin de cercle plein
=====================================================================================*/

void SP_Dessiner_Cercle_Texture( float centreX, float centreY, float radius , SDL_Color color ) {

    //SDL_SetRenderDrawColor(renderer, color.r, color.g, color.b, color.a);

    for (float y = -radius; y <= radius; y++) {
        for (float x = -radius; x <= radius; x++) {
            if (x*x + y*y <= radius*radius) {
                SDL_RenderPoint(renderer, centreX + x, centreY + y);
            }
        }
    }
}


SDL_Texture* SP_Creation_Cercle_Dans_Texture_Carre(float radius, int tailleCarre , SDL_Color couleur)
{

    SDL_Texture *circleTexture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA8888, SDL_TEXTUREACCESS_TARGET, tailleCarre, tailleCarre);

    if (!circleTexture) {
        printf("SP_Creer_Cercle_Dans_Texture_Carre - Erreur SDL_CreateTexture: %s\n", SDL_GetError());
        SDL_DestroyRenderer(renderer);
        //SDL_DestroyWindow(window);
        SDL_Quit();
    }

    // 2. Activer le blending pour la transparence
    SDL_SetTextureBlendMode(circleTexture, SDL_BLENDMODE_BLEND);

    // 3. Dessiner le cercle dans la texture
    SDL_SetRenderTarget(renderer, circleTexture);

    // Fond transparent
    SDL_SetRenderDrawColor(renderer, 0,0,0,0);
    SDL_RenderClear(renderer);

    // Dessiner le cercle vert
    //DL_SetRenderDrawColor(renderer, 0, 255, 0, 255);
    SDL_SetRenderDrawColor(renderer, couleur.r, couleur.g, couleur.b, 255 );
    SP_Dessiner_Cercle_Texture( TAILLE_CELLULE / 2, TAILLE_CELLULE / 2, radius , couleur );

    // 4. Revenir au rendu sur la fenêtre
    SDL_SetRenderTarget(renderer, NULL);

    return circleTexture;
}
