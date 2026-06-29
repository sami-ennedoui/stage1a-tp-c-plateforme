# Bibliothèque de Dessin [OutilsDessin.h] <!-- omit in toc -->

Cette bibliothèque fournit des fonctions pour manipuler des textures :

- créer des textures à partir d'une image ou d'une figure géométrique
- dessiner ces textures dans le rendu graphique
- d'autres fonctionnionalités graphiques utiles

## Table des Matières <!-- omit in toc -->

- [`SP_Creation_Texture_Rectangle`](#sp_creation_texture_rectangle)
- [`SP_Creation_Cercle_Dans_Texture_Carre`](#sp_creation_cercle_dans_texture_carre)
- [`SP_Creation_Texture_Depuis_Image`](#sp_creation_texture_depuis_image)
- [`SP_Dessiner_Texture`](#sp_dessiner_texture)
- [`SP_Copier_Texture_Dans_Texture`](#sp_copier_texture_dans_texture)
- [`SP_Test_Couleur_Egal`](#sp_test_couleur_egal)
- [`SP_Nettoyer_Ecran`](#sp_nettoyer_ecran)
- [`SP_Nettoyer_Texture`](#sp_nettoyer_texture)
  
## Fonctions <!-- omit in toc -->

### `SP_Creation_Texture_Rectangle`

**Objectif :**
Créer et renvoie une texture rectangle avec une taille spécifiée `[largeur_texture,hauteur_texture]` et une couleur de fond `[couleur_fond]`.

**Prototype :**

```c
SDL_Texture* SP_Creation_Texture( float largeur_texture, float hauteur_texture, SDL_Color couleur_fond)

```

**Arguments :**

| Champ          | Type               | Description                                      |
|----------------|--------------------|--------------------------------------------------|
| `largeur_texture`            | `float`            | Largeur de la texture                  |
| `hauteur_texture`            | `float`            | Hauteur de la texture                  |
| `couleur_fond`              | `float`               | Couleur de fond de la texture                 |

| Retour       | Type           | Description                                         |
|--------------|----------------|-----------------------------------------------------|
| `Pointeur sur une texture`       | `SDL_Texture*` | Pointeur vers la texture créée, ou `NULL` en cas d'erreur |


### `SP_Creation_Cercle_Dans_Texture_Carre`

**Objectif :**
Création d'un cercle plein de couleur `[couleur]` et de rayon `[radius]` dans une texture carrée de taille `[tailleCarre]`.
Le centre du cercle est placé au centre de la texture carrée. Ne dessine pas le cercle.

**Prototype :**

```c
SDL_Texture* SP_Creation_Cercle_Dans_Texture_Carre(float radius, int tailleCarre , SDL_Color couleur);

```

**Arguments :**

| Champ          | Type               | Description                                      |
|----------------|--------------------|--------------------------------------------------|
| `radius`            | `float`            | Rayon du cercle                                            |
| `tailleCarre`            | `float`            | Taille de la texture carrée                  |
| `couleur`            | `SDL_Color`            | Couleur choisie pour le remplissage du cercle                  |

***

| Retour       | Type           | Description                                         |
|--------------|----------------|-----------------------------------------------------|
| `Pointeur sur une texture`       | `SDL_Texture*` | Pointeur vers la texture créée, ou `NULL` en cas d'erreur |


### `SP_Creation_Texture_Depuis_Image`

**Objectif :**

Créé et Renvoie une texture de taille `[largeur_texture,hauteur_texture]` contenant une image PNG spécifiée.

**Prototype :**

```c
SDL_Texture* SP_Creation_Texture_Depuis_Image (char* nom_fichier_image, int largeur_texture,int hauteur_texture) ;

```

**Arguments :**

| Champ                        | Type               | Description                                       |
|------------------------------|--------------------|---------------------------------------------------|
| `nom_fichier_image`          | `char *`           | Nom du fichier Source de l'image                  |
| `largeur_texture`            | `float`            | Largeur de la texture                             |
| `hauteur_texture`            | `float`            | Hauteur de la texture                             |

***

| Retour       | Type           | Description                                         |
|--------------|----------------|-----------------------------------------------------|
| `Pointeur sur une texture`       | `SDL_Texture*` | Pointeur vers la texture créée, ou `NULL` en cas d'erreur |


### `SP_Dessiner_Texture`

**Objectif :**
Dessine une texture dans le renderer à une position `[x,y]` spécifiée (coin HAUT-GAUCHE) et avec une taille spécifiée `[largeur_texture,hauteur_texture]`.

**Prototype :**

```c
void SP_Dessiner_Texture(SDL_Texture* texture, float x, float y, float largeur_texture, float hauteur_texture);

```

**Arguments :**

| Champ          | Type               | Description                                      |
|----------------|--------------------|--------------------------------------------------|
| `texture`       | `SDL_Texture*`  | Texture à dessiner                      |
| `x`             | `float*`     | Coordonnée x de la position du coin HAUT-GAUCHE du rectangle dans lequel la texture est incluse                |
| `y`           | `float`        | Coordonnée x de la position du coin HAUT-GAUCHE du rectangle dans lequel la texture est incluse
| `largeur_texture`            | `float`            | Largeur de la texture                  |
| `hauteur_texture`            | `float`            | Hauteur de la texture                  |


### `SP_Copier_Texture_Dans_Texture`

**Objectif :**
Permet de copier une texture source `[texture_source]` dans une texture cible `[texture_cible]`  

**Prototype :**

```c
void SP_Copier_Texture_Dans_Texture ( float x , float y , SDL_Texture* texture_cible , SDL_Texture* texture_source );

```

**Arguments :**

| Champ          | Type               | Description                                      |
|----------------|--------------------|--------------------------------------------------|
| `x`            | `float`            | Coordonnée x du coin HAUT-GAUCHE ou l'on souhaite copier la source dans la cible            |
| `y`            | `float`            | Coordonnée y du coin HAUT-GAUCHE ou l'on souhaite copier la source dans la cible            |
| `texture_cible`            | `SDL_Texture*`            | Texture cible pour la copie                  |
| `texture_source`            | `SDL_Texture*`            | Texture source pour la copie                  |

### `SP_Test_Couleur_Egal`

**Objectif :**
Permet de comparer 2 SDL_Color entre elles. Renvoi 0 si les couleur sont différentes et 1 si elles sont identiques.

**Prototype :**

```c
int SP_Test_Couleur_Egal(SDL_Color c1, SDL_Color c2) ; 

```

**Arguments :**

| Champ          | Type               | Description                                      |
|----------------|--------------------|--------------------------------------------------|
| `largeur_texture`            | `SDL_Color`            | Couleur 1                  |
| `hauteur_texture`            | `SDL_Color`            | Couleur 2                  |

| Retour       | Type           | Description                                         |
|--------------|----------------|-----------------------------------------------------|
| `Résultat comparaison`       | `int` | 0 si les couleur sont différentes et 1 si elles sont identiques. |

### `SP_Nettoyer_Ecran`

**Objectif :**
Vide complètement le renderer en appliquant une couleur de fond choisie `[couleur]`

**Prototype :**

```c
void SP_Nettoyer_Ecran (SDL_Color couleur);

```

**Arguments :**

| Champ          | Type               | Description                                      |
|----------------|--------------------|--------------------------------------------------|
| `couleur`            | `SDL_Color`            | Couleur choisie pour le fond                  |

### `SP_Nettoyer_Texture`

**Objectif :**
Vide complètement une texture en appliquant une couleur de fond choisie `[couleur]`

**Prototype :**

```c
void SP_Nettoyer_Texture (SDL_Texture* texture , SDL_Color couleur);

```

**Arguments :**

| Champ          | Type               | Description                                      |
|----------------|--------------------|--------------------------------------------------|
| `texture`            | `SDL_Texture*`            | Texture à effacer                   |
| `couleur`            | `SDL_Color`            | Couleur choisie pour le fond de la texture                  |
