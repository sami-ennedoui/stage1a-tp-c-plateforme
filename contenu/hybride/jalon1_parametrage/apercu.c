/* Aperçu du jalon 1 : ouvre une fenêtre et dessine les boutons que l'étudiant
   a construits dans SP_Structure_Menu_Parametrage. Échap ou la croix pour fermer. */
#include <SDL3/SDL.h>
#include <SDL3_ttf/SDL_ttf.h>

#include "ConfigurationJeu.h"
#include "MesTypes.h"
#include "VariablesGlobales.h"
#include "Bibliotheque_header/Initialisation_SDL.h"
#include "Bibliotheque_header/OutilsDessin.h"
#include "Bibliotheque_header/OutilsCouleur.h"
#include "Bibliotheque_header/OutilsBouton.h"
#include "Bibliotheque_header/TypeBouton.h"
#include "InitialisationTexture.h"

extern SDL_Renderer* renderer;

void SP_Structure_Menu_Parametrage(void);
extern type_Bouton ListeBouton_Menu_Parametrage[4];

int main(void) {
    SP_Initialisation_SDL();
    SP_Initialisation_Textures();
    SP_Structure_Menu_Parametrage();

    int continuer = 1;
    while (continuer) {
        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_EVENT_QUIT) continuer = 0;
            if (e.type == SDL_EVENT_KEY_DOWN && e.key.key == SDLK_ESCAPE) continuer = 0;
        }
        SP_Nettoyer_Ecran(NOIR);
        for (int i = 0; i < 4; i++) SP_Dessiner_Bouton(ListeBouton_Menu_Parametrage[i]);
        Mise_A_jour_Fenetre();
        SDL_Delay(16);
    }
    SP_Quitter_SDL();
    return 0;
}
