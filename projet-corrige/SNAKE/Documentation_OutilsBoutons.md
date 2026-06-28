# Bibliothèque ZoneTexte - [OutilsBoutons.h] <!-- omit in toc -->

Cette bibliothèque permet de créer, dessiner et mettre à jour des zones de texte en utilisant SDL3 et SDL3_ttf.

## Table des matières <!-- omit in toc -->

- [Types](#types)
  - [`type_bouton`](#type_bouton)
- [Fonctions](#fonctions)
  - [`SP_Creation_Bouton`](#sp_creation_bouton)
  - [`SP_Dessiner_Bouton`](#sp_dessiner_bouton)
  - [`SP_Surveillance_Bouton`](#sp_surveillance_bouton)

## Types 

### `type_bouton`

Structure contenant les paramètrer d'un bouton graphique pour des actions souris

| Champ          | Type               | Description                                      |
|----------------|--------------------|--------------------------------------------------|
| `rect`       | `SDL_FRect`    | Rectangle contenant le bouton                      |
| `label`    | `char*`     | Texte associé au bouton                |
| `textColor` | `SDL_Color`            | Couleur du texte associé au bouton                             |
| `backGroundColor`            | `float`            | Couleur de fond associée au bouton                  |
| `textSurface`            | `SDL_Surface*`     | Surface nécessaire au placement du texte                   |
| `textTexture`            | `SDL_Texture*`            | Texture nécessaire au placement du texte                  |
| `textRect`            | `SDL_FRect`            |  Rectangle contenant le text du bouton                   |

## Fonctions

### `SP_Creation_Bouton`

**Objectif** : Création d'un bouton d'action pour souris. 

**Prototype :**

```c

void SP_Creation_Bouton (type_Bouton *button, char* nomPolice,float taillePolice,float x,float y,float h,float w,char* text,SDL_Color textColor,SDL_Color backGroundColor)

```

**Arguments :**

| Champ          | Type               | Description                                      |
|----------------|--------------------|--------------------------------------------------|
| `button`       | `type_Bouton *`    | Bouton a créer                      |
| `nomPolice`    | `SDL_Surface*`     | Surface contenant le texte rendu.                |
| `taillePolice` | `float`            | Taille de la police.                             |
| `x`            | `float`            | Position X de la zone de texte.                  |
| `y`            | `float`            | Position Y de la zone de texte.                  |

### `SP_Dessiner_Bouton`

**Objectif** : Dessine un bouton dans le renderer 

**Prototype :**

```c

void SP_Dessiner_Bouton(type_Bouton button) ; 

```

**Arguments :**

| Champ          | Type               | Description                                         |
|----------------|--------------------|--------------------------------------------------   |
| `button`    | `type_Bouton`         | bouton à dessiner dans le renderer                         |

### `SP_Surveillance_Bouton`

**Objectif** : Détermine quel bouton a été cliqué par l'utilisateur dans une liste de bouton disponible sur le renderer actuel 
Les boutons sont dans une liste [0..nbbouton-1]

**Prototype :**

```c

int SP_Surveillance_Bouton(SDL_Event* e,type_Bouton* boutonToCheck,int nbBouton);

```

**Arguments :**

| Champ          | Type               | Description                                         |
|----------------|--------------------|--------------------------------------------------   |
| `nbBouton`    | `int`         | nombre de bouton dnas la liste de boutons à surveiller                |
| `boutonToCheck`    | `type_Bouton*`         | Pointeur sur la liste des boutons à surveiller                 |
| `e`    | `SDL_Event`         | Evènement contenant les informations sur les actions réalisées par la souris et la position du pointeur                  |