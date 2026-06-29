#ifndef TYPEBOITESAISIE_H_INCLUDED
#define TYPEBOITESAISIE_H_INCLUDED


typedef struct
{
    char text[265];
    int length;
    int cursorVisible;
    int x,y,w,h;
    int active;
    TTF_Font* font;

} type_BoiteSaisie;


#endif // TYPEBOITESAISIE_H_INCLUDED
