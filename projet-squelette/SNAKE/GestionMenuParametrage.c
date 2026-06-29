#include <SDL3/SDL.h>
#include <SDL3_ttf/SDL_ttf.h>
#include <stdio.h>

#include "MesTypes.h"
#include "VariablesGlobales.h"
#include "ConfigurationJeu.h"
#include "Bibliotheque_header/OutilsDessin.h"
#include "Bibliotheque_header/OutilsZoneTexte.h"
#include "Bibliotheque_header/OutilsBouton.h"
#include "Bibliotheque_header/OutilsCouleur.h"

#include "GestionJeu.h"
#include "InitialisationJeu.h"

/* Quatre couleurs proposees dans chaque menu couleur.
   La meme palette sert pour le serpent, le stade et le bord. */
static const SDL_Color CHOIX_VERT   = {70,  200, 90,  255} ;
static const SDL_Color CHOIX_BLEU   = {50,  100, 200, 255} ;
static const SDL_Color CHOIX_ROUGE  = {200, 50,  50,  255} ;
static const SDL_Color CHOIX_ORANGE = {220, 130, 30,  255} ;

//////////////////////////////////////////////////////////////////////////////////
// Menu PARAMETRAGE
//////////////////////////////////////////////////////////////////////////////////

void SP_Structure_Menu_Parametrage(void) {
    SP_Creation_Bouton(ListeBouton_Menu_Parametrage,
        "arial_bold", 20, 0, TAILLE_CELLULE,   6*TAILLE_CELLULE, TAILLE_CELLULE,
        "COULEUR SERPENT", BLEU_CLAIR, ROUGE);
    SP_Creation_Bouton(ListeBouton_Menu_Parametrage+1,
        "arial_bold", 20, 0, 2*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "COULEUR FOND", BLEU_CLAIR, ROUGE);
    SP_Creation_Bouton(ListeBouton_Menu_Parametrage+2,
        "arial_bold", 20, 0, 3*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "COULEUR BORD", BLEU_CLAIR, ROUGE);
    SP_Creation_Bouton(ListeBouton_Menu_Parametrage+3,
        "arial_bold", 20, 0, 4*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "RETOUR", BLEU_CLAIR, ROUGE);
}

void SP_Gestion_Evenements_Menu_Parametrage(SDL_Event e, int* p_etatMenu) {
    int flag = SP_Surveillance_Bouton(e, ListeBouton_Menu_Parametrage, 4);
    if      (flag == 0) { printf("Couleur serpent\n"); *p_etatMenu = MENU_COULEUR_SNAKE; }
    else if (flag == 1) { printf("Couleur fond\n");    *p_etatMenu = MENU_COULEUR_STADE; }
    else if (flag == 2) { printf("Couleur bord\n");    *p_etatMenu = MENU_COULEUR_BORD;  }
    else if (flag == 3) { printf("Retour accueil\n");  *p_etatMenu = MENU_ACCEUIL;       }
}

//////////////////////////////////////////////////////////////////////////////////
// Menu COULEUR SERPENT
//////////////////////////////////////////////////////////////////////////////////

void SP_Structure_Menu_Couleur_Snake(void) {
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Snake,
        "arial_bold", 20, 0, 1*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "VERT",   BLANC, CHOIX_VERT);
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Snake+1,
        "arial_bold", 20, 0, 2*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "BLEU",   BLANC, CHOIX_BLEU);
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Snake+2,
        "arial_bold", 20, 0, 3*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "ROUGE",  BLANC, CHOIX_ROUGE);
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Snake+3,
        "arial_bold", 20, 0, 4*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "ORANGE", BLANC, CHOIX_ORANGE);
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Snake+4,
        "arial_bold", 20, 0, 5*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "RETOUR", BLEU_CLAIR, ROUGE);
}

void SP_Gestion_Evenements_Menu_Couleur_Snake(SDL_Event e, int* p_etatMenu) {
    int flag = SP_Surveillance_Bouton(e, ListeBouton_Menu_Couleur_Snake, 5);
    if (flag == 0) { couleur_serpent = CHOIX_VERT;   printf("Serpent vert\n");   *p_etatMenu = MENU_PARAMETRAGE; }
    else if (flag == 1) { couleur_serpent = CHOIX_BLEU;   printf("Serpent bleu\n");   *p_etatMenu = MENU_PARAMETRAGE; }
    else if (flag == 2) { couleur_serpent = CHOIX_ROUGE;  printf("Serpent rouge\n");  *p_etatMenu = MENU_PARAMETRAGE; }
    else if (flag == 3) { couleur_serpent = CHOIX_ORANGE; printf("Serpent orange\n"); *p_etatMenu = MENU_PARAMETRAGE; }
    else if (flag == 4) { *p_etatMenu = MENU_PARAMETRAGE; }
}

//////////////////////////////////////////////////////////////////////////////////
// Menu COULEUR FOND (stade)
//////////////////////////////////////////////////////////////////////////////////

void SP_Structure_Menu_Couleur_Stade(void) {
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Stade,
        "arial_bold", 20, 0, 1*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "VERT",   BLANC, CHOIX_VERT);
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Stade+1,
        "arial_bold", 20, 0, 2*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "BLEU",   BLANC, CHOIX_BLEU);
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Stade+2,
        "arial_bold", 20, 0, 3*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "ROUGE",  BLANC, CHOIX_ROUGE);
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Stade+3,
        "arial_bold", 20, 0, 4*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "ORANGE", BLANC, CHOIX_ORANGE);
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Stade+4,
        "arial_bold", 20, 0, 5*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "RETOUR", BLEU_CLAIR, ROUGE);
}

void SP_Gestion_Evenements_Menu_Couleur_Stade(SDL_Event e, int* p_etatMenu) {
    int flag = SP_Surveillance_Bouton(e, ListeBouton_Menu_Couleur_Stade, 5);
    if      (flag == 0) { couleur_stade = CHOIX_VERT;   printf("Fond vert\n");   *p_etatMenu = MENU_PARAMETRAGE; }
    else if (flag == 1) { couleur_stade = CHOIX_BLEU;   printf("Fond bleu\n");   *p_etatMenu = MENU_PARAMETRAGE; }
    else if (flag == 2) { couleur_stade = CHOIX_ROUGE;  printf("Fond rouge\n");  *p_etatMenu = MENU_PARAMETRAGE; }
    else if (flag == 3) { couleur_stade = CHOIX_ORANGE; printf("Fond orange\n"); *p_etatMenu = MENU_PARAMETRAGE; }
    else if (flag == 4) { *p_etatMenu = MENU_PARAMETRAGE; }
}

//////////////////////////////////////////////////////////////////////////////////
// Menu COULEUR BORD
//////////////////////////////////////////////////////////////////////////////////

void SP_Structure_Menu_Couleur_Bord(void) {
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Bord,
        "arial_bold", 20, 0, 1*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "VERT",   BLANC, CHOIX_VERT);
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Bord+1,
        "arial_bold", 20, 0, 2*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "BLEU",   BLANC, CHOIX_BLEU);
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Bord+2,
        "arial_bold", 20, 0, 3*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "ROUGE",  BLANC, CHOIX_ROUGE);
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Bord+3,
        "arial_bold", 20, 0, 4*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "ORANGE", BLANC, CHOIX_ORANGE);
    SP_Creation_Bouton(ListeBouton_Menu_Couleur_Bord+4,
        "arial_bold", 20, 0, 5*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "RETOUR", BLEU_CLAIR, ROUGE);
}

void SP_Gestion_Evenements_Menu_Couleur_Bord(SDL_Event e, int* p_etatMenu) {
    int flag = SP_Surveillance_Bouton(e, ListeBouton_Menu_Couleur_Bord, 5);
    if      (flag == 0) { couleur_bord = CHOIX_VERT;   printf("Bord vert\n");   *p_etatMenu = MENU_PARAMETRAGE; }
    else if (flag == 1) { couleur_bord = CHOIX_BLEU;   printf("Bord bleu\n");   *p_etatMenu = MENU_PARAMETRAGE; }
    else if (flag == 2) { couleur_bord = CHOIX_ROUGE;  printf("Bord rouge\n");  *p_etatMenu = MENU_PARAMETRAGE; }
    else if (flag == 3) { couleur_bord = CHOIX_ORANGE; printf("Bord orange\n"); *p_etatMenu = MENU_PARAMETRAGE; }
    else if (flag == 4) { *p_etatMenu = MENU_PARAMETRAGE; }
}
