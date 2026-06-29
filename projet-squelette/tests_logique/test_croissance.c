/*
 * test_croissance.c -- verifie que le serpent grandit quand il mange une pomme.
 *
 * Apres SP_Initialisation_Partie :
 *   - on oriente le serpent vers le bas (DOWN) ;
 *   - on place la pomme juste devant la tete, lue dynamiquement ;
 *   - on appelle SP_Avancer_Serpent ;
 *   - on verifie que taille a augmente d'un, que score a augmente d'un,
 *     et que la nouvelle pomme est dans les bornes et hors du corps.
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

    printf("=== test_croissance ===\n");

    srand(42);
    SP_Initialisation_Partie();

    /* Direction DOWN : la tete descendra d'une cellule au prochain pas. */
    serpent.dir = DOWN;

    int taille_avant = serpent.taille;
    int score_avant  = score;

    /* Pomme posee exactement devant la tete, position lue dynamiquement. */
    pomme.x = serpent.corps[0].x;
    pomme.y = serpent.corps[0].y + 1.0f;

    int ret = SP_Avancer_Serpent();

    /* Le pas doit reussir. */
    VERIFIER(ret == 1, "SP_Avancer_Serpent a renvoye 0 (collision inattendue)");

    /* La taille doit avoir augmente d'un. */
    VERIFIER(serpent.taille == taille_avant + 1,
             "serpent.taille n'a pas augmente apres absorption de la pomme");

    /* Le score doit avoir augmente d'un. */
    VERIFIER(score == score_avant + 1,
             "score n'a pas augmente apres absorption de la pomme");

    /* La nouvelle pomme doit etre dans les bornes de la grille. */
    VERIFIER((int)pomme.x >= 0 && (int)pomme.x < NOMBRE_CELLULE_LARGEUR,
             "nouvelle pomme.x hors bornes");
    VERIFIER((int)pomme.y >= 0 && (int)pomme.y < NOMBRE_CELLULE_HAUTEUR,
             "nouvelle pomme.y hors bornes");

    /* La nouvelle pomme doit etre hors du corps (maintenant plus long). */
    VERIFIER(!sur_le_corps((int)pomme.x, (int)pomme.y, 0),
             "la nouvelle pomme est sur le corps du serpent");

    if (erreurs == 0) {
        printf("test_croissance : PASS\n");
        return 0;
    } else {
        printf("test_croissance : FAIL (%d erreur(s))\n", erreurs);
        return 1;
    }
}
