
#define INPUT_MAX 256

typedef struct
{
    char text[INPUT_MAX];
    int length;
    int cursor;
    int x,y,w,h;
    int blink;
} InputBox;

InputBox box = { "",0,0,100,100,300,40,0 };

void InputBox_HandleEvent(InputBox *box, SDL_Event *event)
{
    if(event->type == SDL_TEXTINPUT)
    {
        const char *t = event->text.text;

        while(*t && box->length < INPUT_MAX-1)
        {
            for(int i=box->length;i>=box->cursor;i--)
                box->text[i+1] = box->text[i];

            box->text[box->cursor] = *t;

            box->cursor++;
            box->length++;
            t++;
        }
    }

    if(event->type == SDL_KEYDOWN)
    {
        SDL_Keycode key = event->key.keysym.sym;

        if(key == SDLK_BACKSPACE && box->cursor>0)
        {
            for(int i=box->cursor-1;i<box->length;i++)
                box->text[i] = box->text[i+1];

            box->cursor--;
            box->length--;
        }

        if(key == SDLK_DELETE && box->cursor < box->length)
        {
            for(int i=box->cursor;i<box->length;i++)
                box->text[i] = box->text[i+1];

            box->length--;
        }

        if(key == SDLK_LEFT && box->cursor>0)
            box->cursor--;

        if(key == SDLK_RIGHT && box->cursor < box->length)
            box->cursor++;
    }
}


void InputBox_Draw(InputBox *box, SDL_Renderer *renderer, TTF_Font *font)
{
    SDL_Rect rect = {box->x,box->y,box->w,box->h};

    SDL_SetRenderDrawColor(renderer,40,40,40,255);
    SDL_RenderFillRect(renderer,&rect);

    SDL_SetRenderDrawColor(renderer,255,255,255,255);
    SDL_RenderDrawRect(renderer,&rect);

    SDL_Color color = {255,255,255};

    SDL_Surface *surf = TTF_RenderText_Blended(font,box->text,color);
    SDL_Texture *tex = SDL_CreateTextureFromSurface(renderer,surf);

    SDL_Rect textRect = {box->x+5, box->y+5, surf->w, surf->h};

    SDL_RenderCopy(renderer,tex,NULL,&textRect);

    SDL_FreeSurface(surf);
    SDL_DestroyTexture(tex);
}
// Cursor clih=gnottant

if((SDL_GetTicks()/500)%2==0)
{
    char temp[INPUT_MAX];
    strncpy(temp,box->text,box->cursor);
    temp[box->cursor]='\0';

    SDL_Surface *surf = TTF_RenderText_Blended(font,temp,(SDL_Color){255,255,255});
    int cursorX = box->x + 5 + surf->w;

    SDL_FreeSurface(surf);

    SDL_SetRenderDrawColor(renderer,255,255,255,255);
    SDL_RenderDrawLine(renderer,cursorX,box->y+5,cursorX,box->y+box->h-5);
}

// Boucle principale

SDL_StartTextInput();

while(running)
{
    SDL_Event event;

    while(SDL_PollEvent(&event))
    {
        InputBox_HandleEvent(&box,&event);
    }

    SDL_RenderClear(renderer);

    InputBox_Draw(&box,renderer,font);

    SDL_RenderPresent(renderer);
}

SDL_StopTextInput();
