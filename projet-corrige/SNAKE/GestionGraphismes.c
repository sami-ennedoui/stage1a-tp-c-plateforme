
#include <SDL3/SDL.h>
#include <SDL3_image/SDL_image.h>
#include <SDL3_ttf/SDL_ttf.h>

#include "ConfigurationJeu.h"
#include "VariablesGlobales.h"
#include "InitialisationJeu.h"

#include "Bibliotheque_header/OutilsZoneTexte.h"
#include "Bibliotheque_header/OutilsDessin.h"
#include "Bibliotheque_header/OutilsBouton.h"
#include "Bibliotheque_header/OutilsBoiteSaisie.h"
#include "Bibliotheque_header/OutilsCouleur.h"

#include "GestionMenuParametrage.h"
#include "GestionJeu.h"
#include "GestionGraphismes.h"


//////////////////////////////////////////////////////////////////////////////////
// Gestion des DESSINS
//////////////////////////////////////////////////////////////////////////////////



void SP_Dessiner_Menu_Acceuil() {


    // Dessin des textures

    SP_Dessiner_Texture(TEXTURE_FOND_ACCEUIL,0,0,FENETRE_LARGEUR,FENETRE_HAUTEUR);

    // Dessin des boutons

    SP_Dessiner_Bouton(ListeBouton_Menu_Acceuil[0]) ;
    SP_Dessiner_Bouton(ListeBouton_Menu_Acceuil[1]) ;
    SP_Dessiner_Bouton(ListeBouton_Menu_Acceuil[2]) ;

    // Dessin des zones de texte

    SP_Dessiner_Zone_Texte(texteAccueil,"Bienvenu dans le SNAKE",BLANC) ;


}


/* =========================================================================
   Dessin de l'ecran de jeu (etat MENU_JEU)
   =========================================================================
   On porte ici la fonction dessiner() de linux-build/SNAKE/jeu_demo.c.

   Bug connu : SP_Dessiner_Cercle_Texture a sa ligne SDL_SetRenderDrawColor
   commentee et dessine donc avec la couleur courante du renderer, en ignorant
   son argument. On appelle SDL_SetRenderDrawColor nous-memes avant chaque
   cercle pour forcer la bonne couleur.
   =========================================================================*/

/* Couleurs de rendu du jeu (meme palette que jeu_demo.c). */
static const SDL_Color JEU_FOND  = {30,  30,  40,  255};
static const SDL_Color JEU_STADE = {40,  90,  50,  255};
static const SDL_Color JEU_BORD  = {90,  140, 90,  255};
static const SDL_Color JEU_CORPS = {70,  200, 90,  255};
static const SDL_Color JEU_TETE  = {180, 240, 120, 255};
static const SDL_Color JEU_POMME = {220, 60,  60,  255};

/* Fixe la couleur du renderer puis dessine un cercle plein.
   Compense le bug de SP_Dessiner_Cercle_Texture dont la ligne de couleur
   est commentee dans OutilsDessin.c. */
static void cercle_colore(float x, float y, float r, SDL_Color c) {
    SDL_SetRenderDrawColor(renderer, c.r, c.g, c.b, 255);
    SP_Dessiner_Cercle_Texture(x, y, r, c);
}

/* Calcule le centre en pixels d'une cellule de grille (cx, cy).
   La marge centre le stade horizontalement et verticalement dans la fenetre. */
static void centre_cellule(int cx, int cy, float* px, float* py) {
    int marge = (int)((FENETRE_LARGEUR - STADE_LARGEUR) / 2);
    *px = (float)(marge + cx * TAILLE_CELLULE + TAILLE_CELLULE / 2);
    *py = (float)(marge + cy * TAILLE_CELLULE + TAILLE_CELLULE / 2);
}

/* Dessine le stade, le serpent et la pomme a partir des variables globales. */
void SP_Dessiner_Jeu(void) {

    int marge = (int)((FENETRE_LARGEUR - STADE_LARGEUR) / 2);

    /* Fond general */
    SP_Nettoyer_Ecran(JEU_FOND);

    /* Bord du stade */
    SDL_FRect rect_bord = {
        (float)(marge - 6),
        (float)(marge - 6),
        (float)(STADE_LARGEUR + 12),
        (float)(STADE_HAUTEUR + 12)
    };
    SDL_SetRenderDrawColor(renderer, JEU_BORD.r, JEU_BORD.g, JEU_BORD.b, 255);
    SDL_RenderFillRect(renderer, &rect_bord);

    /* Fond du stade */
    SDL_FRect rect_stade = {
        (float)marge,
        (float)marge,
        (float)STADE_LARGEUR,
        (float)STADE_HAUTEUR
    };
    SDL_SetRenderDrawColor(renderer, JEU_STADE.r, JEU_STADE.g, JEU_STADE.b, 255);
    SDL_RenderFillRect(renderer, &rect_stade);

    /* Pomme */
    float px, py;
    centre_cellule((int)pomme.x, (int)pomme.y, &px, &py);
    cercle_colore(px, py, TAILLE_CELLULE * 0.40f, JEU_POMME);

    /* Corps (de la queue vers la tete pour que la tete recouvre le corps) */
    for (int i = serpent.taille - 1; i >= 1; i--) {
        float bx, by;
        centre_cellule((int)serpent.corps[i].x, (int)serpent.corps[i].y, &bx, &by);
        cercle_colore(bx, by, TAILLE_CELLULE * 0.45f, JEU_CORPS);
    }

    /* Tete */
    float hx, hy;
    centre_cellule((int)serpent.corps[0].x, (int)serpent.corps[0].y, &hx, &hy);
    cercle_colore(hx, hy, TAILLE_CELLULE * 0.48f, JEU_TETE);
}


void SP_Gestion_Graphismes (int etatMenu)
{

    if ( etatMenu == MENU_ACCEUIL )
        SP_Dessiner_Menu_Acceuil();
    else if ( etatMenu == MENU_JEU )
        SP_Dessiner_Jeu();
    //else if (etatMenu == MENU_PARAMETRAGE )
    //    SP_Dessiner_Menu_Parametrage() ;

}
