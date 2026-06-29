#ifndef MENUPARAMETRAGE_H_INCLUDED
#define MENUPARAMETRAGE_H_INCLUDED

/* Menu Parametrage (4 boutons). */
void SP_Structure_Menu_Parametrage(void);
void SP_Gestion_Evenements_Menu_Parametrage(SDL_Event, int*);

/* Menu choix de couleur serpent (4 couleurs + retour). */
void SP_Structure_Menu_Couleur_Snake(void);
void SP_Gestion_Evenements_Menu_Couleur_Snake(SDL_Event, int*);

/* Menu choix de couleur fond du stade (4 couleurs + retour). */
void SP_Structure_Menu_Couleur_Stade(void);
void SP_Gestion_Evenements_Menu_Couleur_Stade(SDL_Event, int*);

/* Menu choix de couleur bord (4 couleurs + retour). */
void SP_Structure_Menu_Couleur_Bord(void);
void SP_Gestion_Evenements_Menu_Couleur_Bord(SDL_Event, int*);

#endif // MENUPARAMETRAGE_H_INCLUDED
