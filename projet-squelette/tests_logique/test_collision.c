/*
 * test_collision.c -- verifie la detection des deux types de collision.
 *
 * Cas 1 -- collision avec un mur :
 *   On monte a la main un serpent court colle au bord droit, tete a
 *   l'extremite (x = NOMBRE_CELLULE_LARGEUR - 1), direction RIGHT. Un pas
 *   suffit pour que la tete sorte de la grille.
 *   SP_Avancer_Serpent doit renvoyer 0 et poser partie_terminee = 1.
 *
 * Cas 2 -- collision avec le corps propre :
 *   On construit manuellement un serpent en forme de U ferme :
 *     corps[0] = (5,5)  tete
 *     corps[1] = (5,6)
 *     corps[2] = (4,6)
 *     corps[3] = (4,5)
 *     direction = DOWN
 *   Apres le pas, la tete avance en (5,6), qui correspond a corps[2]
 *   apres decalage -> collision.
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

    printf("=== test_collision ===\n");

    /* ----- Cas 1 : collision avec le mur de droite ----- */
    printf("  Cas 1 : mur de droite\n");

    /* Serpent court colle au bord droit, tete a l'extremite, direction RIGHT.
       Le pas suivant fait sortir la tete de la grille. On monte cet etat a la
       main pour ne pas dependre du placement initial. */
    serpent.taille     = 3;
    serpent.dir        = RIGHT;
    serpent.corps[0].x = (float)(NOMBRE_CELLULE_LARGEUR - 1);  serpent.corps[0].y = 10.0f;
    serpent.corps[1].x = (float)(NOMBRE_CELLULE_LARGEUR - 2);  serpent.corps[1].y = 10.0f;
    serpent.corps[2].x = (float)(NOMBRE_CELLULE_LARGEUR - 3);  serpent.corps[2].y = 10.0f;
    partie_terminee    = 0;
    pomme.x = 0.0f;  pomme.y = 0.0f;   /* pomme loin, sans effet sur le test */

    int ret = SP_Avancer_Serpent();
    VERIFIER(ret == 0,
             "SP_Avancer_Serpent aurait du renvoyer 0 (sortie de grille)");
    VERIFIER(partie_terminee == 1,
             "partie_terminee aurait du etre 1 apres collision avec le mur");

    /* ----- Cas 2 : collision avec le corps propre ----- */
    printf("  Cas 2 : collision avec soi-meme\n");

    /*
     * Serpent en U ferme, direction DOWN :
     *
     *   col:  4   5
     *  lig 5: [3] [0]  <- tete en (5,5), corps[3] en (4,5)
     *  lig 6: [2] [1]
     *
     * Apres decalage et avancement :
     *   corps[1] <- ancienne tete (5,5)
     *   corps[2] <- ancien corps[1] = (5,6)
     *   corps[3] <- ancien corps[2] = (4,6)
     *   nouvelle tete : (5, 6)
     *   sur_le_corps(5, 6, 1) trouve corps[2] = (5,6) -> collision.
     */
    serpent.taille     = 4;
    serpent.dir        = DOWN;
    serpent.corps[0].x = 5.0f;  serpent.corps[0].y = 5.0f;
    serpent.corps[1].x = 5.0f;  serpent.corps[1].y = 6.0f;
    serpent.corps[2].x = 4.0f;  serpent.corps[2].y = 6.0f;
    serpent.corps[3].x = 4.0f;  serpent.corps[3].y = 5.0f;
    partie_terminee    = 0;
    /* On pose une pomme loin pour ne pas perturber le test. */
    pomme.x = 0.0f;
    pomme.y = 0.0f;

    ret = SP_Avancer_Serpent();
    VERIFIER(ret == 0,
             "SP_Avancer_Serpent aurait du renvoyer 0 (collision avec soi-meme)");
    VERIFIER(partie_terminee == 1,
             "partie_terminee aurait du etre 1 apres collision avec le corps");

    if (erreurs == 0) {
        printf("test_collision : PASS\n");
        return 0;
    } else {
        printf("test_collision : FAIL (%d erreur(s))\n", erreurs);
        return 1;
    }
}
