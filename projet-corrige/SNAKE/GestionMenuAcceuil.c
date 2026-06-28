#include <SDL3/SDL.h>
#include <SDL3_ttf/SDL_ttf.h>
#include <SDL3_image/SDL_image.h>
#include <stdio.h>

#include "ConfigurationJeu.h"
#include "VariablesGlobales.h"
#include "MesTypes.h"

#include "Bibliotheque_header/OutilsDessin.h"
#include "Bibliotheque_header/OutilsZoneTexte.h"
#include "Bibliotheque_header/OutilsBouton.h"
#include "Bibliotheque_header/OutilsCouleur.h"

#include "GestionJeu.h"
#include "InitialisationJeu.h"

//////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////
// Gestion des EVENEMENTS
//////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////

void SP_Gestion_Evenements_MENU_ACCUEIL ( SDL_Event e , int* p_etatMenu ){

// Menu ACCEUIL ==> PARAMETRAGE / JEU / QUITTER

int flag = SP_Surveillance_Bouton(e, ListeBouton_Menu_Acceuil, 3);

if (flag == 0)  {

    printf("Tu viens d'appuyer sur Parametres \n") ;
    //*p_etatMenu = MENU_PARAMETRAGE ;

}

else if (flag == 1) {

    printf("Tu viens d'appuyer sur Jouer \n") ;
    //*p_etatMenu = MENU_JEU ;
}

else if (flag == 2) {

    printf ("Tu viens d'appuyer sur Quitter \n");
    // *p_etatMenu = QUITTER_MENU ;

}


}


//////////////////////////////////////////////////////////////////////////////////
// CREATION des BOUTONS et des ZONES TEXTE
//////////////////////////////////////////////////////////////////////////////////


void SP_Structure_Menu_Acceuil() {

// Création des boutons

SP_Creation_Bouton(ListeBouton_Menu_Acceuil,"arial_bold",20,0,TAILLE_CELLULE,4*TAILLE_CELLULE,TAILLE_CELLULE,"PARAMETRES",BLEU_CLAIR,ROUGE);
SP_Creation_Bouton(ListeBouton_Menu_Acceuil+1,"arial_bold",20,0,2*TAILLE_CELLULE,4*TAILLE_CELLULE,TAILLE_CELLULE,"JOUER",BLEU_CLAIR,ROUGE);
SP_Creation_Bouton(ListeBouton_Menu_Acceuil+2,"arial_bold",20,0,3*TAILLE_CELLULE,4*TAILLE_CELLULE,TAILLE_CELLULE,"QUITTER",BLEU_CLAIR,ROUGE);

// Création des zones de texte

SP_Creation_Zone_Texte(&texteAccueil,"arial_bold",20,0,0) ;

}


