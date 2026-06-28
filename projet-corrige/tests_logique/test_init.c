/*
 * test_init.c -- verifie l'etat apres SP_Initialisation_Partie.
 *
 * Criteres :
 *   - serpent.taille == TAILLE_INITIALE
 *   - la tete (corps[0]) est sur la ligne centrale (y == NOMBRE_CELLULE_HAUTEUR/2)
 *     et a l'extremite droite attendue (x == NOMBRE_CELLULE_LARGEUR - 1)
 *   - le corps forme une ligne horizontale valide
 *   - pomme dans les bornes de la grille et hors du corps
 *
 * Aucune fenetre SDL n'est creee, le test tourne sans ecran.
 */

#include <stdio.h>
#include <stdlib.h>

#include "ConfigurationJeu.h"
#include "MesTypes.h"
#include "VariablesGlobales.h"
#include "InitialisationJeu.h"

/* Compteur d'erreurs -- le main renvoie 0 seulement si tout passe. */
static int erreurs = 0;

#define VERIFIER(cond, msg) do { \
    if (!(cond)) { \
        printf("  ECHEC : %s\n", msg); \
        erreurs++; \
    } \
} while(0)

int main(void) {

    printf("=== test_init ===\n");

    /* Graine fixe pour la reproductibilite de la pomme. */
    srand(42);
    SP_Initialisation_Partie();

    /* Taille initiale. */
    VERIFIER(serpent.taille == TAILLE_INITIALE,
             "serpent.taille != TAILLE_INITIALE apres initialisation");

    /* Direction initiale. */
    VERIFIER(serpent.dir == RIGHT,
             "serpent.dir != RIGHT apres initialisation");

    /* Position de la tete (corps[0]). */
    VERIFIER((int)serpent.corps[0].x == NOMBRE_CELLULE_LARGEUR - 1,
             "tete.x incorrect (attendu NOMBRE_CELLULE_LARGEUR - 1)");
    VERIFIER((int)serpent.corps[0].y == NOMBRE_CELLULE_HAUTEUR / 2,
             "tete.y incorrect (attendu NOMBRE_CELLULE_HAUTEUR / 2)");

    /* Integrite du corps : ligne horizontale continue. */
    for (int i = 1; i < serpent.taille; i++) {
        if ((int)serpent.corps[i].x != (int)serpent.corps[i-1].x - 1 ||
            (int)serpent.corps[i].y != NOMBRE_CELLULE_HAUTEUR / 2) {
            printf("  ECHEC : corps[%d] mal place (x=%d y=%d attendu x=%d y=%d)\n",
                   i,
                   (int)serpent.corps[i].x, (int)serpent.corps[i].y,
                   (int)serpent.corps[i-1].x - 1, NOMBRE_CELLULE_HAUTEUR / 2);
            erreurs++;
        }
    }

    /* Pomme dans les bornes de la grille. */
    VERIFIER((int)pomme.x >= 0 && (int)pomme.x < NOMBRE_CELLULE_LARGEUR,
             "pomme.x hors bornes");
    VERIFIER((int)pomme.y >= 0 && (int)pomme.y < NOMBRE_CELLULE_HAUTEUR,
             "pomme.y hors bornes");

    /* Pomme hors du corps. */
    VERIFIER(!sur_le_corps((int)pomme.x, (int)pomme.y, 0),
             "la pomme initiale est sur le corps du serpent");

    /* Bilan. */
    if (erreurs == 0) {
        printf("test_init : PASS\n");
        return 0;
    } else {
        printf("test_init : FAIL (%d erreur(s))\n", erreurs);
        return 1;
    }
}
