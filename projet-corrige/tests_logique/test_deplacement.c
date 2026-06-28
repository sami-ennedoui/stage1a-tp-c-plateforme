/*
 * test_deplacement.c -- verifie qu'un pas deplace correctement le serpent.
 *
 * Apres SP_Initialisation_Partie (tete au centre, direction RIGHT) :
 *   - on change la direction a DOWN, puis on lit la position reelle de la tete
 *     pour calculer l'attendu, donc le test ne depend pas du placement exact ;
 *   - on enregistre toutes les positions avant le pas ;
 *   - on appelle SP_Avancer_Serpent ;
 *   - on verifie que la tete a avance d'une cellule vers le bas et que
 *     chaque segment a pris la place de son predecesseur.
 *
 * Aucune fenetre SDL n'est creee, le test tourne sans ecran.
 */

#include <stdio.h>
#include <stdlib.h>

#include "ConfigurationJeu.h"
#include "MesTypes.h"
#include "VariablesGlobales.h"
#include "InitialisationJeu.h"
#include "GestionJeu.h"

static int erreurs = 0;

#define VERIFIER(cond, msg) do { \
    if (!(cond)) { \
        printf("  ECHEC : %s\n", msg); \
        erreurs++; \
    } \
} while(0)

int main(void) {

    printf("=== test_deplacement ===\n");

    srand(42);
    SP_Initialisation_Partie();

    /* On choisit DOWN : la tete descend d'une cellule, sans collision possible. */
    serpent.dir = DOWN;

    /* Sauvegarde des positions avant le deplacement. */
    int taille_avant = serpent.taille;
    type_point anciens[NOMBRE_CELLULE_LARGEUR * NOMBRE_CELLULE_HAUTEUR];
    for (int i = 0; i < taille_avant; i++)
        anciens[i] = serpent.corps[i];

    float hx_attendu = anciens[0].x;
    float hy_attendu = anciens[0].y + 1.0f;   /* DOWN = y + 1 */

    int ret = SP_Avancer_Serpent();

    /* Le serpent ne doit pas mourir sur ce deplacement. */
    VERIFIER(ret == 1, "SP_Avancer_Serpent a renvoye 0 (collision inattendue)");
    VERIFIER(partie_terminee == 0, "partie_terminee != 0 apres deplacement valide");

    /* La taille ne change pas (pas de pomme mangee). */
    VERIFIER(serpent.taille == taille_avant,
             "serpent.taille a change sans manger de pomme");

    /* La tete a avance d'une cellule dans la bonne direction. */
    VERIFIER((int)serpent.corps[0].x == (int)hx_attendu,
             "tete.x incorrect apres deplacement DOWN");
    VERIFIER((int)serpent.corps[0].y == (int)hy_attendu,
             "tete.y incorrect apres deplacement DOWN");

    /* Chaque segment a pris la place de son predecesseur. */
    for (int i = 1; i < taille_avant; i++) {
        if ((int)serpent.corps[i].x != (int)anciens[i-1].x ||
            (int)serpent.corps[i].y != (int)anciens[i-1].y) {
            printf("  ECHEC : corps[%d] vaut (%d,%d), attendu (%d,%d)\n",
                   i,
                   (int)serpent.corps[i].x, (int)serpent.corps[i].y,
                   (int)anciens[i-1].x,     (int)anciens[i-1].y);
            erreurs++;
        }
    }

    if (erreurs == 0) {
        printf("test_deplacement : PASS\n");
        return 0;
    } else {
        printf("test_deplacement : FAIL (%d erreur(s))\n", erreurs);
        return 1;
    }
}
