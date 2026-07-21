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

## Ajouter un parcours

Un **parcours** (un ensemble d'exercices, par exemple les 14 du BE C) s'ajoute **sans
toucher au code** : il suffit de déposer un dossier dans `contenu/`. Aucune inscription,
aucun enregistrement : la découverte est automatique.

### Règle de découverte

`diagnostic.parcours_disponibles()` liste **tout sous-dossier de `contenu/` qui contient
un `parcours.json`** (et rien d'autre : un dossier sans ce fichier est ignoré). C'est
exactement ce que propose le menu **Paramètres → Changer de parcours…**
(`fenetre._changer_parcours`).

### Le fichier `parcours.json`

Lu par `modele_etape.charger_parcours_complet`. Deux clés :

| Clé     | Type  | Sens                                                                    |
|---------|-------|-------------------------------------------------------------------------|
| `ordre` | liste | Noms des dossiers d'étapes, dans l'ordre d'affichage                     |
| `mode`  | texte | `"isole"` (exercices indépendants) ou `"projet"` ; défaut `"isole"`      |
| `libre` | booléen | Optionnel, défaut `false`. À `true`, toutes les étapes sont ouvertes d'emblée, sans franchir les portes précédentes (`Parcours.libre`, testé dans `fenetre.py` : `if self.mode == "projet" or self.libre or self.tout_debloque`). Utile pour un parcours de révision sur le même contenu qu'un parcours étanche. |

Exemple minimal complet (parcours isolé d'un seul exercice) :

```json
{
  "ordre": ["ex01_intro"],
  "mode": "isole"
}
```

### Les étapes

Chaque nom cité dans `ordre` est un sous-dossier d'étape, au **format commun décrit plus
haut** (« Ce qu'est un niveau » : `meta.json` + `enonce.md` + `starter.c` + `corrige.c`,
`approfondissement.md` optionnel ; les champs de `meta.json` figurent dans le tableau
ci-dessus). Le plus simple pour démarrer est de copier une étape existante de `be_c`
(par exemple `contenu/be_c/ex01_types/`) et de l'adapter, ou d'utiliser l'outil d'auteur
(**Gérer les niveaux… → Ajouter**), qui crée le dossier et l'insère dans `ordre`.

### Où poser le dossier : source vs paquet livré

`chemins.RACINE = Path(__file__).resolve().parent`, et
`chemins.contenu_racine(nom) = RACINE/"contenu"/nom`.

- **Dépôt / checkout source** : `<repo>\contenu\<nom>\`.
- **Exe PyInstaller livré** : les modules Python vivent dans `_internal\`, donc le contenu
  est à `TP-C-perso\_internal\contenu\<nom>\`. Un enseignant qui ajoute un parcours au
  produit livré dépose son dossier là.

### Sélection et effet au lancement

`Changer de parcours…` mémorise le choix dans `reglages.json` via
`reglages.definir_parcours` (`reglages.json` est **local et git-ignoré**). Le parcours
d'ouverture est résolu par `atelier_snake._parcours_choisi()` : **priorité à l'argument
`--parcours`, sinon `reglages.dernier_parcours()`** (défaut `be_c`, `reglages.PARCOURS_DEFAUT`).

Conséquence importante selon le lanceur :

- **Depuis les sources** (`Atelier.bat`, qui lance `atelier_snake.py` **sans** `--parcours`) :
  le choix du menu est bien pris en compte **au prochain lancement**. C'est le cas nominal.
- **Depuis l'exe livré** : le point d'entrée `packaging/entree_be_c.py` **force
  `--parcours be_c`** quand aucun `--parcours` n'est passé, et `lancer.bat` passe déjà
  `--parcours be_c`. Comme `--parcours` est prioritaire sur `reglages.json`, le choix
  mémorisé par le menu **n'a pas d'effet** dans le paquet livré : l'exe ouvre toujours
  `be_c`. Pour ouvrir un autre parcours dans le livrable, il faut **éditer `lancer.bat`**
  et remplacer `--parcours be_c` par `--parcours <nom>` (l'argument, non `be_c`, est alors
  respecté par `entree_be_c.py`).

### Empaqueter un nouveau parcours

Le build ne bundle **que `be_c`** : voir `packaging/build_windows.ps1`, ligne
`--add-data "$Repo\contenu\be_c;contenu/be_c"`. Un nouveau parcours n'est donc pas dans
l'exe livré tant que l'une des deux choses n'est pas faite :

- **le copier après coup** dans `TP-C-perso\_internal\contenu\<nom>\` du livrable, ou
- **étendre le packaging** : ajouter une ligne `--add-data "$Repo\contenu\<nom>;contenu/<nom>"`
  dans `packaging/build_windows.ps1` pour l'embarquer au build.

> Rappel notation : un seul parcours est noté par le compagnon (`be_c` par défaut). Ajouter
> un parcours ne le rend pas noté ; voir « Parcours noté et redéploiement du compagnon ».

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

## Parcours noté et redéploiement du compagnon

Un seul parcours est **noté** dans Moodle, `be_c` par défaut. Le compagnon en ligne ne
voit jamais `contenu/` (son image Docker ne copie que `compagnon/`) : il note d'après une
liste séparée, `compagnon/etapes_notees.json`, qui redit l'ordre du parcours noté. Les
deux doivent rester d'accord, sinon les notes de toute la promotion deviennent fausses,
en silence. Exemple : retirer un niveau de `be_c` sans mettre la liste à jour plafonne
tout le monde à 13/14, pour toujours.

L'outil s'en charge. Dès qu'un **Ajouter**, **Retirer**, **Monter/Descendre** ou
**Détachés…** touche le parcours noté, la GUI réaligne `etapes_notees.json` sur le nouvel
ordre et affiche un rappel :

> « be_c » est le parcours noté par le compagnon. Sa liste d'étapes notées a été
> réalignée. **Le compagnon doit être redéployé** pour que les notes en tiennent compte.

Éditer le contenu ne suffit donc pas : le seul geste qui reste manuel est le
**redéploiement du service compagnon**. Tant qu'il n'est pas fait, la version en ligne
note encore sur l'ancienne liste.

Sur un poste étudiant, `compagnon/` est absent du bundle : la GUI ne fait alors rien, sans
erreur. La ligne de commande fait le même travail via `python atelier_contenu.py notation`,
et `tests/test_etapes_notees.py` refuse que les deux listes divergent.

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
- **Tout débloquer (mode enseignant)** : case à cocher qui ouvre toutes les étapes et les
  quatre crans du tuteur d'un coup, comme en mode démo. L'**activation exige le mot de
  passe auteur** ; la décocher (retour au parcours progressif) n'en demande pas. Le réglage
  est mémorisé dans `reglages.json` (clé `tout_debloque`) et **survit au relancement**.
  Point clé : il ne touche **pas** la progression réelle — il lève seulement le verrou à
  l'affichage (`fenetre._remplir_liste` / `_cran_dispo`). Aucune étape n'est faussement
  marquée « faite », donc rien de faux ne part vers Moodle. En parcours projet l'entrée est
  grisée (tout y est déjà ouvert). Réglage : `reglages.tout_debloque` /
  `definir_tout_debloque` ; bascule : `fenetre._basculer_tout_debloque`.

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
| `gestion_niveaux.py`           | Logique pure sur les fichiers (ajout, retrait, ordre) et suivi de la notation |
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
