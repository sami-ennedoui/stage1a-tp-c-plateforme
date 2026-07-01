#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*============================================*/
/* Exercice 6 ==> Les tableaux (suite)        */
/*============================================*/

int main(void)
{
    char chaine[6] = "Salut";

    printf("  La chaine contient = %s \n", chaine);
    printf("  Le tableau est stocke a l'adresse = %p \n", (void*)chaine);

    printf("  Veuillez entrer une nouvelle chaine de caracteres \n");
    scanf("%s", chaine); /* et pas &chaine : chaine est un tableau, son nom est deja une adresse */
    printf("  La nouvelle chaine contient = %s \n", chaine);

    /* Si on entre une chaine de plus de 5 caracteres, scanf ecrit quand meme
       au dela du tableau, dans une zone memoire non reservee. DANGER. */

    return 0;
}
