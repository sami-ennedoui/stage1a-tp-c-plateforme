
//==================================================================================
//==================================================================================
// Exemple de Programme utilisant la librairie SDL3
// Ne pas hésiter à utiliser ChatGPT pour des exemples de Code
// Attention car les exemples sont souvent donnés avec SDL2 qui est obsolète
// Les adaptations necessaires sont parfois guidés par le compilateur donc
// bien regarger les messages de compilation
//==================================================================================
//==================================================================================

//==================================================================================
//==================================================================================
// Inclusion des bibliothèques
//==================================================================================
//==================================================================================

// Inclusion des bibliothèques C

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

// Inclusion des bibliothèques SDL3

#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>
#include <SDL3_image/SDL_image.h>
#include <SDL3_ttf/SDL_ttf.h>

// Inclusion fichiers de déclarations de variables et de types

#include "ConfigurationJeu.h"
#include "MesTypes.h"
#include "VariablesGlobales.h"

// Inclusion des bibliothèques d'outils

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

    int etatMenu    = MENU_ACCEUIL      ;

    //==================================================================================
    // Appel à l'initialisation du jeu
    // ==> a appeler obligatoirement au début d'un code utilisant la SDL3
    // Contient également des instructions pour charges des images de son choix
    // Voir dans "InitialisationJeu.c"
    //==================================================================================

    SP_Initialisation_SDL() ;
    SP_Initialisation_Textures();
    SP_Structure_Menu_Acceuil();

    while (etatMenu != QUITTER_MENU)
    {

    SDL_Event e;

        while ( SP_surveillance_Evenement(&e) !=0  )
        {

                if ( etatMenu == MENU_ACCEUIL ) SP_Gestion_Evenements_MENU_ACCUEIL(e,&etatMenu) ;

        }

        SP_Nettoyer_Ecran(NOIR) ;

        SP_Gestion_Graphismes(etatMenu);

        Mise_A_jour_Fenetre() ;

        SDL_Delay(16); // ~60 FPS
    }

    SP_Quitter_SDL();

    return 0;
}
