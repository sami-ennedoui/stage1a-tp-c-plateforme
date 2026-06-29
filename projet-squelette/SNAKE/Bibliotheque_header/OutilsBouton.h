#ifndef BOUTONCLICK_H_INCLUDED
#define BOUTONCLICK_H_INCLUDED

int checkButtonClick(SDL_FRect , int , int );
void SP_Dessiner_Bouton(type_Bouton);
int SP_Surveillance_Bouton(SDL_Event, type_Bouton*,int);

void SP_Creation_Bouton (type_Bouton*, char* ,float ,float ,float ,float ,float ,char* ,SDL_Color ,SDL_Color ) ;
 void SP_Creation_Bouton_Texture(type_Bouton*,float, float,float, float,SDL_Texture *) ;
#endif // BOUTONCLICK_H_INCLUDED
