#ifndef INITIALISATIONJEU_H_INCLUDED
#define INITIALISATIONJEU_H_INCLUDED

/* Longueur de depart du serpent. Volontairement courte pour que la partie soit
   jouable, voir le commentaire de SP_Initialisation_Partie. */
#define LONGUEUR_DEPART 4

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
 * - serpent au centre de la grille, LONGUEUR_DEPART segments, tete a droite
 *   (corps[0] = tete) et corps qui s'etend vers la gauche ;
 * - score remis a zero, partie_terminee remis a 0 ;
 * - premiere pomme posee hors du corps.
 */
void SP_Initialisation_Partie(void);

#endif // INITIALISATIONJEU_H_INCLUDED
