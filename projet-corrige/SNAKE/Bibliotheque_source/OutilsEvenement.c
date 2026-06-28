#include <SDL3/SDL.h>



int SP_surveillance_Evenement(SDL_Event* e) {

int flag_Evenement ;

flag_Evenement = SDL_PollEvent(e)  ;

return(flag_Evenement) ;

}

