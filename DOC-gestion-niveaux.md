# Gestion des niveaux en interface graphique (mode auteur)

Cette fonctionnalité ajoute, depuis l'appli, un **outil d'auteur** pour ajouter,
retirer et réordonner les niveaux d'un parcours, sans éditer les fichiers à la main.
Elle a été faite côté Windows sur la branche `gui-gestion-niveaux`.

> Côté Linux, l'ajout d'un niveau se fait en créant les fichiers directement. Ici le
> même résultat passe par une fenêtre. Le **format des niveaux est identique** dans les
> deux cas : un outil ne casse pas le travail de l'autre.

## Ce qu'est un niveau (rappel du format commun)

Un niveau (un « exercice ») est un sous-dossier de `contenu/<parcours>/`. Il contient :

| Fichier                | Rôle                                                        |
|------------------------|-------------------------------------------------------------|
| `meta.json`            | Métadonnées lues par `modele_etape.charger_etape`           |
| `enonce.md`            | L'énoncé affiché à l'étudiant (Markdown)                     |
| `starter.c`            | Le code de départ, chargé dans l'éditeur                    |
| `corrige.c`            | Le corrigé de référence, rejoué par la porte                |
| `approfondissement.md` | Optionnel, le « niveau caché » révélé après la porte de base |

Un niveau n'est **actif** que s'il figure dans la liste `ordre` de
`contenu/<parcours>/parcours.json`. Un dossier présent mais absent de `ordre` est un
niveau **détaché** (retiré du parcours, mais conservé sur le disque).

### Champs de `meta.json`

| Champ             | Type   | Sens                                                             |
|-------------------|--------|------------------------------------------------------------------|
| `id`              | texte  | Identifiant, doit valoir le nom du dossier                       |
| `titre`           | texte  | Titre affiché dans la liste et l'énoncé                          |
| `type`            | texte  | `programme` pour un exercice programme complet                  |
| `mode`            | texte  | `programme`, `test_fourni` ou `test_a_ecrire`                    |
| `fichier_edite`   | texte  | Nom du fichier que l'étudiant édite (ex : `programme.c`)         |
| `cran_debloque`   | entier | Cran d'aide tuteur débloqué à la validation (0 à 3)             |
| `noeud_cours`     | texte  | Rappel du point de cours visé, sert au tuteur                   |
| `sortie_attendue` | liste  | Fragments qui doivent figurer dans la sortie (mode `programme`) |

## Ouvrir l'outil dans l'appli

1. Menu **Paramètres → Gérer les niveaux…**
2. Saisir le **mot de passe auteur** (voir plus bas).
3. La fenêtre liste les niveaux actifs dans l'ordre. Boutons disponibles :
   - **Ajouter…** : ouvre un formulaire (id, titre, mode, fichier édité, cran, nœud de
     cours, sortie attendue). À la validation, le dossier et ses gabarits sont créés et
     le niveau est ajouté en fin de parcours. L'appli propose alors de l'éditer tout de
     suite.
   - **Modifier…** : ouvre l'éditeur de contenu du niveau sélectionné. Un onglet par
     fichier (`enonce.md`, `starter.c`, `corrige.c`), plus le titre et la sortie
     attendue. Enregistrer écrit dans les fichiers, sans passer par l'Explorateur.
   - **Retirer** : **détache** le niveau (le sort de `ordre`). Le dossier n'est **pas
     effacé**, on peut le remettre plus tard.
   - **Monter / Descendre** : change la place du niveau dans le parcours.
   - **Détachés…** : liste les niveaux détachés (dossier présent, absent de `ordre`) et
     en réattache un au parcours.

Après la fermeture de la fenêtre, la liste du parcours dans l'appli est rechargée.

> Après un **Ajouter**, remplis `enonce.md`, `starter.c`, `corrige.c` et la sortie
> attendue via **Modifier…** : les gabarits sont volontairement vides. La porte d'un
> exercice `programme` ne s'ouvre que quand `corrige.c` produit bien la `sortie_attendue`.

## Le mot de passe auteur

L'édition du contenu est réservée au mode auteur pour qu'un étudiant ne modifie pas le
parcours par curiosité. Le mot de passe n'est jamais stocké en clair (empreinte SHA-256).

- **Par défaut** : `auteur`. À changer dès que possible via **Paramètres → Changer le
  mot de passe auteur…**.
- Le nouveau mot de passe est enregistré dans `auteur.json`, à la racine du dépôt. Ce
  fichier est **git-ignoré** : il reste local à chaque poste, il n'est pas partagé.
- Poste enseignant sans `auteur.json` : on peut fixer le mot de passe par la variable
  d'environnement `ATELIER_AUTEUR_MDP` avant de lancer l'appli.

Ordre de résolution : `auteur.json` s'il existe, sinon `ATELIER_AUTEUR_MDP`, sinon le
défaut `auteur`.

## Lancement sans commande et menu Paramètres

L'appli se pilote sans taper de commande.

- **`Atelier.bat`** (racine) : double-clic pour lancer. Il détecte Python (l'installation
  utilisateur `Python312` d'abord, sinon le lanceur `py`), ajoute le compilateur portable
  `w64devkit\bin` au PATH s'il est présent, puis lance l'appli. Aucun `--parcours` à
  passer : le parcours vient de `reglages.json`.
- **Raccourci bureau** : la fenêtre de diagnostic (voir plus bas) a un bouton « Créer un
  raccourci sur le bureau » qui pose un « Atelier TP C.lnk » pointant sur `Atelier.bat`.

Le menu **Paramètres** contient, en plus de la gestion des niveaux :

- **Changer de parcours…** : liste les dossiers de `contenu\` qui ont un `parcours.json`,
  et mémorise le choix dans `reglages.json`. Le changement prend effet **au prochain
  lancement** (ferme puis relance). Au tout premier lancement, sans `reglages.json`, le
  parcours par défaut est `be_c`.
- **Ouvrir le dossier du contenu** : ouvre l'Explorateur sur `contenu\<parcours courant>`,
  pratique pour éditer à la main les `enonce.md`, `starter.c`, `corrige.c`.
- **Emplacements et diagnostic…** : version fenêtre de l'ancien `diagnostic.bat`. Montre
  les chemins clés (appli, contenu, progression, w64devkit) et l'état présent/absent de
  `gcc`, `clangd`, `claude`, chacun avec un bouton « Ouvrir le dossier ».

`reglages.json` est **local et git-ignoré**, comme `auteur.json`.

### Le compilateur gcc (w64devkit)

Compiler un exercice a besoin de `gcc`. Sur ce poste, le compilateur portable
**w64devkit 2.8.0** (gcc 16.1) est extrait dans `w64devkit\` à la racine (git-ignoré).
`Atelier.bat` l'ajoute au PATH au démarrage. Pour l'installer ailleurs : télécharger
`w64devkit-x64-2.8.0.7z.exe` depuis les releases skeeto/w64devkit et l'extraire à la
racine du dépôt de sorte à obtenir `w64devkit\bin\gcc.exe`.

## Où c'est dans le code

| Fichier                        | Rôle                                                   |
|--------------------------------|--------------------------------------------------------|
| `gestion_niveaux.py`           | Logique pure sur les fichiers (ajout, retrait, ordre)  |
| `auteur.py`                    | Porte du mot de passe (empreinte, vérification)        |
| `reglages.py`                  | Dernier parcours retenu (`reglages.json`)              |
| `diagnostic.py`                | Parcours détectés, chemins clés, présence des outils   |
| `dialogue_niveaux.py`          | Les fenêtres PyQt6 (gestionnaire + formulaire d'ajout) |
| `dialogue_diagnostic.py`       | La fenêtre Emplacements et diagnostic                  |
| `fenetre.py`                   | Menu Paramètres et branchement                         |
| `atelier_snake.py`             | Choix du parcours : `--parcours` sinon `reglages.json` |
| `Atelier.bat`                  | Lanceur double-clic (détection Python + gcc portable)  |
| `tests/test_gestion_niveaux.py`| Tests de la logique de niveaux et du mot de passe      |
| `tests/test_reglages.py`       | Tests du dernier parcours retenu                       |
| `tests/test_diagnostic.py`     | Tests des parcours détectés et des chemins clés        |

La logique (`gestion_niveaux.py`, `auteur.py`) ne dépend pas de PyQt : elle se teste
sans écran. `dialogue_niveaux.py` n'est qu'une couche mince au-dessus.

## Lancer les tests

```
python -m unittest tests.test_gestion_niveaux tests.test_reglages tests.test_diagnostic
```

Pour un tour complet des portes (compilation réelle), il faut `gcc` au PATH, ce que fait
`Atelier.bat`. Les tests du parcours projet (Snake) exigent SDL3 et restent hors
périmètre sur Windows.

## Note pour la coordination Linux / Windows

- Fichiers **communs** (format des niveaux, `parcours.json`, `meta.json`) : inchangés.
  L'outil GUI écrit exactement la même forme que ce que le Claude Linux écrit à la main
  (JSON indenté à 2 espaces, accents conservés, saut de ligne final).
- Fichiers **nouveaux, propres à Windows** : `gestion_niveaux.py`, `auteur.py`,
  `reglages.py`, `diagnostic.py`, `dialogue_niveaux.py`, `dialogue_diagnostic.py`,
  `Atelier.bat`, `tests/test_gestion_niveaux.py`, `tests/test_reglages.py`,
  `tests/test_diagnostic.py`, ce document.
- `auteur.json`, `reglages.json` et le dossier `w64devkit\` ne doivent **pas** être
  commités (déjà dans `.gitignore`).
- Le packaging portable doit embarquer les modules frères au même niveau que
  `fenetre.py`, comme `executeur` et `chemins`.
