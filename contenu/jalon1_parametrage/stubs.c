/* Bouchons des fonctions Outils, pour lier le test sans la vraie bibliothèque
   ni le graphisme. La logique clic vers état ne dépend pas de l'affichage. */
#include <SDL3/SDL.h>
#include "MesTypes.h"
#include "Bibliotheque_header/TypeBouton.h"

static int g_boutonClique = -1;

void simuler_clic(int bouton) { g_boutonClique = bouton; }

int SP_Surveillance_Bouton(SDL_Event e, type_Bouton* liste, int n) {
    (void)e; (void)liste; (void)n;
    return g_boutonClique;
}

void SP_Creation_Bouton(type_Bouton* b, char* p, float a, float x, float y,
                        float h, float w, char* t, SDL_Color c1, SDL_Color c2) {
    (void)b;(void)p;(void)a;(void)x;(void)y;(void)h;(void)w;(void)t;(void)c1;(void)c2;
}

/* Constantes couleur, normalement dans la bibliothèque Outils. */
SDL_Color ROUGE, VERT, NOIR, BLANC, BLEU_CLAIR, VERT_CLAIR, ORANGE;
