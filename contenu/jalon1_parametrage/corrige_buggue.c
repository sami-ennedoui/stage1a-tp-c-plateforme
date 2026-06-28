/* Jalon 1, version buggée pour juger les tests de l'étudiant. NE PAS montrer.
   Bug : les clics 0 et 1 mènent au mauvais état, échangés. */
#include <SDL3/SDL.h>
#include <stdio.h>

#include "MesTypes.h"
#include "ConfigurationJeu.h"
#include "Bibliotheque_header/TypeBouton.h"
#include "Bibliotheque_header/OutilsBouton.h"
#include "Bibliotheque_header/OutilsCouleur.h"

type_Bouton ListeBouton_Menu_Parametrage[4];

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

void SP_Gestion_Evenements_MENU_PARAMETRAGE(SDL_Event e, int* p_etatMenu) {
    int flag = SP_Surveillance_Bouton(e, ListeBouton_Menu_Parametrage, 4);
    if (flag == 0)      *p_etatMenu = MENU_COULEUR_STADE;  /* BUG, devrait être SNAKE */
    else if (flag == 1) *p_etatMenu = MENU_COULEUR_SNAKE;  /* BUG, devrait être STADE */
    else if (flag == 2) *p_etatMenu = MENU_COULEUR_BORD;
    else if (flag == 3) *p_etatMenu = MENU_ACCEUIL;
}
