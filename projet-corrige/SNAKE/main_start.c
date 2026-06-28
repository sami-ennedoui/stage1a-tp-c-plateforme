#include <SDL3/SDL.h>
#include <stdio.h>

#define WINDOW_WIDTH  800
#define WINDOW_HEIGHT 600
#define CELL_SIZE     64

// Fonction pour dessiner un cercle rempli dans un renderer
void SDL_RenderFillCircle(SDL_Renderer *renderer, int centreX, int centreY, int radius) {
    for (int y = -radius; y <= radius; y++) {
        for (int x = -radius; x <= radius; x++) {
            if (x*x + y*y <= radius*radius) {
                SDL_RenderPoint(renderer, centreX + x, centreY + y);
            }
        }
    }
}

int main(int argc, char* argv[]) {
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        printf("Erreur SDL_Init: %s\n", SDL_GetError());
        return 1;
    }

    SDL_Window *window = SDL_CreateWindow("Texture avec Cercle (SDL3)", WINDOW_WIDTH, WINDOW_HEIGHT, 0);
    if (!window) {
        printf("Erreur SDL_CreateWindow: %s\n", SDL_GetError());
        SDL_Quit();
        return 1;
    }

    SDL_Renderer *renderer = SDL_CreateRenderer(window, NULL);
    if (!renderer) {
        printf("Erreur SDL_CreateRenderer: %s\n", SDL_GetError());
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    // 1. Créer une texture pour le cercle
    SDL_Texture *circleTexture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA8888, SDL_TEXTUREACCESS_TARGET, CELL_SIZE, CELL_SIZE);
    if (!circleTexture) {
        printf("Erreur SDL_CreateTexture: %s\n", SDL_GetError());
        SDL_DestroyRenderer(renderer);
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    // 2. Activer le blending pour la transparence
    //SDL_SetTextureBlendMode(circleTexture, SDL_BLENDMODE_BLEND);

    // 3. Dessiner le cercle dans la texture
    //SDL_SetRenderTarget(renderer, circleTexture);

    // Fond transparent
    //SDL_SetRenderDrawColor(renderer, 0, 0, 0, 0);
    //SDL_RenderClear(renderer);

    // Dessiner le cercle vert
    //SDL_SetRenderDrawColor(renderer, 0, 255, 0, 255);
    //SDL_RenderFillCircle(renderer, CELL_SIZE / 2, CELL_SIZE / 2, CELL_SIZE / 2);

    // 4. Revenir au rendu sur la fenêtre
    //SDL_SetRenderTarget(renderer, NULL);

    // Position du cercle à l'écran
    //float cx = WINDOW_WIDTH / 2;
    //float cy = WINDOW_HEIGHT / 2;

    int running = 1;
    while (1) {


        // Effacer l'écran
        //SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        //SDL_RenderClear(renderer);

        // 5. Dessiner la texture à l'écran
        //SDL_FRect dest = {cx - CELL_SIZE/2.0f, cy - CELL_SIZE/2.0f, CELL_SIZE, CELL_SIZE};
        //SDL_RenderTexture(renderer, circleTexture, NULL, &dest);

        // Mettre à jour l'affichage
        //SDL_RenderPresent(renderer);
        //SDL_Delay(16);
    }

    // Nettoyage
    SDL_DestroyTexture(circleTexture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
