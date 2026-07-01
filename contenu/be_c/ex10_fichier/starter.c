#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Exercice 13 du BE : ecriture d'un tableau dans un fichier en mode texte. */

int main(void)
{
    int tab[4] = {3, 12, 7, 25};
    char nom_fichier[10];

    printf(" Donner le nom de votre fichier ( avec extension ) :  \t");
    scanf("%s", nom_fichier);

    /* A toi de faire :
       - ouvrir le fichier nom_fichier en ecriture avec fopen(..., "w"),
       - ecrire chaque case de tab avec fprintf dans une boucle for,
       - fermer le fichier avec fclose,
       - afficher la confirmation exacte : Fichier resultats.txt ecrit. */

    return 0;
}
