#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Exercice 13 du BE : ecriture d'un tableau dans un fichier en mode texte. */

int main(void)
{
    int tab[4] = {3, 12, 7, 25};
    int i;
    FILE* p_fichier;        /* pointeur sur un fichier */
    char nom_fichier[10];   /* chaine pour recueillir le nom du fichier */

    printf(" Donner le nom de votre fichier ( avec extension ) :  \t");
    scanf("%s", nom_fichier);

    /* Ouverture du fichier en ecriture, avec le nom saisi. Chemin relatif,
       le fichier est cree dans le dossier courant. */
    p_fichier = fopen(nom_fichier, "w");
    if (p_fichier == NULL) {
        printf("Erreur: impossible d'ouvrir le fichier.\n");
        return 1;
    }

    /* Ecriture de chaque case du tableau dans le fichier. */
    for (i = 0; i < 4; i++) {
        fprintf(p_fichier, " tab[%d] = %d \n", i, tab[i]);
    }

    fclose(p_fichier);

    /* Confirmation a l'ecran : c'est le seul texte que la porte peut lire. */
    printf("Fichier %s ecrit.\n", nom_fichier);

    return 0;
}
