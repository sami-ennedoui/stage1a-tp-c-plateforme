#ifndef MESTYPES_H_INCLUDED
#define MESTYPES_H_INCLUDED


#include <SDL3_ttf/SDL_ttf.h>
#include "ConfigurationJeu.h"

enum {
    MENU_ACCEUIL,
    MENU_PARAMETRAGE,
    MENU_COULEUR_SNAKE,
    MENU_COULEUR_STADE,
    MENU_COULEUR_BORD,
    MENU_JEU,
    QUITTER_MENU

} ;

enum {

    JEU_OFF,
    JEU_INITIALISATION,
    JEU_NOM_JOUEUR,
    JEU_PRET,
    JEU_EN_COURS,
    JEU_TERMINE,


} ;

typedef enum {UP, DOWN, LEFT, RIGHT} Direction;

typedef struct {

    float x;
    float y;

} type_point;

/*
 * type_serpent : structure principale du jeu.
 * La tete est corps[0], la queue est corps[taille-1].
 * Le tableau est dimensionne au maximum possible (toute la grille).
 */
typedef struct {

    type_point corps[NOMBRE_CELLULE_LARGEUR * NOMBRE_CELLULE_HAUTEUR];
    int        taille;
    Direction  dir;

} type_serpent;

typedef struct {

 SDL_Texture* motifFond ;
 SDL_Texture* motifBord ;
 SDL_Texture* dessinStade ;

} type_stade ;



#endif // MESTYPES_H_INCLUDED
