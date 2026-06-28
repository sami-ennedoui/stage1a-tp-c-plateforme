# Bibliothèque ZoneTexte - Documentation

Cette bibliothèque permet de créer, dessiner et mettre à jour des zones de texte en utilisant SDL3 et SDL3_ttf.

---

## Table des matières
- [Types](#types)
- [Fonctions](#fonctions)
  - [`SP_Creation_Zone_Texte`](#sp_creation_zone_texte)
  - [`SP_Dessiner_Zone_Texte`](#sp_dessiner_zone_texte)
- [Exemple d'utilisation](#exemple-dutilisation)

---

## Types

### `type_ZoneTexte`
Structure représentant une zone de texte.

| Champ          | Type               | Description                                      |
|----------------|--------------------|--------------------------------------------------|
| `font`         | `TTF_Font*`        | Police de caractères utilisée pour le texte.     |
| `textSurface`  | `SDL_Surface*`     | Surface contenant le texte rendu.               |
| `textTexture`  | `SDL_Texture*`     | Texture contenant le texte rendu.               |
| `taillePolice` | `float`            | Taille de la police.                             |
| `x`            | `float`            | Position X de la zone de texte.                  |
| `y`            | `float`            | Position Y de la zone de texte.                  |

---

## Fonctions

---

### `SP_Creation_Zone_Texte`
**Objectif** : Initialiser une zone de texte avec une police, une taille et une position données [x,y] pour le coin HAUT-GAUCHE.

**Prototype :**
```c
void SP_Creation_Zone_Texte(type_ZoneTexte* zoneTexte, char* nomPolice, float taillePolice, float x, float y);

```

**Arguments :**

| Champ          | Type               | Description                                      |
|----------------|--------------------|--------------------------------------------------|
| `zoneTexte`    | `type_ZoneTexte*`  | Zone de texte à positionner                      |
| `nomPolice`    | `SDL_Surface*`     | Surface contenant le texte rendu.                |
| `taillePolice` | `float`            | Taille de la police.                             |
| `x`            | `float`            | Position X de la zone de texte.                  |
| `y`            | `float`            | Position Y de la zone de texte.                  |


### `SP_Dessiner_Zone_Texte`
**Objectif** : Dessiner une zone de texte préalablement créée avec ```SP_Creation_Zone_Text(..)```. Le texte est placé à la position spécifiée lors de la création


**Prototype :**
```c
void SP_Dessiner_Zone_Texte (type_ZoneTexte zoneTexte , char* text , SDL_Color textColor );

```
**Arguments :**

| Champ          | Type               | Description                                         |
|----------------|--------------------|--------------------------------------------------   |
| `zoneTexte`    | `type_ZoneTexte*`  | Zone de texte à positionner                         |
| `text`         | `char * `          | chaine de caractère conyenant le texte à afficher   |
| `textColor`    | `SDL_Color`        | Couleur du texte                                 |


