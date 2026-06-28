#ifndef INITIALISATIONJEU_H_INCLUDED
#define INITIALISATIONJEU_H_INCLUDED

/*
 * Renvoie 1 si la case (cx, cy) de la grille est occupee par le corps du
 * serpent a partir de l'index depuis (inclus), 0 sinon.
 * Utiliser depuis=0 pour tester toute la longueur, depuis=1 pour ignorer
 * la tete (utile apres deplacement).
 */
int sur_le_corps(int cx, int cy, int depuis);

/*
 * Place la pomme a une position aleatoire dans la grille, hors du corps
 * du serpent dans son etat courant.
 */
void SP_Nouvelle_Pomme(void);

/*
 * Initialise une nouvelle partie :
 * - serpent horizontal au centre de la grille, TAILLE_INITIALE segments,
 *   tete a droite (corps[0] = tete) ;
 * - score remis a zero, partie_terminee remis a 0 ;
 * - premiere pomme posee hors du corps.
 */
void SP_Initialisation_Partie(void);

#endif // INITIALISATIONJEU_H_INCLUDED
