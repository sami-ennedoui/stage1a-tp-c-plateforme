#ifndef BOITESAISIETEXTE_H_INCLUDED
#define BOITESAISIETEXTE_H_INCLUDED

//void Dessiner_Boite_Saisie(Boite_Saisie *, SDL_Renderer *, TTF_Font *) ;
void Dessiner_Boite_Saisie(type_BoiteSaisie) ;
void Evenement_Boite_Saisie(type_BoiteSaisie *, SDL_Event);
void Initialiser_boite_Saisie(type_BoiteSaisie* , float x, float y, float w, float h, char* , int );
void SP_Reinitialiser_boite_Saisie(type_BoiteSaisie* );

#endif // BOITESAISIETEXTE_H_INCLUDED
