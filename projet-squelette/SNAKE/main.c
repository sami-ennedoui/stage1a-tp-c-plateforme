
//==================================================================================
//==================================================================================
// Exemple de Programme utilisant la librairie SDL3
//==================================================================================
//==================================================================================

// Inclusion des bibliotheques C

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

// Inclusion des bibliotheques SDL3

#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>
#include <SDL3_image/SDL_image.h>
#include <SDL3_ttf/SDL_ttf.h>

// Inclusion fichiers de declarations de variables et de types

#include "ConfigurationJeu.h"
#include "MesTypes.h"
#include "VariablesGlobales.h"

// Inclusion des bibliotheques d'outils

#include "Bibliotheque_header/Initialisation_SDL.h"
#include "Bibliotheque_header/OutilsDessin.h"
#include "Bibliotheque_header/OutilsEvenement.h"
#include "Bibliotheque_header/OutilsCouleur.h"

// Inclusion des sous-programmes personnels

#include "InitialisationJeu.h"
#include "GestionMenuAcceuil.h"
#include "GestionMenuParametrage.h"
#include "GestionJeu.h"
#include "GestionGraphismes.h"
#include "InitialisationTexture.h"

//==================================================================================
//==================================================================================
// Programme Principal
//==================================================================================
//==================================================================================

int main(int argc, char *argv[]) {

    int etatMenu = MENU_ACCEUIL ;

    /* Vaut 1 quand SP_Initialisation_Partie a deja ete appelee pour la
       partie en cours, 0 sinon. Evite l'appel a chaque frame. */
    int jeu_demarre = 0 ;

    /* Compteur de frames pour la cadence de jeu.
       Un pas de serpent se produit tous les CADENCE_JEU images (~133 ms a 60 FPS). */
    int compteur_frames = 0 ;
    const int CADENCE_JEU = 8 ;

    //==================================================================================
    // Appel a l'initialisation du jeu
    // ==> a appeler obligatoirement au debut d'un code utilisant la SDL3
    // Voir dans "InitialisationJeu.c"
    //==================================================================================

    SP_Initialisation_SDL() ;
    SP_Initialisation_Textures();
    SP_Structure_Menu_Acceuil();
    SP_Structure_Menu_Parametrage();
    SP_Structure_Menu_Couleur_Snake();
    SP_Structure_Menu_Couleur_Stade();
    SP_Structure_Menu_Couleur_Bord();

    while (etatMenu != QUITTER_MENU)
    {

        SDL_Event e;

        /* --- Entree dans le jeu : une seule initialisation par partie --- */
        if ( etatMenu == MENU_JEU && !jeu_demarre ) {
            SP_Initialisation_Partie() ;
            jeu_demarre     = 1 ;
            compteur_frames = 0 ;
        }

        /* --- Traitement des evenements --- */
        while ( SP_surveillance_Evenement(&e) != 0 )
        {
            if ( etatMenu == MENU_ACCEUIL )
                SP_Gestion_Evenements_MENU_ACCUEIL(e, &etatMenu) ;

            else if ( etatMenu == MENU_PARAMETRAGE )
                SP_Gestion_Evenements_Menu_Parametrage(e, &etatMenu) ;

            else if ( etatMenu == MENU_COULEUR_SNAKE )
                SP_Gestion_Evenements_Menu_Couleur_Snake(e, &etatMenu) ;

            else if ( etatMenu == MENU_COULEUR_STADE )
                SP_Gestion_Evenements_Menu_Couleur_Stade(e, &etatMenu) ;

            else if ( etatMenu == MENU_COULEUR_BORD )
                SP_Gestion_Evenements_Menu_Couleur_Bord(e, &etatMenu) ;

            /* Clavier en cours de partie : direction + anti demi-tour */
            else if ( etatMenu == MENU_JEU && e.type == SDL_EVENT_KEY_DOWN ) {
                int d = SP_Gestion_Clavier(e) ;
                if (d != -1) {
                    /* Interdit le demi-tour direct (regle du Snake). */
                    int demi = ( serpent.dir == LEFT  && d == RIGHT )
                             ||( serpent.dir == RIGHT && d == LEFT  )
                             ||( serpent.dir == UP    && d == DOWN  )
                             ||( serpent.dir == DOWN  && d == UP   ) ;
                    if (!demi) serpent.dir = (Direction)d ;
                }
            }
        }

        /* --- Cadence de jeu : un pas du serpent tous les CADENCE_JEU images --- */
        if ( etatMenu == MENU_JEU && !partie_terminee ) {
            compteur_frames++ ;
            if ( compteur_frames >= CADENCE_JEU ) {
                SP_Avancer_Serpent() ;
                compteur_frames = 0 ;
            }
        }

        /* --- Rendu de la frame courante --- */
        SP_Nettoyer_Ecran(NOIR) ;
        SP_Gestion_Graphismes(etatMenu);
        Mise_A_jour_Fenetre() ;

        /* --- Fin de partie : bref affichage du dernier etat, puis retour Accueil --- */
        if ( etatMenu == MENU_JEU && partie_terminee ) {
            SDL_Delay(1500) ;
            etatMenu    = MENU_ACCEUIL ;
            jeu_demarre = 0 ;
        }

        SDL_Delay(16); /* ~60 FPS */
    }

    SP_Quitter_SDL();

    return 0;
}
