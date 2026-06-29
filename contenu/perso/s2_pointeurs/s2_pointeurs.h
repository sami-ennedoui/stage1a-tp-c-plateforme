#ifndef S2_POINTEURS_H
#define S2_POINTEURS_H
#include <stdio.h>

/* Permute circulairement les trois entiers dont on reçoit les adresses :
   val_a prend la valeur de val_c, val_c celle de val_b, val_b l'ancienne valeur de val_a. */
void permuter_valeur(int* val_a, int* val_b, int* val_c);
#endif
