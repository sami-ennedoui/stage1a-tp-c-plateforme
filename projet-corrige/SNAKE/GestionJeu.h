#ifndef GESTIONJEU_H_INCLUDED
#define GESTIONJEU_H_INCLUDED

#include <SDL3/SDL.h>

/*
 * Surveille le clavier et renvoie la direction correspondant a la touche
 * flechee enfoncee, ou -1 si aucune touche directionnelle n'est detectee.
 */
int SP_Gestion_Clavier(SDL_Event event);

/*
 * Effectue un pas de jeu :
 *   - decale le corps (chaque segment prend la place du precedent cote tete) ;
 *   - avance la tete selon la direction courante ;
 *   - detecte la collision avec un mur ou avec le corps propre, marque
 *     partie_terminee = 1 et renvoie 0 dans ce cas ;
 *   - si la tete atteint la pomme : agrandit le serpent, incremente le score
 *     et pose une nouvelle pomme hors du corps ;
 *   - renvoie 1 si le serpent est toujours vivant.
 *
 * Cette fonction n'effectue aucun rendu graphique, ce qui la rend testable
 * sans ecran.
 */
int SP_Avancer_Serpent(void);

/* Mise a jour du jeu (boucle principale -- a remplir lors du cablage). */
void Update_Jeu(void);

#endif // GESTIONJEU_H_INCLUDED
