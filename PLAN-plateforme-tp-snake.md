# Plateforme du TP Snake, plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construire une application de bureau PyQt6 où un étudiant travaille le TP Snake en C, avec portes de preuve exécutables, tests fournis puis écrits par l'étudiant, et aide IA débridée par la preuve. La v1 est une tranche verticale, deux étapes, `perso_P1` et `jalon1_parametrage`.

**Architecture:** Le contenu est de la donnée, une étape est un dossier sous `contenu/`. Des modules purs sans UI, `modele_etape`, `executeur`, `progression`, `tuteur_ia`, chacun testable sans écran. Une fenêtre `fenetre.py` les câble. Un point d'entrée `atelier_snake.py` lance l'appli ou les autotests.

**Tech Stack:** Python 3.14, PyQt6 6.11, gcc 15, SDL3 via pkg-config. Tests Python en `unittest` stdlib. Pas de dépendance ajoutée.

## Global Constraints

- Tout vit dans `~/scratch-stage1a/snake-sdl/plateforme/`, hors du vault.
- L'archive d'origine `~/scratch-stage1a/snake-sdl/extracted/SNAKE_STAGE/SNAKE_ARCHIVE_SDL_DEPART/` ne se modifie jamais. Les compilations qui ont besoin du projet utilisent la copie de build `~/scratch-stage1a/snake-sdl/linux-build/SNAKE/`.
- Les dossiers `SDL3`, `SDL3_ttf`, `SDL3_image` ne se modifient pas.
- Le protocole de réussite d'un test C est le code de sortie : 0 si tout passe, non nul sinon. L'exécuteur se fie au code de sortie, pas au texte. Un `printf` de débogage ne casse pas le protocole.
- Langue des libellés, énoncés et messages : français. Style sans tiret cadratin, sans parenthèses fourre-tout, sans emoji.
- Niveaux de débridage : N0 explique seulement, N1 squelette ou analogie, N2 candidat à justifier, N3 libre. Départ N0, une porte passée débloque le cran indiqué par `cran_debloque`. L'étudiant peut descendre sous le cran débloqué, jamais monter au-dessus.
- Pacing du contenu, calé sur le Snake d'origine : test fourni d'abord, l'étudiant écrit les tests à partir des jalons du projet. Ordre des concepts moteur plus tard, MVT puis EVOLUTION puis ALLONGE puis GAME_OVER, voir l'annexe A de la spec.
- Commits fréquents, locaux au dépôt git de `plateforme/` créé en tâche 1. Ce dépôt est distinct du vault, il ne touche pas au vault.

## Structure des fichiers

```
plateforme/
├── chemins.py            constantes de chemins, détection des modules pkg-config
├── modele_etape.py       Etape + chargement du parcours depuis les données
├── executeur.py          recettes de compilation, portes perso et jalon, aperçu
├── progression.py        état persistant, déverrouillage des étapes et crans
├── tuteur_ia.py          prompt par cran, filtre de solution, appel moteur
├── fenetre.py            QMainWindow qui câble tout
├── atelier_snake.py      point d'entrée, --selftest, --smoketest
├── contenu/
│   ├── parcours.json     ordre des étapes
│   ├── perso_P1/         meta.json, enonce.md, p1.h, starter.c, corrige.c, tests.c
│   └── jalon1_parametrage/
│         meta.json, enonce.md, starter.c, corrige.c, corrige_buggue.c,
│         stubs.c, harnais.h, test_reference.c, apercu.c
└── tests/
    ├── test_modele_etape.py
    ├── test_executeur.py
    ├── test_progression.py
    └── test_tuteur_ia.py
```

Responsabilités, une par fichier. `chemins` ne fait que résoudre des chemins et des drapeaux pkg-config. `modele_etape` ne fait que lire des données. `executeur` ne fait que compiler et exécuter, il ne connaît pas l'UI. `progression` ne fait que l'état. `tuteur_ia` ne fait que le prompt, le filtre et l'appel moteur. `fenetre` ne fait que l'UI. `atelier_snake` ne fait qu'orchestrer.

---

## Task 1: Squelette, dépôt, chemins, modèle d'étape

**Files:**
- Create: `plateforme/chemins.py`
- Create: `plateforme/modele_etape.py`
- Create: `plateforme/contenu/parcours.json`
- Create: `plateforme/tests/test_modele_etape.py`

**Interfaces:**
- Produces: `chemins.RACINE`, `chemins.CONTENU`, `chemins.SNAKE_ROOT`, `chemins.ARCH`, `chemins.BUILD_COPY`, `chemins.SDL_INCLUDES` (list[Path]), `chemins.PROGRESSION_FICHIER`, `chemins.modules_sdl(avec_ttf_image: bool) -> list[str]`, `chemins.cflags_sdl(avec_ttf_image) -> list[str]`, `chemins.libs_sdl(avec_ttf_image) -> list[str]`.
- Produces: `modele_etape.Etape` (dataclass: `id, titre, type, mode, recette, cran_debloque, noeud_cours, fichier_edite, dossier: Path`), `modele_etape.charger_etape(dossier: Path) -> Etape`, `modele_etape.charger_parcours(dossier_contenu: Path = chemins.CONTENU) -> list[Etape]`.

- [ ] **Step 1: Initialiser le dépôt et l'arborescence**

```bash
cd ~/scratch-stage1a/snake-sdl/plateforme
git init
mkdir -p contenu/perso_P1 contenu/jalon1_parametrage tests
printf '__pycache__/\n*.pyc\nprogression.json\n' > .gitignore
```

- [ ] **Step 2: Écrire `chemins.py`**

```python
"""Chemins et drapeaux de compilation. Aucune logique métier ici."""
from pathlib import Path
import subprocess

RACINE = Path(__file__).resolve().parent
CONTENU = RACINE / "contenu"
PROGRESSION_FICHIER = RACINE / "progression.json"

SNAKE_ROOT = Path.home() / "scratch-stage1a" / "snake-sdl" / "extracted" / "SNAKE_STAGE"
ARCH = SNAKE_ROOT / "SNAKE_ARCHIVE_SDL_DEPART"
BUILD_COPY = Path.home() / "scratch-stage1a" / "snake-sdl" / "linux-build" / "SNAKE"

SDL_INCLUDES = [
    SNAKE_ROOT / "SDL3" / "include",
    SNAKE_ROOT / "SDL3_ttf" / "include",
    SNAKE_ROOT / "SDL3_image" / "include",
]


def _module_existe(nom: str) -> bool:
    return subprocess.run(["pkg-config", "--exists", nom]).returncode == 0


def modules_sdl(avec_ttf_image: bool = True) -> list[str]:
    mods = ["sdl3"]
    if avec_ttf_image:
        for c in ("sdl3-ttf", "SDL3_ttf"):
            if _module_existe(c):
                mods.append(c)
                break
        for c in ("sdl3-image", "SDL3_image"):
            if _module_existe(c):
                mods.append(c)
                break
    return mods


def _pkg(champ: str, mods: list[str]) -> list[str]:
    r = subprocess.run(["pkg-config", champ, *mods], capture_output=True, text=True)
    return r.stdout.split()


def cflags_sdl(avec_ttf_image: bool = True) -> list[str]:
    return _pkg("--cflags", modules_sdl(avec_ttf_image))


def libs_sdl(avec_ttf_image: bool = True) -> list[str]:
    return _pkg("--libs", modules_sdl(avec_ttf_image))
```

- [ ] **Step 3: Écrire `contenu/parcours.json`**

```json
{
  "ordre": ["perso_P1", "jalon1_parametrage"]
}
```

- [ ] **Step 4: Écrire le test d'abord, `tests/test_modele_etape.py`**

```python
import unittest
from pathlib import Path
import chemins
from modele_etape import charger_parcours, charger_etape


class TestModeleEtape(unittest.TestCase):
    def test_parcours_dans_l_ordre(self):
        etapes = charger_parcours(chemins.CONTENU)
        self.assertEqual([e.id for e in etapes], ["perso_P1", "jalon1_parametrage"])

    def test_champs_perso(self):
        e = charger_etape(chemins.CONTENU / "perso_P1")
        self.assertEqual(e.type, "perso")
        self.assertEqual(e.mode, "test_fourni")
        self.assertEqual(e.cran_debloque, 1)

    def test_champs_jalon(self):
        e = charger_etape(chemins.CONTENU / "jalon1_parametrage")
        self.assertEqual(e.type, "jalon")
        self.assertEqual(e.mode, "test_a_ecrire")
        self.assertEqual(e.fichier_edite, "GestionMenuParametrage.c")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 5: Lancer le test, vérifier qu'il échoue**

Run: `cd ~/scratch-stage1a/snake-sdl/plateforme && python3 -m unittest tests.test_modele_etape -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'modele_etape'`, et les `meta.json` n'existent pas encore.

- [ ] **Step 6: Écrire `modele_etape.py`**

```python
"""Lecture des étapes du TP depuis les dossiers de données. Aucune compilation ici."""
from dataclasses import dataclass
from pathlib import Path
import json

import chemins


@dataclass
class Etape:
    id: str
    titre: str
    type: str            # "perso" | "jalon"
    mode: str            # "test_fourni" | "test_a_ecrire"
    recette: str         # "perso" | "jalon_test"
    cran_debloque: int
    noeud_cours: str
    fichier_edite: str
    dossier: Path


def charger_etape(dossier: Path) -> Etape:
    meta = json.loads((dossier / "meta.json").read_text(encoding="utf-8"))
    return Etape(
        id=meta["id"],
        titre=meta["titre"],
        type=meta["type"],
        mode=meta["mode"],
        recette=meta["recette"],
        cran_debloque=meta["cran_debloque"],
        noeud_cours=meta["noeud_cours"],
        fichier_edite=meta["fichier_edite"],
        dossier=dossier,
    )


def charger_parcours(dossier_contenu: Path = chemins.CONTENU) -> list[Etape]:
    ordre = json.loads((dossier_contenu / "parcours.json").read_text(encoding="utf-8"))["ordre"]
    return [charger_etape(dossier_contenu / i) for i in ordre]
```

- [ ] **Step 7: Créer les deux `meta.json` (les fichiers de code viennent aux tâches 2 et 3)**

`contenu/perso_P1/meta.json` :

```json
{
  "id": "perso_P1",
  "titre": "P1, le pointeur qui change l'état",
  "type": "perso",
  "mode": "test_fourni",
  "recette": "perso",
  "cran_debloque": 1,
  "noeud_cours": "Passage par pointeur IN/OUT",
  "fichier_edite": "soumission.c"
}
```

`contenu/jalon1_parametrage/meta.json` :

```json
{
  "id": "jalon1_parametrage",
  "titre": "Jalon 1, le menu Paramétrage",
  "type": "jalon",
  "mode": "test_a_ecrire",
  "recette": "jalon_test",
  "cran_debloque": 2,
  "noeud_cours": "Décomposition fonctionnelle, tableau de boutons, état par pointeur",
  "fichier_edite": "GestionMenuParametrage.c"
}
```

- [ ] **Step 8: Lancer le test, vérifier qu'il passe**

Run: `python3 -m unittest tests.test_modele_etape -v`
Expected: PASS, 3 tests.

- [ ] **Step 9: Commit**

```bash
git add -A && git commit -m "modele d'etape et chemins, parcours a deux etapes"
```

---

## Task 2: Contenu de l'étape perso P1, mode test fourni

**Files:**
- Create: `plateforme/contenu/perso_P1/p1.h`
- Create: `plateforme/contenu/perso_P1/starter.c`
- Create: `plateforme/contenu/perso_P1/corrige.c`
- Create: `plateforme/contenu/perso_P1/tests.c`
- Create: `plateforme/contenu/perso_P1/enonce.md`

**Interfaces:**
- Produces: un dossier d'étape `test_fourni` où `corrige.c` plus `tests.c` compilent et sortent avec le code 0, et `starter.c` plus `tests.c` sortent non nul. Consommé par `executeur.porte_perso` en tâche 4.

- [ ] **Step 1: Écrire `p1.h`**

```c
#ifndef P1_H
#define P1_H
#include <stdio.h>

/* Les états du menu, comme l'enum du projet Snake. */
enum { MENU_ACCUEIL, MENU_PARAMETRAGE, MENU_JEU, QUITTER };

void changer_par_valeur(int etat);
void changer_par_pointeur(int* p_etat);
#endif
```

- [ ] **Step 2: Écrire `corrige.c`**

```c
/* P1 corrigé. Implémentation seule, le main et les vérifications sont dans tests.c. */
#include "p1.h"

/* Passage par VALEUR : la fonction reçoit une copie, la modification est perdue. */
void changer_par_valeur(int etat) {
    etat = MENU_PARAMETRAGE;
}

/* Passage par POINTEUR : la fonction reçoit l'adresse, donc *p_etat modifie
   bien la variable de l'appelant. C'est la signature de p_etatMenu du projet. */
void changer_par_pointeur(int* p_etat) {
    *p_etat = MENU_PARAMETRAGE;
}
```

- [ ] **Step 3: Écrire `starter.c`, la version à trou montrée à l'étudiant**

```c
/* P1. Implémente changer_par_pointeur pour que l'état de l'appelant change vraiment. */
#include "p1.h"

void changer_par_valeur(int etat) {
    etat = MENU_PARAMETRAGE;   /* perdu au retour, c'est voulu, pour montrer le contraste */
}

void changer_par_pointeur(int* p_etat) {
    /* À TOI. Tu reçois l'ADRESSE de la variable de l'appelant, pas sa valeur.
       Fais que cette variable devienne MENU_PARAMETRAGE. */
}
```

- [ ] **Step 4: Écrire `tests.c`, la porte de preuve**

```c
#include "p1.h"

int main(void) {
    int etat = MENU_ACCUEIL;

    changer_par_valeur(etat);
    if (etat != MENU_ACCUEIL) {
        printf("FAIL: le passage par valeur a modifie l'appelant\n");
        return 1;
    }

    changer_par_pointeur(&etat);
    if (etat != MENU_PARAMETRAGE) {
        printf("FAIL: le passage par pointeur n'a pas change l'etat, lu %d\n", etat);
        return 1;
    }

    printf("TOUT PASSE\n");
    return 0;
}
```

- [ ] **Step 5: Écrire `enonce.md`**

```markdown
# P1, le pointeur qui change l'état

Dans le projet Snake, un sous-programme doit changer l'état du menu de celui qui
l'appelle. Sa signature ressemble à `SP_Gestion_Evenements_MENU_ACCUEIL(SDL_Event, int*)`.
Le deuxième paramètre est un `int*`, un pointeur. On isole ce mécanisme hors de SDL.

Tu as deux fonctions. `changer_par_valeur` reçoit une copie, elle ne peut rien changer
chez l'appelant, c'est normal. À toi d'écrire `changer_par_pointeur` pour que la variable
de l'appelant devienne `MENU_PARAMETRAGE`.

Indice : tu reçois l'adresse de la variable. Pour atteindre la variable derrière l'adresse,
utilise l'étoile.

La porte : quand `changer_par_pointeur` modifie bien l'appelant et que `changer_par_valeur`
le laisse intact, le test sort en succès.
```

- [ ] **Step 6: Vérifier la porte à la main, corrigé puis starter**

```bash
cd ~/scratch-stage1a/snake-sdl/plateforme/contenu/perso_P1
gcc -Wall corrige.c tests.c -I. -o /tmp/p1c && /tmp/p1c; echo "corrige code=$?"
gcc -Wall starter.c tests.c -I. -o /tmp/p1s && /tmp/p1s; echo "starter code=$?"
```
Expected : corrigé imprime `TOUT PASSE` et `code=0`. Starter imprime un `FAIL` et `code=1`.

- [ ] **Step 7: Commit**

```bash
cd ~/scratch-stage1a/snake-sdl/plateforme
git add -A && git commit -m "contenu P1, pointeur IN/OUT, mode test fourni"
```

---

## Task 3: Contenu du jalon 1, mode test à écrire

**Files:**
- Create: `plateforme/contenu/jalon1_parametrage/corrige.c`
- Create: `plateforme/contenu/jalon1_parametrage/corrige_buggue.c`
- Create: `plateforme/contenu/jalon1_parametrage/starter.c`
- Create: `plateforme/contenu/jalon1_parametrage/stubs.c`
- Create: `plateforme/contenu/jalon1_parametrage/harnais.h`
- Create: `plateforme/contenu/jalon1_parametrage/test_reference.c`
- Create: `plateforme/contenu/jalon1_parametrage/apercu.c`
- Create: `plateforme/contenu/jalon1_parametrage/enonce.md`

**Interfaces:**
- Produces: un dossier d'étape `test_a_ecrire`. `corrige.c` définit `void SP_Structure_Menu_Parametrage(void)`, `void SP_Gestion_Evenements_MENU_PARAMETRAGE(SDL_Event, int*)`, et `type_Bouton ListeBouton_Menu_Parametrage[4]`. `harnais.h` déclare `void simuler_clic(int bouton)` et le prototype de `SP_Gestion_Evenements_MENU_PARAMETRAGE`. Consommé par `executeur.juger_test`, `executeur.porte_jalon`, `executeur.construire_apercu` en tâches 5 et 6.

- [ ] **Step 1: Écrire `corrige.c`, repris du noyau déjà vérifié**

```c
/* Jalon 1 corrigé. Le menu Paramétrage : 4 boutons, et la gestion des clics
   qui change l'état du menu via un pointeur. La liste de boutons est définie ici. */
#include <SDL3/SDL.h>
#include <stdio.h>

#include "MesTypes.h"
#include "ConfigurationJeu.h"
#include "Bibliotheque_header/TypeBouton.h"
#include "Bibliotheque_header/OutilsBouton.h"
#include "Bibliotheque_header/OutilsCouleur.h"

type_Bouton ListeBouton_Menu_Parametrage[4];

void SP_Structure_Menu_Parametrage(void) {
    SP_Creation_Bouton(ListeBouton_Menu_Parametrage,
        "arial_bold", 20, 0, TAILLE_CELLULE,   6*TAILLE_CELLULE, TAILLE_CELLULE,
        "COULEUR SERPENT", BLEU_CLAIR, ROUGE);
    SP_Creation_Bouton(ListeBouton_Menu_Parametrage+1,
        "arial_bold", 20, 0, 2*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "COULEUR FOND", BLEU_CLAIR, ROUGE);
    SP_Creation_Bouton(ListeBouton_Menu_Parametrage+2,
        "arial_bold", 20, 0, 3*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "COULEUR BORD", BLEU_CLAIR, ROUGE);
    SP_Creation_Bouton(ListeBouton_Menu_Parametrage+3,
        "arial_bold", 20, 0, 4*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "RETOUR", BLEU_CLAIR, ROUGE);
}

void SP_Gestion_Evenements_MENU_PARAMETRAGE(SDL_Event e, int* p_etatMenu) {
    int flag = SP_Surveillance_Bouton(e, ListeBouton_Menu_Parametrage, 4);
    if (flag == 0)      *p_etatMenu = MENU_COULEUR_SNAKE;
    else if (flag == 1) *p_etatMenu = MENU_COULEUR_STADE;
    else if (flag == 2) *p_etatMenu = MENU_COULEUR_BORD;
    else if (flag == 3) *p_etatMenu = MENU_ACCEUIL;
}
```

- [ ] **Step 2: Écrire `corrige_buggue.c`, le bug planté du méta-test**

Bug planté : les associations des clics 0 et 1 sont échangées. Un bon test, qui épingle chaque clic à son état attendu, l'attrape. Un test mou, qui vérifie seulement que l'état a changé, le laisse passer.

```c
/* Jalon 1, version buggée pour juger les tests de l'étudiant. NE PAS montrer.
   Bug : les clics 0 et 1 mènent au mauvais état, échangés. */
#include <SDL3/SDL.h>
#include <stdio.h>

#include "MesTypes.h"
#include "ConfigurationJeu.h"
#include "Bibliotheque_header/TypeBouton.h"
#include "Bibliotheque_header/OutilsBouton.h"
#include "Bibliotheque_header/OutilsCouleur.h"

type_Bouton ListeBouton_Menu_Parametrage[4];

void SP_Structure_Menu_Parametrage(void) {
    SP_Creation_Bouton(ListeBouton_Menu_Parametrage,
        "arial_bold", 20, 0, TAILLE_CELLULE,   6*TAILLE_CELLULE, TAILLE_CELLULE,
        "COULEUR SERPENT", BLEU_CLAIR, ROUGE);
    SP_Creation_Bouton(ListeBouton_Menu_Parametrage+1,
        "arial_bold", 20, 0, 2*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "COULEUR FOND", BLEU_CLAIR, ROUGE);
    SP_Creation_Bouton(ListeBouton_Menu_Parametrage+2,
        "arial_bold", 20, 0, 3*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "COULEUR BORD", BLEU_CLAIR, ROUGE);
    SP_Creation_Bouton(ListeBouton_Menu_Parametrage+3,
        "arial_bold", 20, 0, 4*TAILLE_CELLULE, 6*TAILLE_CELLULE, TAILLE_CELLULE,
        "RETOUR", BLEU_CLAIR, ROUGE);
}

void SP_Gestion_Evenements_MENU_PARAMETRAGE(SDL_Event e, int* p_etatMenu) {
    int flag = SP_Surveillance_Bouton(e, ListeBouton_Menu_Parametrage, 4);
    if (flag == 0)      *p_etatMenu = MENU_COULEUR_STADE;  /* BUG, devrait être SNAKE */
    else if (flag == 1) *p_etatMenu = MENU_COULEUR_SNAKE;  /* BUG, devrait être STADE */
    else if (flag == 2) *p_etatMenu = MENU_COULEUR_BORD;
    else if (flag == 3) *p_etatMenu = MENU_ACCEUIL;
}
```

- [ ] **Step 3: Écrire `starter.c`, la version à trou de l'étudiant**

```c
/* Jalon 1. Écris le menu Paramétrage par analogie avec GestionMenuAcceuil.c.
   Quatre boutons à créer, et la gestion des clics qui change l'état du menu. */
#include <SDL3/SDL.h>
#include <stdio.h>

#include "MesTypes.h"
#include "ConfigurationJeu.h"
#include "Bibliotheque_header/TypeBouton.h"
#include "Bibliotheque_header/OutilsBouton.h"
#include "Bibliotheque_header/OutilsCouleur.h"

/* La liste des boutons du menu Paramétrage. */
type_Bouton ListeBouton_Menu_Parametrage[4];

void SP_Structure_Menu_Parametrage(void) {
    /* À TOI. Crée les 4 boutons avec SP_Creation_Bouton, comme dans l'accueil :
       couleur serpent, couleur fond, couleur bord, retour. */
}

void SP_Gestion_Evenements_MENU_PARAMETRAGE(SDL_Event e, int* p_etatMenu) {
    /* À TOI. Récupère le bouton cliqué avec SP_Surveillance_Bouton, puis change
       *p_etatMenu vers le bon état selon le bouton. */
}
```

- [ ] **Step 4: Écrire `harnais.h`, l'infrastructure fournie à l'étudiant pour tester**

```c
#ifndef HARNAIS_JALON1_H
#define HARNAIS_JALON1_H
#include <SDL3/SDL.h>
#include "MesTypes.h"

/* Le sous-programme que tu écris, dans GestionMenuParametrage.c. */
void SP_Gestion_Evenements_MENU_PARAMETRAGE(SDL_Event e, int* p_etatMenu);

/* Fourni par le harnais : fait comme si le bouton donné était sous le clic.
   Passe -1 pour un clic en dehors de tout bouton. */
void simuler_clic(int bouton);
#endif
```

- [ ] **Step 5: Écrire `stubs.c`, les bouchons des outils, pour tester sans graphisme**

```c
/* Bouchons des fonctions Outils, pour lier le test sans la vraie bibliothèque
   ni le graphisme. La logique clic vers état ne dépend pas de l'affichage. */
#include <SDL3/SDL.h>
#include "MesTypes.h"
#include "Bibliotheque_header/TypeBouton.h"

static int g_boutonClique = -1;

void simuler_clic(int bouton) { g_boutonClique = bouton; }

int SP_Surveillance_Bouton(SDL_Event e, type_Bouton* liste, int n) {
    (void)e; (void)liste; (void)n;
    return g_boutonClique;
}

void SP_Creation_Bouton(type_Bouton* b, char* p, float a, float x, float y,
                        float h, float w, char* t, SDL_Color c1, SDL_Color c2) {
    (void)b;(void)p;(void)a;(void)x;(void)y;(void)h;(void)w;(void)t;(void)c1;(void)c2;
}

/* Constantes couleur, normalement dans la bibliothèque Outils. */
SDL_Color ROUGE, VERT, NOIR, BLANC, BLEU_CLAIR, VERT_CLAIR, ORANGE;
```

- [ ] **Step 6: Écrire `test_reference.c`, un test solide pour l'autotest, pas montré**

```c
/* Test de référence solide. Sert au --selftest de la plateforme. NE PAS montrer.
   Il épingle chaque clic à son état, donc il attrape le bug des clics échangés. */
#include <stdio.h>
#include "harnais.h"

static int echecs = 0;

static void verifier(int bouton, int attendu, const char* libelle) {
    simuler_clic(bouton);
    int etat = 12345;            /* sentinelle, doit changer si le clic est valide */
    SDL_Event e;
    SP_Gestion_Evenements_MENU_PARAMETRAGE(e, &etat);
    int ok = (etat == attendu);
    printf("  %s clic=%2d -> etat=%d attendu=%d : %s\n",
           ok ? "OK  " : "FAIL", bouton, etat, attendu, libelle);
    if (!ok) echecs++;
}

int main(void) {
    verifier(0, MENU_COULEUR_SNAKE, "couleur serpent");
    verifier(1, MENU_COULEUR_STADE, "couleur fond");
    verifier(2, MENU_COULEUR_BORD,  "couleur bord");
    verifier(3, MENU_ACCEUIL,       "retour accueil");
    verifier(-1, 12345,             "clic hors bouton, etat inchange");
    printf(echecs == 0 ? "TOUT PASSE\n" : "%d ECHEC(S)\n", echecs);
    return echecs;
}
```

- [ ] **Step 7: Écrire `apercu.c`, la couche visible, qui dessine les boutons de l'étudiant**

Modelé sur `shooter.c` du projet, qui rend déjà un menu. Il ne passe pas par `SP_Gestion_Graphismes`, dont la branche Paramétrage est commentée dans l'archive de départ. Il dessine la liste de l'étudiant directement avec `SP_Dessiner_Bouton`.

```c
/* Aperçu du jalon 1 : ouvre une fenêtre et dessine les boutons que l'étudiant
   a construits dans SP_Structure_Menu_Parametrage. Échap ou la croix pour fermer. */
#include <SDL3/SDL.h>
#include <SDL3_ttf/SDL_ttf.h>
#include <stdio.h>

#include "ConfigurationJeu.h"
#include "MesTypes.h"
#include "VariablesGlobales.h"
#include "Bibliotheque_header/Initialisation_SDL.h"
#include "Bibliotheque_header/OutilsDessin.h"
#include "Bibliotheque_header/OutilsCouleur.h"
#include "Bibliotheque_header/OutilsBouton.h"
#include "Bibliotheque_header/TypeBouton.h"
#include "InitialisationTexture.h"

extern SDL_Renderer* renderer;

void SP_Structure_Menu_Parametrage(void);
extern type_Bouton ListeBouton_Menu_Parametrage[4];

int main(void) {
    SP_Initialisation_SDL();
    SP_Initialisation_Textures();
    SP_Structure_Menu_Parametrage();

    int continuer = 1;
    while (continuer) {
        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_EVENT_QUIT) continuer = 0;
            if (e.type == SDL_EVENT_KEY_DOWN && e.key.key == SDLK_ESCAPE) continuer = 0;
        }
        SP_Nettoyer_Ecran(NOIR);
        for (int i = 0; i < 4; i++) SP_Dessiner_Bouton(ListeBouton_Menu_Parametrage[i]);
        Mise_A_jour_Fenetre();
        SDL_Delay(16);
    }
    SP_Quitter_SDL();
    return 0;
}
```

- [ ] **Step 8: Écrire `enonce.md`**

```markdown
# Jalon 1, le menu Paramétrage

Tu as l'accueil comme exemple, dans `GestionMenuAcceuil.c`. Écris le menu Paramétrage
sur le même modèle. Deux sous-programmes.

`SP_Structure_Menu_Parametrage` crée les quatre boutons dans `ListeBouton_Menu_Parametrage`,
avec `SP_Creation_Bouton` : couleur du serpent, couleur du fond, couleur du bord, retour.

`SP_Gestion_Evenements_MENU_PARAMETRAGE` lit le bouton cliqué avec `SP_Surveillance_Bouton`,
puis change `*p_etatMenu` vers le bon état. Souviens-toi de P1, tu as un pointeur, c'est
l'état de l'appelant que tu changes.

Ici, tu écris aussi ton test. Le harnais te donne `simuler_clic(bouton)` pour faire comme
si un bouton donné était cliqué, et le prototype du sous-programme. Écris des
vérifications dans `test_eleve`, du genre : après `simuler_clic(0)` et un appel, l'état doit
valoir `MENU_COULEUR_SNAKE`.

La plateforme juge d'abord ton test, sans te montrer comment. Un test qui se contente de
vérifier que l'état a changé est trop faible. Quand ton test est jugé solide, il devient
la porte de ton propre code. Le bouton Lancer le jeu ouvre une fenêtre avec tes boutons.
```

- [ ] **Step 9: Vérifier le méta-test à la main, le test de référence attrape le bug**

```bash
cd ~/scratch-stage1a/snake-sdl/plateforme/contenu/jalon1_parametrage
BC=~/scratch-stage1a/snake-sdl/linux-build/SNAKE
INC="-I. -I$BC -I$BC/SDL3/include"
# ces -I SDL viennent en fait des chemins SNAKE_ROOT, mais BUILD_COPY suffit pour les en-têtes projet
SROOT=~/scratch-stage1a/snake-sdl/extracted/SNAKE_STAGE
INC="-I. -I$BC -I$SROOT/SDL3/include -I$SROOT/SDL3_ttf/include -I$SROOT/SDL3_image/include"
gcc -Wall $INC corrige.c test_reference.c stubs.c $(pkg-config --libs sdl3) -o /tmp/jref_ok && /tmp/jref_ok; echo "corrige code=$?"
gcc -Wall $INC corrige_buggue.c test_reference.c stubs.c $(pkg-config --libs sdl3) -o /tmp/jref_bug && /tmp/jref_bug; echo "buggue code=$?"
```
Expected : contre le corrigé, `TOUT PASSE` et `code=0`. Contre le buggé, des `FAIL` et `code` non nul, le test attrape bien le bug.

- [ ] **Step 10: Commit**

```bash
cd ~/scratch-stage1a/snake-sdl/plateforme
git add -A && git commit -m "contenu jalon 1, mode test a ecrire, corrige bug stubs harnais apercu"
```

---

## Task 4: Exécuteur, recette perso et porte perso

**Files:**
- Create: `plateforme/executeur.py`
- Create: `plateforme/tests/test_executeur.py`

**Interfaces:**
- Consumes: `modele_etape.Etape`, `chemins`.
- Produces: `executeur.Resultat` (dataclass `ok: bool, sortie: str`), `executeur.porte_perso(etape: Etape, code_eleve: str) -> Resultat`. Le helper interne `executeur._compiler_et_lancer(sources: list[Path], includes: list[Path], cflags: list[str] = [], libs: list[str] = [], timeout: int = 15) -> Resultat`.

- [ ] **Step 1: Écrire le test d'abord, `tests/test_executeur.py`**

```python
import unittest
import chemins
from modele_etape import charger_etape
from executeur import porte_perso


class TestPortePerso(unittest.TestCase):
    def setUp(self):
        self.etape = charger_etape(chemins.CONTENU / "perso_P1")
        self.corrige = (self.etape.dossier / "corrige.c").read_text(encoding="utf-8")
        self.starter = (self.etape.dossier / "starter.c").read_text(encoding="utf-8")

    def test_corrige_passe(self):
        r = porte_perso(self.etape, self.corrige)
        self.assertTrue(r.ok, r.sortie)

    def test_starter_echoue(self):
        r = porte_perso(self.etape, self.starter)
        self.assertFalse(r.ok, r.sortie)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Lancer le test, vérifier qu'il échoue**

Run: `cd ~/scratch-stage1a/snake-sdl/plateforme && python3 -m unittest tests.test_executeur -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'executeur'`.

- [ ] **Step 3: Écrire `executeur.py`, partie helper et porte perso**

```python
"""Compile et exécute du C, rend un résultat. Aucune UI ici.
Le code de sortie du programme fait foi, pas le texte affiché."""
from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile

import chemins
from modele_etape import Etape


@dataclass
class Resultat:
    ok: bool
    sortie: str


def _compiler_et_lancer(sources: list[Path], includes: list[Path],
                        cflags: list[str] = [], libs: list[str] = [],
                        timeout: int = 15) -> Resultat:
    with tempfile.TemporaryDirectory() as d:
        binaire = Path(d) / "prog"
        cmd = ["gcc", "-Wall", "-Wno-unused-parameter", "-Wno-unused-variable"]
        cmd += [f"-I{i}" for i in includes]
        cmd += cflags
        cmd += [str(s) for s in sources]
        cmd += libs
        cmd += ["-lm", "-o", str(binaire)]
        comp = subprocess.run(cmd, capture_output=True, text=True)
        if comp.returncode != 0:
            return Resultat(False, "Erreur de compilation :\n" + comp.stderr)
        try:
            run = subprocess.run([str(binaire)], capture_output=True, text=True,
                                 timeout=timeout)
        except subprocess.TimeoutExpired:
            return Resultat(False, "Le test a dépassé le délai, boucle infinie probable.")
        return Resultat(run.returncode == 0, run.stdout + run.stderr)


def porte_perso(etape: Etape, code_eleve: str) -> Resultat:
    """Compile le code de l'étudiant avec tests.c de l'étape, exécute, code 0 = porte ouverte."""
    with tempfile.TemporaryDirectory() as d:
        soumission = Path(d) / "soumission.c"
        soumission.write_text(code_eleve, encoding="utf-8")
        sources = [soumission, etape.dossier / "tests.c"]
        includes = [etape.dossier]
        return _compiler_et_lancer(sources, includes)
```

- [ ] **Step 4: Lancer le test, vérifier qu'il passe**

Run: `python3 -m unittest tests.test_executeur -v`
Expected: PASS, 2 tests. Le corrigé ouvre la porte, le starter ne l'ouvre pas.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "executeur, recette perso et porte perso, executes vraiment"
```

---

## Task 5: Exécuteur, recette jalon, méta-test et porte jalon

**Files:**
- Modify: `plateforme/executeur.py`
- Modify: `plateforme/tests/test_executeur.py`

**Interfaces:**
- Consumes: `modele_etape.Etape`, `chemins`, le helper `_compiler_et_lancer`.
- Produces: `executeur.ResultatTest` (dataclass `test_solide: bool, passe_corrige: bool, attrape_bug: bool, sortie: str`), `executeur.juger_test(etape: Etape, test_eleve: str) -> ResultatTest`, `executeur.porte_jalon(etape: Etape, code_eleve: str, test_eleve: str) -> Resultat`, et le helper `executeur._includes_jalon() -> list[Path]`.

- [ ] **Step 1: Ajouter les tests, dans `tests/test_executeur.py`**

Ajouter, en réutilisant `import` existants, plus `from executeur import juger_test, porte_jalon` en haut :

```python
class TestJalon(unittest.TestCase):
    def setUp(self):
        self.etape = charger_etape(chemins.CONTENU / "jalon1_parametrage")
        self.test_ref = (self.etape.dossier / "test_reference.c").read_text(encoding="utf-8")
        self.corrige = (self.etape.dossier / "corrige.c").read_text(encoding="utf-8")
        # un test mou : il vérifie seulement que l'état a changé, il rate le bug
        self.test_mou = (
            '#include <stdio.h>\n#include "harnais.h"\n'
            'int main(void){ int etat=12345; SDL_Event e; simuler_clic(0);'
            ' SP_Gestion_Evenements_MENU_PARAMETRAGE(e,&etat);'
            ' if(etat==12345){printf("FAIL\\n");return 1;} printf("ok\\n"); return 0; }\n'
        )

    def test_reference_est_solide(self):
        r = juger_test(self.etape, self.test_ref)
        self.assertTrue(r.passe_corrige, r.sortie)
        self.assertTrue(r.attrape_bug, r.sortie)
        self.assertTrue(r.test_solide, r.sortie)

    def test_mou_est_rejete(self):
        r = juger_test(self.etape, self.test_mou)
        self.assertTrue(r.passe_corrige, r.sortie)
        self.assertFalse(r.attrape_bug, r.sortie)
        self.assertFalse(r.test_solide, r.sortie)

    def test_porte_jalon_corrige_passe(self):
        r = porte_jalon(self.etape, self.corrige, self.test_ref)
        self.assertTrue(r.ok, r.sortie)
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `python3 -m unittest tests.test_executeur -v`
Expected: FAIL, `ImportError: cannot import name 'juger_test'`.

- [ ] **Step 3: Étendre `executeur.py`**

Ajouter en haut la dataclass, et les fonctions :

```python
@dataclass
class ResultatTest:
    test_solide: bool
    passe_corrige: bool
    attrape_bug: bool
    sortie: str


def _includes_jalon() -> list[Path]:
    # les en-têtes projet viennent de la copie de build, la casse y est corrigée
    return [chemins.BUILD_COPY] + chemins.SDL_INCLUDES


def juger_test(etape: Etape, test_eleve: str) -> ResultatTest:
    """Juge le test de l'étudiant : il doit passer le corrigé et attraper le bug planté."""
    includes = [etape.dossier] + _includes_jalon()
    libs = chemins.libs_sdl(avec_ttf_image=False)
    with tempfile.TemporaryDirectory() as d:
        t = Path(d) / "test_eleve.c"
        t.write_text(test_eleve, encoding="utf-8")
        stubs = etape.dossier / "stubs.c"

        r_ok = _compiler_et_lancer([etape.dossier / "corrige.c", t, stubs], includes, libs=libs)
        r_bug = _compiler_et_lancer([etape.dossier / "corrige_buggue.c", t, stubs], includes, libs=libs)

        passe_corrige = r_ok.ok
        attrape_bug = (not r_bug.ok) and ("Erreur de compilation" not in r_bug.sortie)
        solide = passe_corrige and attrape_bug
        sortie = ("Contre le corrigé, ton test doit passer :\n" + r_ok.sortie +
                  "\nContre une version buggée, ton test doit échouer :\n" + r_bug.sortie)
        return ResultatTest(solide, passe_corrige, attrape_bug, sortie)


def porte_jalon(etape: Etape, code_eleve: str, test_eleve: str) -> Resultat:
    """Lance le test solide de l'étudiant contre son propre code. Code 0 = porte ouverte."""
    includes = [etape.dossier] + _includes_jalon()
    libs = chemins.libs_sdl(avec_ttf_image=False)
    with tempfile.TemporaryDirectory() as d:
        code = Path(d) / etape.fichier_edite
        code.write_text(code_eleve, encoding="utf-8")
        t = Path(d) / "test_eleve.c"
        t.write_text(test_eleve, encoding="utf-8")
        return _compiler_et_lancer([code, t, etape.dossier / "stubs.c"], includes, libs=libs)
```

- [ ] **Step 4: Lancer, vérifier le succès**

Run: `python3 -m unittest tests.test_executeur -v`
Expected: PASS, 5 tests au total. Le test de référence est jugé solide, le test mou est rejeté car il n'attrape pas le bug, la porte du corrigé passe.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "executeur, meta-test du test eleve et porte jalon"
```

---

## Task 6: Exécuteur, aperçu graphique du jalon

**Files:**
- Modify: `plateforme/executeur.py`
- Modify: `plateforme/tests/test_executeur.py`

**Interfaces:**
- Consumes: `modele_etape.Etape`, `chemins`.
- Produces: `executeur.construire_apercu(etape: Etape, code_eleve: str) -> tuple[Resultat, Path | None]` qui construit le binaire d'aperçu et rend le chemin du binaire si la compilation passe, et `executeur.lancer_jeu(etape: Etape, code_eleve: str) -> Resultat` qui construit puis lance la fenêtre en sous-processus détaché.

Note de conception : l'aperçu se lie à la bibliothèque du projet seulement, pas aux fichiers de gameplay incomplets de l'archive. Les sources sont explicites et confirmées présentes. La version du fichier édité de l'archive est exclue, on met celle de l'étudiant.

- [ ] **Step 1: Ajouter le test de construction, dans `tests/test_executeur.py`**

Ajouter `from executeur import construire_apercu` en haut, puis :

```python
class TestApercu(unittest.TestCase):
    def test_apercu_se_construit_avec_le_corrige(self):
        etape = charger_etape(chemins.CONTENU / "jalon1_parametrage")
        corrige = (etape.dossier / "corrige.c").read_text(encoding="utf-8")
        resultat, binaire = construire_apercu(etape, corrige)
        self.assertTrue(resultat.ok, resultat.sortie)
        self.assertIsNotNone(binaire)
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `python3 -m unittest tests.test_executeur.TestApercu -v`
Expected: FAIL, `ImportError: cannot import name 'construire_apercu'`.

- [ ] **Step 3: Étendre `executeur.py`, l'aperçu**

```python
import shutil

# Sources de la bibliothèque du projet suffisantes pour un menu. Confirmées présentes
# dans la copie de build. On évite les fichiers de gameplay incomplets de l'archive.
_SOURCES_APERCU = [
    "Bibliotheque_source/Initialisation_SDL.c",
    "Bibliotheque_source/OutilsDessin.c",
    "Bibliotheque_source/OutilsBouton.c",
    "Bibliotheque_source/OutilsCouleur.c",
    "Bibliotheque_source/OutilsZoneTexte.c",
    "InitialisationTexture.c",
    "VariablesGlobales.c",
]


def construire_apercu(etape: Etape, code_eleve: str):
    """Construit le binaire d'aperçu : le code de l'étudiant plus apercu.c plus la
    bibliothèque du projet. Rend (Resultat, chemin_binaire_ou_None)."""
    persistant = Path(tempfile.mkdtemp(prefix="apercu_"))
    code = persistant / etape.fichier_edite
    code.write_text(code_eleve, encoding="utf-8")
    binaire = persistant / "apercu"

    sources = [code, etape.dossier / "apercu.c"]
    sources += [chemins.BUILD_COPY / s for s in _SOURCES_APERCU]
    includes = [etape.dossier, chemins.BUILD_COPY, chemins.BUILD_COPY / "Bibliotheque_header"]
    includes += chemins.SDL_INCLUDES

    cmd = ["gcc", "-Wall", "-Wno-unused-parameter", "-Wno-unused-variable"]
    cmd += [f"-I{i}" for i in includes]
    cmd += chemins.cflags_sdl(avec_ttf_image=True)
    cmd += [str(s) for s in sources]
    cmd += chemins.libs_sdl(avec_ttf_image=True)
    cmd += ["-lm", "-o", str(binaire)]
    comp = subprocess.run(cmd, capture_output=True, text=True)
    if comp.returncode != 0:
        shutil.rmtree(persistant, ignore_errors=True)
        return Resultat(False, "Erreur de compilation de l'aperçu :\n" + comp.stderr), None
    return Resultat(True, "Aperçu construit."), binaire


def lancer_jeu(etape: Etape, code_eleve: str) -> Resultat:
    """Construit l'aperçu puis ouvre la fenêtre. Les assets sont chargés en chemin
    relatif, donc on lance depuis la copie de build."""
    resultat, binaire = construire_apercu(etape, code_eleve)
    if not resultat.ok:
        return resultat
    subprocess.Popen([str(binaire)], cwd=str(chemins.BUILD_COPY))
    return Resultat(True, "Fenêtre lancée. Échap pour fermer.")
```

- [ ] **Step 4: Lancer, vérifier le succès de la construction**

Run: `python3 -m unittest tests.test_executeur.TestApercu -v`
Expected: PASS. Si la liaison échoue sur un symbole manquant, lire le nom dans le message et ajouter la source correspondante de `Bibliotheque_source` à `_SOURCES_APERCU`, c'est la même boucle compiler puis lire l'erreur que le projet enseigne.

- [ ] **Step 5: Vérifier la fenêtre à la main, sur l'affichage**

```bash
cd ~/scratch-stage1a/snake-sdl/plateforme
python3 -c "import chemins; from modele_etape import charger_etape; from executeur import lancer_jeu; e=charger_etape(chemins.CONTENU/'jalon1_parametrage'); print(lancer_jeu(e,(e.dossier/'corrige.c').read_text()).sortie)"
```
Expected : une fenêtre s'ouvre avec les quatre boutons du menu Paramétrage, couleur serpent, couleur fond, couleur bord, retour. Échap ferme.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "executeur, apercu graphique du jalon, dessine les boutons de l etudiant"
```

---

## Task 7: Progression, état persistant et déverrouillage

**Files:**
- Create: `plateforme/progression.py`
- Create: `plateforme/tests/test_progression.py`

**Interfaces:**
- Consumes: `modele_etape.Etape`, `chemins`.
- Produces: `progression.Progression` (dataclass `etapes_faites: list[str], cran_max: int`), `progression.charger(fichier: Path = chemins.PROGRESSION_FICHIER) -> Progression`, `progression.sauver(p: Progression, fichier: Path = chemins.PROGRESSION_FICHIER) -> None`, `progression.etape_deverrouillee(etape: Etape, parcours: list[Etape], prog: Progression) -> bool`, `progression.valider(etape: Etape, prog: Progression) -> Progression`, `progression.cran_disponible(prog: Progression) -> int`.

- [ ] **Step 1: Écrire le test d'abord, `tests/test_progression.py`**

```python
import unittest
import tempfile
from pathlib import Path
import chemins
from modele_etape import charger_parcours
from progression import (Progression, charger, sauver, etape_deverrouillee,
                         valider, cran_disponible)


class TestProgression(unittest.TestCase):
    def setUp(self):
        self.parcours = charger_parcours(chemins.CONTENU)
        self.p1, self.j1 = self.parcours[0], self.parcours[1]

    def test_depart_seule_premiere_deverrouillee(self):
        prog = Progression(etapes_faites=[], cran_max=0)
        self.assertTrue(etape_deverrouillee(self.p1, self.parcours, prog))
        self.assertFalse(etape_deverrouillee(self.j1, self.parcours, prog))
        self.assertEqual(cran_disponible(prog), 0)

    def test_valider_debloque_la_suite_et_le_cran(self):
        prog = valider(self.p1, Progression(etapes_faites=[], cran_max=0))
        self.assertIn("perso_P1", prog.etapes_faites)
        self.assertEqual(prog.cran_max, 1)
        self.assertTrue(etape_deverrouillee(self.j1, self.parcours, prog))

    def test_sauver_puis_charger(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "p.json"
            sauver(Progression(["perso_P1"], 1), f)
            relu = charger(f)
            self.assertEqual(relu.etapes_faites, ["perso_P1"])
            self.assertEqual(relu.cran_max, 1)

    def test_charger_absent_rend_vierge(self):
        relu = charger(Path("/tmp/nexiste_pas_42.json"))
        self.assertEqual(relu.etapes_faites, [])
        self.assertEqual(relu.cran_max, 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `python3 -m unittest tests.test_progression -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'progression'`.

- [ ] **Step 3: Écrire `progression.py`**

```python
"""État persistant de l'étudiant et règles de déverrouillage. Aucune UI."""
from dataclasses import dataclass, asdict
from pathlib import Path
import json

import chemins
from modele_etape import Etape


@dataclass
class Progression:
    etapes_faites: list[str]
    cran_max: int


def charger(fichier: Path = chemins.PROGRESSION_FICHIER) -> Progression:
    if not Path(fichier).exists():
        return Progression(etapes_faites=[], cran_max=0)
    d = json.loads(Path(fichier).read_text(encoding="utf-8"))
    return Progression(etapes_faites=d.get("etapes_faites", []), cran_max=d.get("cran_max", 0))


def sauver(p: Progression, fichier: Path = chemins.PROGRESSION_FICHIER) -> None:
    Path(fichier).write_text(json.dumps(asdict(p), ensure_ascii=False, indent=2),
                             encoding="utf-8")


def etape_deverrouillee(etape: Etape, parcours: list[Etape], prog: Progression) -> bool:
    """Déverrouillée si toutes les étapes qui la précèdent dans le parcours sont faites."""
    for e in parcours:
        if e.id == etape.id:
            return True
        if e.id not in prog.etapes_faites:
            return False
    return False


def valider(etape: Etape, prog: Progression) -> Progression:
    faites = list(prog.etapes_faites)
    if etape.id not in faites:
        faites.append(etape.id)
    return Progression(faites, max(prog.cran_max, etape.cran_debloque))


def cran_disponible(prog: Progression) -> int:
    return prog.cran_max
```

- [ ] **Step 4: Lancer, vérifier le succès**

Run: `python3 -m unittest tests.test_progression -v`
Expected: PASS, 4 tests.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "progression, etat persistant et deverrouillage par les portes"
```

---

## Task 8: Tuteur IA, prompt par cran et filtre de solution

**Files:**
- Create: `plateforme/tuteur_ia.py`
- Create: `plateforme/tests/test_tuteur_ia.py`

**Interfaces:**
- Consumes: `modele_etape.Etape`.
- Produces: `tuteur_ia.construire_prompt(etape: Etape, code_eleve: str, question: str, niveau: int) -> str`, `tuteur_ia.filtre_solution(reponse: str, corrige: str) -> str`, `tuteur_ia.moteur_disponible() -> bool`, `tuteur_ia.demander_aide(etape: Etape, code_eleve: str, question: str, niveau: int) -> str`.

- [ ] **Step 1: Écrire le test d'abord, `tests/test_tuteur_ia.py`**

```python
import unittest
import chemins
from modele_etape import charger_etape
from tuteur_ia import construire_prompt, filtre_solution


class TestTuteur(unittest.TestCase):
    def setUp(self):
        self.etape = charger_etape(chemins.CONTENU / "perso_P1")

    def test_prompt_n0_interdit_le_code(self):
        p = construire_prompt(self.etape, "code", "comment faire ?", 0)
        self.assertIn("explique", p.lower())
        self.assertIn("sans donner", p.lower())

    def test_prompt_n3_est_libre(self):
        p = construire_prompt(self.etape, "code", "comment faire ?", 3)
        self.assertIn("libre", p.lower())

    def test_filtre_masque_la_ligne_solution(self):
        corrige = "void f(int* p){\n    *p_etat = MENU_PARAMETRAGE;\n}\n"
        reponse = ("Voici la correction :\n"
                   "    *p_etat = MENU_PARAMETRAGE;\n"
                   "et voilà, c'est tout.")
        filtre = filtre_solution(reponse, corrige)
        self.assertNotIn("*p_etat = MENU_PARAMETRAGE;", filtre)
        self.assertIn("Voici la correction", filtre)
        self.assertIn("c'est tout", filtre)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `python3 -m unittest tests.test_tuteur_ia -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'tuteur_ia'`.

- [ ] **Step 3: Écrire `tuteur_ia.py`**

```python
"""Tuteur IA bridé. Prompt selon le cran, filtre déterministe qui masque la solution,
appel du moteur en sous-processus. Aucune UI."""
import os
import re
import shutil
import subprocess

from modele_etape import Etape

_CONSIGNE_CRAN = {
    0: "Cran N0. Explique seulement le concept en jeu, avec tes mots, sans donner ni "
       "écrire la moindre ligne de la solution. Pose une question qui fait réfléchir.",
    1: "Cran N1. Tu peux donner un squelette vide ou une analogie, mais pas la solution "
       "écrite. Montre la forme, pas le contenu.",
    2: "Cran N2. Tu peux proposer une piste candidate, mais demande à l'étudiant de la "
       "justifier et de la vérifier lui-même, sans affirmer qu'elle est correcte.",
    3: "Cran N3. Tu es libre d'aider comme tu veux.",
}


def construire_prompt(etape: Etape, code_eleve: str, question: str, niveau: int) -> str:
    enonce = (etape.dossier / "enonce.md").read_text(encoding="utf-8")
    return (
        "Tu es un tuteur de programmation C pour un étudiant débutant. Tu n'es jamais "
        "celui qui résout à sa place.\n\n"
        f"{_CONSIGNE_CRAN.get(niveau, _CONSIGNE_CRAN[0])}\n\n"
        f"Énoncé de l'étape :\n{enonce}\n\n"
        f"Code actuel de l'étudiant :\n{code_eleve}\n\n"
        f"Question de l'étudiant :\n{question}\n"
    )


def _lignes_significatives(code: str) -> list[str]:
    lignes = []
    for ligne in code.splitlines():
        nu = ligne.strip()
        if len(nu) < 6:            # ignore {, }, lignes trop courtes
            continue
        if nu.startswith("//") or nu.startswith("/*") or nu.startswith("*"):
            continue
        if nu.startswith("#include"):
            continue
        lignes.append(nu)
    return lignes


def filtre_solution(reponse: str, corrige: str) -> str:
    """Masque dans la réponse les lignes qui reproduisent une ligne du corrigé,
    laisse passer tout le reste."""
    cibles = set(_lignes_significatives(corrige))
    sortie = []
    for ligne in reponse.splitlines():
        if ligne.strip() in cibles:
            sortie.append("    … (ligne masquée par le filtre anti-solution) …")
        else:
            sortie.append(ligne)
    return "\n".join(sortie)


def moteur_disponible() -> bool:
    moteur = os.environ.get("ATELIER_AI", "claude")
    binaire = moteur.split(":", 1)[0]
    return shutil.which(binaire) is not None


def demander_aide(etape: Etape, code_eleve: str, question: str, niveau: int) -> str:
    if not moteur_disponible():
        return "Moteur IA indisponible. Le reste de l'atelier marche, compiler, tester, lancer."
    prompt = construire_prompt(etape, code_eleve, question, niveau)
    moteur = os.environ.get("ATELIER_AI", "claude")
    try:
        r = subprocess.run([moteur.split(":", 1)[0], "-p", prompt],
                           capture_output=True, text=True, timeout=60)
        reponse = r.stdout.strip() or r.stderr.strip()
    except subprocess.TimeoutExpired:
        return "Le moteur IA n'a pas répondu à temps."
    corrige = (etape.dossier / "corrige.c").read_text(encoding="utf-8")
    return filtre_solution(reponse, corrige)
```

- [ ] **Step 4: Lancer, vérifier le succès**

Run: `python3 -m unittest tests.test_tuteur_ia -v`
Expected: PASS, 3 tests. Le filtre masque la ligne de solution et garde le reste.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "tuteur ia, prompt par cran et filtre deterministe anti-solution"
```

---

## Task 9: Fenêtre, point d'entrée, autotests

**Files:**
- Create: `plateforme/fenetre.py`
- Create: `plateforme/atelier_snake.py`

**Interfaces:**
- Consumes: tous les modules précédents.
- Produces: `fenetre.Fenetre` (QMainWindow), `fenetre.construire(app)` qui rend une `Fenetre` sans l'afficher pour le smoketest, `atelier_snake` avec les options `--selftest` et `--smoketest`.

- [ ] **Step 1: Écrire `fenetre.py`**

```python
"""Fenêtre de l'atelier Snake. Câble énoncé, éditeur, console, tuteur et portes."""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
                             QPlainTextEdit, QTextEdit, QPushButton, QLabel, QTabWidget,
                             QListWidgetItem, QInputDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

import chemins
import executeur
import progression
import tuteur_ia
from modele_etape import charger_parcours


class FilTuteur(QThread):
    """Appel IA dans un fil séparé pour ne pas figer la fenêtre."""
    repondu = pyqtSignal(str)

    def __init__(self, etape, code, question, niveau):
        super().__init__()
        self._args = (etape, code, question, niveau)

    def run(self):
        self.repondu.emit(tuteur_ia.demander_aide(*self._args))


class Fenetre(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atelier Snake")
        self.parcours = charger_parcours(chemins.CONTENU)
        self.prog = progression.charger()
        self.etape = self.parcours[0]
        self.niveau = 0

        self.liste = QListWidget()
        self.liste.currentRowChanged.connect(self._changer_etape)

        self.enonce = QTextEdit(readOnly=True)
        self.editeur = QPlainTextEdit()
        self.editeur_test = QPlainTextEdit()
        self.onglets = QTabWidget()
        self.onglets.addTab(self.editeur, "Mon code")
        self.onglets.addTab(self.editeur_test, "Mon test")

        self.console = QTextEdit(readOnly=True)
        self.label_cran = QLabel()
        self.reponse_tuteur = QTextEdit(readOnly=True)

        b_compiler = QPushButton("Compiler")
        b_tester = QPushButton("Tester")
        self.b_jeu = QPushButton("Lancer le jeu")
        b_aide = QPushButton("Demander de l'aide")
        b_compiler.clicked.connect(self._compiler)
        b_tester.clicked.connect(self._tester)
        self.b_jeu.clicked.connect(self._lancer_jeu)
        b_aide.clicked.connect(self._demander_aide)

        barre = QHBoxLayout()
        for b in (b_compiler, b_tester, self.b_jeu, b_aide):
            barre.addWidget(b)

        centre = QVBoxLayout()
        centre.addWidget(self.enonce, 2)
        centre.addWidget(self.onglets, 5)
        centre.addLayout(barre)
        centre.addWidget(self.console, 3)

        droite = QVBoxLayout()
        droite.addWidget(self.label_cran)
        droite.addWidget(self.reponse_tuteur)

        racine = QHBoxLayout()
        racine.addWidget(self.liste, 1)
        racine.addLayout(centre, 4)
        racine.addLayout(droite, 2)
        conteneur = QWidget()
        conteneur.setLayout(racine)
        self.setCentralWidget(conteneur)

        self._remplir_liste()
        self.liste.setCurrentRow(0)

    def _remplir_liste(self):
        self.liste.clear()
        for e in self.parcours:
            ouverte = progression.etape_deverrouillee(e, self.parcours, self.prog)
            faite = e.id in self.prog.etapes_faites
            marque = "[fait]" if faite else ("[ouvert]" if ouverte else "[verrou]")
            item = QListWidgetItem(f"{marque}  {e.titre}")
            if not ouverte:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.liste.addItem(item)

    def _changer_etape(self, ligne):
        if ligne < 0:
            return
        self.etape = self.parcours[ligne]
        self.enonce.setMarkdown((self.etape.dossier / "enonce.md").read_text(encoding="utf-8"))
        self.editeur.setPlainText((self.etape.dossier / "starter.c").read_text(encoding="utf-8"))
        self.editeur_test.setPlainText("")
        a_ecrire = self.etape.mode == "test_a_ecrire"
        self.onglets.setTabVisible(1, a_ecrire)
        self.b_jeu.setVisible(self.etape.type == "jalon")
        self._maj_cran()

    def _maj_cran(self):
        dispo = progression.cran_disponible(self.prog)
        self.label_cran.setText(f"Tuteur, cran courant N{min(self.niveau, dispo)} sur N{dispo} débloqué")

    def _compiler(self):
        self.console.setPlainText("Compilation et exécution en cours…")
        self._tester()

    def _tester(self):
        code = self.editeur.toPlainText()
        if self.etape.mode == "test_fourni":
            r = executeur.porte_perso(self.etape, code)
            self._afficher_porte(r.ok, r.sortie)
        else:
            test = self.editeur_test.toPlainText()
            jug = executeur.juger_test(self.etape, test)
            if not jug.test_solide:
                self.console.setPlainText(
                    "Ton test n'est pas encore solide.\n" +
                    ("Il rejette un code correct.\n" if not jug.passe_corrige else "") +
                    ("Il laisse passer un bug, renforce-le.\n" if not jug.attrape_bug else "") +
                    "\n" + jug.sortie)
                return
            r = executeur.porte_jalon(self.etape, code, test)
            self._afficher_porte(r.ok, "Ton test est solide.\n" + r.sortie)

    def _afficher_porte(self, ok, sortie):
        self.console.setPlainText(("PORTE OUVERTE\n\n" if ok else "PORTE FERMÉE\n\n") + sortie)
        if ok:
            self.prog = progression.valider(self.etape, self.prog)
            progression.sauver(self.prog)
            self.niveau = progression.cran_disponible(self.prog)
            self._remplir_liste()
            self._maj_cran()

    def _lancer_jeu(self):
        r = executeur.lancer_jeu(self.etape, self.editeur.toPlainText())
        self.console.setPlainText(r.sortie)

    def _demander_aide(self):
        question, ok = QInputDialog.getText(self, "Demander de l'aide", "Ta question :")
        if not ok or not question:
            return
        dispo = progression.cran_disponible(self.prog)
        niveau = min(self.niveau, dispo)
        self.reponse_tuteur.setPlainText("Le tuteur réfléchit…")
        self._fil = FilTuteur(self.etape, self.editeur.toPlainText(), question, niveau)
        self._fil.repondu.connect(self.reponse_tuteur.setPlainText)
        self._fil.start()


def construire(app):
    """Construit la fenêtre sans l'afficher. Sert au smoketest."""
    return Fenetre()
```

- [ ] **Step 2: Écrire `atelier_snake.py`, le point d'entrée et les autotests**

```python
#!/usr/bin/env python3
"""Atelier Snake. Lance l'appli, ou les autotests sans écran.
  python3 atelier_snake.py             lance la fenêtre
  python3 atelier_snake.py --selftest  vérifie les portes sans écran
  python3 atelier_snake.py --smoketest construit la fenêtre sans l'afficher
"""
import sys

import chemins
import executeur
from modele_etape import charger_parcours, charger_etape


def selftest() -> int:
    echecs = 0

    p1 = charger_etape(chemins.CONTENU / "perso_P1")
    if not executeur.porte_perso(p1, (p1.dossier / "corrige.c").read_text()).ok:
        print("FAIL P1 : le corrigé devrait passer"); echecs += 1
    if executeur.porte_perso(p1, (p1.dossier / "starter.c").read_text()).ok:
        print("FAIL P1 : le starter ne devrait pas passer"); echecs += 1

    j1 = charger_etape(chemins.CONTENU / "jalon1_parametrage")
    ref = (j1.dossier / "test_reference.c").read_text()
    jug = executeur.juger_test(j1, ref)
    if not jug.test_solide:
        print("FAIL jalon1 : le test de référence devrait être jugé solide\n", jug.sortie)
        echecs += 1
    if not executeur.porte_jalon(j1, (j1.dossier / "corrige.c").read_text(), ref).ok:
        print("FAIL jalon1 : la porte du corrigé devrait passer"); echecs += 1

    print("SELFTEST OK" if echecs == 0 else f"SELFTEST {echecs} ECHEC(S)")
    return echecs


def smoketest() -> int:
    from PyQt6.QtWidgets import QApplication
    import fenetre
    app = QApplication.instance() or QApplication([])
    f = fenetre.construire(app)
    print("SMOKETEST OK, fenêtre construite :", f.windowTitle())
    return 0


def main():
    if "--selftest" in sys.argv:
        sys.exit(1 if selftest() else 0)
    if "--smoketest" in sys.argv:
        sys.exit(smoketest())
    from PyQt6.QtWidgets import QApplication
    import fenetre
    app = QApplication(sys.argv)
    f = fenetre.Fenetre()
    f.resize(1280, 800)
    f.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Lancer le selftest, sans écran**

Run: `cd ~/scratch-stage1a/snake-sdl/plateforme && python3 atelier_snake.py --selftest`
Expected: `SELFTEST OK`, code de sortie 0. Les portes P1 et jalon 1 tiennent de bout en bout.

- [ ] **Step 4: Lancer le smoketest, sans afficher**

Run: `QT_QPA_PLATFORM=offscreen python3 atelier_snake.py --smoketest`
Expected: `SMOKETEST OK, fenêtre construite : Atelier Snake`, code 0.

- [ ] **Step 5: Vérifier l'appli à la main**

Run: `cd ~/scratch-stage1a/snake-sdl/plateforme && python3 atelier_snake.py`
Expected : la fenêtre s'ouvre sur P1, le jalon 1 est verrouillé. Remplir P1, Tester ouvre la porte, le jalon 1 se déverrouille et le cran passe à N1. Sur le jalon 1, l'onglet Mon test apparaît, écrire un test mou est rejeté, un test solide ouvre la porte, Lancer le jeu montre les boutons.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "fenetre pyqt6, point d entree, selftest et smoketest"
```

---

## Auto-revue du plan

**Couverture de la spec.** Section 2 périmètre v1, tâches 2 et 3. Section 3 contenu en données, tâche 1, `meta.json` plus `parcours.json`. Section 4 les deux modes de test, tâches 4 et 5. Section 5 débridage par les portes, tâches 7 et 9. Section 6 deux couches de preuve, tâches 5 et 6. Section 7 recettes, tâches 4 à 6. Section 8 interface, tâche 9. Section 9 découpage, respecté un fichier par responsabilité. Section 10 progression, tâche 7. Section 11 robustesse, gérée dans `_compiler_et_lancer` timeout et erreurs, et le moteur IA absent en tâche 8. Section 12 vérification, `--selftest` et `--smoketest` en tâche 9. Section 13 archive intacte, contrainte globale, on lit la copie de build, jamais l'archive. Annexe A, le jalon 1 en porte le premier cas, les autres viennent comme données après la v1.

**Pas de placeholder.** Tout le code est écrit, aucune mention de à compléter. Le seul point ouvert est volontaire et borné, la liste des sources d'aperçu peut demander un ajout si le lieur réclame un symbole, et la méthode est donnée.

**Cohérence des types.** `Resultat(ok, sortie)` et `ResultatTest(test_solide, passe_corrige, attrape_bug, sortie)` partout. `porte_perso(etape, code)`, `juger_test(etape, test)`, `porte_jalon(etape, code, test)`, `construire_apercu(etape, code)`, `lancer_jeu(etape, code)` cohérents entre l'exécuteur, la fenêtre et le selftest. `Progression(etapes_faites, cran_max)` partout. `construire_prompt`, `filtre_solution`, `demander_aide` cohérents entre tuteur et fenêtre.
