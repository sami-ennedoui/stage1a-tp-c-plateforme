
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



void SP_Gestion_Graphismes (int etatMenu)
{

    if ( etatMenu == MENU_ACCEUIL )
        SP_Dessiner_Menu_Acceuil();
    //else if (etaMenu == MENU_PARAMETRAGE )
    //    SP_Dessiner_Menu_Parametrage() ;

}
