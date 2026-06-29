/* Test de référence solide. Sert au --selftest de la plateforme. NE PAS montrer.
   Il épingle chaque clic à son état, donc il attrape le bug des clics échangés. */
#include <stdio.h>
#include "harnais.h"

static int echecs = 0;

static void verifier(int bouton, int attendu, const char* libelle) {
    simuler_clic(bouton);
    int etat = 12345;            /* sentinelle, doit changer si le clic est valide */
    SDL_Event e = {0};
    SP_Gestion_Evenements_MENU_PARAMETRAGE(e, &etat);
    int ok = (etat == attendu);
    printf("  %s clic=%2d -> etat=%d attendu=%d : %s\n",
           ok ? "OK  " : "FAIL", bouton, etat, attendu, libelle);
    if (!ok) echecs++;
}

int main(void) {
    verifier(0, MENU_COULEUR_SNAKE, "couleur serpent");
    verifier(1, MENU_COULEUR_STADE, "couleur fond");
    verifier(2, MENU_COULEUR_BORD,  "couleur bord");
    verifier(3, MENU_ACCEUIL,       "retour accueil");
    verifier(-1, 12345,             "clic hors bouton, etat inchange");
    printf(echecs == 0 ? "TOUT PASSE\n" : "%d ECHEC(S)\n", echecs);
    return echecs;
}
