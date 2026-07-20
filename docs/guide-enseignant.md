# L'atelier C, guide de l'enseignant

Comment distribuer l'atelier, écrire des exercices, et récupérer l'avancement des étudiants.

Ce guide décrit **ce que le programme fait réellement**, y compris ses limites. Elles sont
énoncées franchement, parce qu'une limite connue se contourne et qu'une limite ignorée fausse
une note.

---

## 1. Distribuer

Vous donnez aux étudiants un fichier zip d'environ **213 Mo**. Il contient tout, y compris le
compilateur et le serveur de langage, donc rien ne s'installe sur les machines.

L'étudiant décompresse et double-clique `lancer.bat`. Il n'a besoin d'aucun droit
d'administrateur.

**Prévenez-les de l'avertissement SmartScreen.** L'exécutable n'est pas signé, une signature de
code étant payante, donc Windows affiche « Windows a protégé votre ordinateur » au premier
lancement. La parade est « Informations complémentaires » puis « Exécuter quand même ». Sans
cet avertissement préalable, une partie de la promotion croira à un virus et abandonnera.

En cas de problème sur un poste, `diagnostic.bat` affiche ce que l'atelier trouve. C'est le
premier réflexe à leur donner.

---

## 2. Le contenu est une donnée, pas du code

Un **parcours** est une suite d'**étapes**. Une étape est un dossier de fichiers texte. On
ajoute ou modifie un exercice **sans toucher au programme**, c'est le principe de conception
qui compte le plus ici.

```
contenu/be_c/
  parcours.json          l'ordre des étapes
  ex01_types/
    meta.json            comment la porte juge
    enonce.md            ce que l'étudiant lit
    starter.c            le code de départ
    corrige.c            la solution de référence
```

Les parcours livrés aujourd'hui : **`be_c`**, les 14 exercices du BE, c'est celui qui compte ;
`tp_c`, `bonus_pointeurs`, `perso`, `hybride` et `projet` sont des restes de développement.

---

## 3. Ajouter ou modifier un exercice

Par la fenêtre, en mode auteur, protégé par mot de passe. Ou en ligne de commande :

```
python3 atelier_contenu.py lister
python3 atelier_contenu.py nouvelle-etape be_c ex15_matrices --titre "Exercice 15, les matrices"
python3 atelier_contenu.py verifier be_c
```

**Lancez toujours `verifier` après une modification.** Il compile chaque corrigé contre sa
porte et vous dit lequel ne passe plus. C'est le seul filet avant l'étudiant.

**La règle d'or : le corrigé doit franchir la porte, le starter non.** Si le starter passe,
l'exercice se valide sans rien faire. Si le corrigé échoue, personne ne pourra le franchir.

### Les champs de `meta.json`

| champ | à quoi il sert |
|---|---|
| `id` | l'identifiant, unique dans **tout** `contenu/` |
| `titre` | affiché dans la liste |
| `mode` | `programme`, `test_fourni` ou `test_a_ecrire` |
| `sortie_attendue` | les fragments cherchés dans la sortie, en mode `programme` |
| `entree` | ce qui est envoyé sur l'entrée standard du programme |
| `cran_debloque` | le niveau d'aide du tuteur que franchir cette étape ouvre |
| `fichier_edite` | le nom du fichier écrit par l'étudiant |
| `type` | `jalon` fait apparaître le bouton qui lance le jeu |
| `noeud_cours`, `recette` | notes libres, **le programme ne les lit pas** |

### Quatre choses qui surprennent

**`fichier_edite` est ignoré en mode `programme` et en mode `test_fourni`.** Le fichier est
alors nommé en dur, `programme.c` ou `soumission.c`. Il ne compte vraiment qu'en mode
`test_a_ecrire` et dans le parcours projet. Comme les 14 exercices de `be_c` sont en mode
`programme`, ce champ n'y sert à rien, malgré les apparences.

**`noeud_cours` n'est affiché nulle part.** Les outils l'écrivent, le programme le charge, et
personne ne l'utilise. C'est un commentaire pour vous.

**Un identifiant doit être unique dans tout `contenu/`, pas seulement dans son parcours.** Le
suivi ne transporte que l'identifiant, jamais le nom du parcours, donc deux étapes homonymes
seraient le même exercice. Les outils refusent déjà les homonymes, et un test bloque si un
homonyme entre par une autre porte.

**Retirer une étape sans `--effacer` laisse son dossier sur le disque.** Elle devient
« détachée » : invisible pour l'étudiant, réattachable plus tard. Son identifiant reste donc
pris, ce qui est voulu.

---

## 4. Comment la porte juge, et ce qu'elle ne voit pas

Trois modes, du plus permissif au plus strict.

**`programme`** compile le programme de l'étudiant, lui envoie `entree` sur l'entrée standard,
et vérifie que chaque fragment de `sortie_attendue` **apparaît** dans ce qu'il affiche. La
comparaison est une recherche de texte, tolérante sur ce qu'il y a autour, intransigeante sur
l'orthographe et les espaces.

**`test_fourni`** compile le code de l'étudiant avec un `tests.c` que vous écrivez. Le code de
retour décide.

**`test_a_ecrire`** est le plus intéressant. L'étudiant écrit son code **et** son test. Le test
est d'abord jugé : il doit passer contre `corrige.c` et échouer contre `corrige_buggue.c`. Un
test qui ne fait pas les deux est refusé, et l'étudiant est renvoyé à son test avant même de
parler de son code.

### La limite qu'il faut connaître avant de noter

**En mode `programme`, la porte regarde la sortie et jamais le code.** Un programme qui affiche
les bonnes lignes sans rien calculer franchit la porte :

```c
int main(void) { printf("short : 12\nint : 260\nchar : A\n...\n"); return 0; }
```

Vérifié sur les 14 exercices de `be_c` : **les 14 se franchissent ainsi**. Et le message
d'échec affiche les fragments manquants, donc il donne les lignes à copier.

Ce n'est pas un accident, c'est ce que ce mode sait faire. Conséquence pratique : **le nombre
d'étapes validées mesure l'avancement, pas la compétence.** Ne le transformez pas en note sans
regarder le code. Un correctif est prévu, qui testera chaque exercice avec plusieurs jeux
d'entrées, ce qu'un affichage figé ne peut pas satisfaire.

Deux défauts plus petits, en attendant. `short : 120` est accepté là où l'on attend
`short : 12`, parce que l'un contient l'autre. Et **plusieurs énoncés demandent `scanf` alors
que le champ `entree` est vide** : l'exercice devient alors impossible à réussir en suivant la
consigne, puisque toute lecture échoue. Si un étudiant se plaint d'un exercice infaisable,
c'est la première chose à regarder.

---

## 5. Récupérer l'avancement

Par défaut, **l'atelier ne contacte aucun serveur**. La progression vit sur la machine de
l'étudiant.

Pour la relever, l'étudiant lance l'atelier avec l'option `--releve`, ou vous ajoutez un
raccourci qui le fait. Cela écrit un fichier `releve.txt` lisible :

```
Relevé de progression, Atelier TP C
Parcours : be_c
Étapes validées : 2 sur 14, soit 14.3 %

  [x] ex01_types            Exercice 1, les types de variables
  [ ] ex03_menu             Exercice 3, les structures de contrôle
  ...
Empreinte : 06582f9a
```

**L'empreinte détecte une modification accidentelle, pas une falsification.** L'algorithme est
dans le code que l'étudiant possède, donc quelqu'un de motivé la recalculera. C'est écrit dans
le code source lui-même, et c'est honnête.

Le fichier de progression est d'ailleurs du JSON lisible, modifiable au Bloc-notes. **Si
l'avancement compte pour une note, demandez le code, pas le relevé.**

---

## 6. Le tuteur IA

Optionnel. S'il n'est pas configuré, l'atelier fonctionne et le bouton d'aide se tait.

Il ne donne pas la solution, un filtre automatique masque les lignes de code qui ouvriraient la
porte. La limite connue est qu'une explication en prose pure peut encore trop en dire.

L'aide se précise à mesure que l'étudiant avance, chaque étape franchie pouvant ouvrir un cran
supplémentaire par le champ `cran_debloque`.

**Vous devez fournir vos propres accès.** L'atelier appelle un outil en ligne de commande
installé sur la machine, il n'embarque aucune clé. Prévoyez-le si vous voulez le tuteur en
salle machine, et sachez que ces outils sont généralement payants.

---

## 7. Le mot de passe du mode auteur

Il protège l'accès à l'édition des niveaux depuis la fenêtre. Il se résout dans cet ordre :
le fichier `auteur.json` s'il existe, sinon la variable d'environnement `ATELIER_AUTEUR_MDP`,
sinon une valeur par défaut.

**Cette valeur par défaut est le mot `auteur`, et elle est écrite dans le code source.**
Changez-la avant de distribuer, sinon elle ne protège de personne.

C'est une barrière contre la curiosité, pas contre un étudiant déterminé : tout est sur sa
machine.

---

## Annexe. La remontée automatique vers Moodle

Elle existe, elle a fonctionné, et **elle ne doit pas servir en production**.

Un petit serveur reçoit les portes franchies et pousse une note dans le carnet Moodle par
LTI 1.3. La chaîne a été prouvée de bout en bout en juillet 2026, l'étudiant s'appairant par un
code court obtenu en cliquant l'activité dans Moodle.

Deux raisons de ne pas s'y fier. Le service tourne sur un **compte personnel** d'hébergement,
avec des identifiants personnels ; l'établissement ne peut pas en dépendre. Et l'hébergement
gratuit s'endort : mesuré en juillet 2026, le service dormait quasiment en permanence, avec
**32,8 secondes de réveil** au premier appel, et sa base était effacée à chaque redéploiement,
donc tous les appairages avec elle.

Pour l'activer en démonstration, réglez `ATELIER_SUIVI=moodle`. Sans cela, l'atelier reste
local et le bouton de connexion n'apparaît même pas.

Remettre cette chaîne en service demanderait de reprendre le déploiement à son compte, et un
administrateur Moodle pour déclarer l'outil externe. Un compte enseignant seul n'y suffit pas,
c'est vérifié.
