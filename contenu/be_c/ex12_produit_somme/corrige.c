#include <stdio.h>
#include <stdlib.h>

/* Exercice 10 du BE : realisation d'une procedure avec passage par valeur.
   Faire une procedure realisant l'affichage de la somme et du produit de 2 nombres. */

/* nom : somme_produit
   semantique : calcul de la somme et du produit de 2 nombres
   parametres :
   a : IN reel, nombre 1
   b : IN reel, nombre 2
   pre-condition : a et b initialises
   post-condition : somme et produit affiches
   Tests : a=3, b=2, solutions produit = 6, somme = 5 */
void somme_produit(int a, int b)
{
    int somme, produit;

    somme = a + b;
    produit = a * b;

    printf("La somme de a+b = %d\n", somme);
    printf("La produit de a*b = %d\n", produit);
}

/* programme principal
   Tests : a=3, b=2, solutions produit = 6, somme = 5 */
int main(void)
{
    int val_a = 3;
    int val_b = 2;

    somme_produit(val_a, val_b);

    return 0;
}
