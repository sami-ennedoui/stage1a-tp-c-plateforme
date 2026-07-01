#include <stdio.h>
#include <stdlib.h>

/* À toi d'écrire le menu de l'exercice 3.
   - Déclare trois float a = 1.5, b = 0.5 et c = 0.6.
   - Dans une boucle do while, affiche le menu et lis le choix avec scanf.
   - Un switch case : selon le choix (1, 2 ou 3), lis une nouvelle valeur
     pour a, b ou c. Le cas default affiche un message d'erreur.
   - Après chaque modification, affiche les nouvelles valeurs.
   - Demande si l'utilisateur veut modifier une autre variable et répète
     tant qu'il répond oui. À la fin, affiche « Fin du programme. ». */

int main(void)
{
    float a = 1.5, b = 0.5, c = 0.6;

    printf("Les valeurs des variables sont :\n");
    printf("a = %.1f - b = %.1f - c = %.1f\n", a, b, c);

    return 0;
}
