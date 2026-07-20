# Reprendre ce projet

Pour la personne qui hérite du code. Écrit le 2026-07-20, à la fin du stage de Sami Ennedoui.

Ce document répond à quatre questions : ce que le projet est, comment le reconstruire, comment
le modifier, et ce qui ne va pas encore. Il dit aussi **pourquoi** certaines choses sont faites
d'une façon qui paraît étrange. Ces raisons sont ce qui se perd le plus vite.

---

## 1. Ce que c'est

Un atelier de programmation C pour les étudiants de 2A, distribué sous forme d'un exécutable
Windows. L'étudiant lit un énoncé, écrit son code dans la fenêtre, clique **Compiler** pour
voir la sortie, puis **Tester** pour franchir la « porte » de l'exercice. Une porte franchie
débloque la suite. Un tuteur IA optionnel répond à ses questions sans lui donner la solution.

Il y a trois morceaux, et un seul est indispensable.

**Le client**, en Python et PyQt6. C'est le produit. Il embarque son propre compilateur, gcc
via w64devkit, et son propre serveur de langage, clangd. L'étudiant n'installe rien d'autre.

**Le contenu**, dans `contenu/`. Des dossiers de texte et de C, sans code d'application. On
ajoute un exercice sans toucher au programme, c'est le point important de la conception.

**Le compagnon**, dans `compagnon/`. Un petit serveur Flask qui remonte les notes vers Moodle
par LTI 1.3. **Il n'est plus qu'une démonstration**, voir la section 5.

### L'état au 2026-07-20

Le produit est la **version Windows**. La version Linux a servi au développement et n'est plus
la cible. Le suivi est **local par défaut**, le client ne contacte aucun serveur tant que
personne ne le lui demande.

**La fusion des deux branches historiques n'est pas terminée.** Voir la section 6, c'est la
première chose à finir.

---

## 2. Reconstruire le livrable

Sur une machine Windows, depuis la racine du dépôt :

```powershell
powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1 -Zip
```

Le script télécharge ce qui manque, w64devkit pour gcc et clangd pour le serveur de langage,
construit l'exécutable avec PyInstaller et assemble le bundle. **Sans `-Zip` il s'arrête avant
l'archive**, ce qui est pratique pour essayer sans attendre. Il ne modifie rien hors du dépôt
et ses sorties sont ignorées par git.

Ordres de grandeur mesurés le 2026-07-20 : **bundle 721 Mo, zip 213 Mo**, dont 567 Mo pour
w64devkit et 63 Mo pour clangd. Le poids vient du compilateur, pas du reste. Si quelqu'un
attaque la taille un jour, c'est là qu'il faut chercher, et nulle part ailleurs.

**Vérifier le livrable, pas le dépôt.** Déballez le zip ailleurs, sur une machine où ni gcc, ni
clangd, ni Python ne sont visibles, et lancez `diagnostic.bat`. C'est la seule façon de voir un
outil qui manque. Sur la machine de développement tout marche toujours, y compris ce qui n'est
pas dans le paquet, et c'est ainsi qu'un serveur de langage absent est passé inaperçu pendant
une semaine.

---

## 3. Où vivent les choses

| chemin | rôle |
|---|---|
| `atelier_snake.py` | point d'entrée, options de ligne de commande |
| `fenetre.py` | toute l'interface graphique |
| `executeur.py` | compile, exécute, et juge les portes |
| `modele_etape.py` | lit `contenu/` et construit les objets `Etape` |
| `progression.py` | ce que l'étudiant a fait, et ce qui est déverrouillé |
| `chemins.py` | chemins, drapeaux de compilation, variables d'environnement |
| `tuteur_ia.py` | prompts, filtre anti-solution, appel du moteur |
| `lsp_clangd.py` | client LSP, autocomplétion et erreurs en direct |
| `moodle_sync.py` | file d'attente et envoi vers le compagnon |
| `gestion_niveaux.py` | ajout et retrait d'étapes, sans interface |
| `dialogue_niveaux.py` | le mode auteur dans la fenêtre |
| `atelier_contenu.py` | le même travail en ligne de commande |
| `contenu/<parcours>/` | les exercices |
| `compagnon/` | le serveur LTI, indépendant du client |
| `packaging/` | scripts de construction et lanceurs |

### Les fichiers locaux de l'étudiant

Écrits à côté de l'exécutable, tous ignorés par git : `progression.json` pour l'avancement,
`moodle_sync.json` pour l'appairage, `reglages.json` pour les préférences, `auteur.json` pour
l'empreinte du mot de passe du mode auteur, `releve.txt` pour le relevé.

**Un point à trancher si le produit est un jour installé dans `C:\Program Files`** : ces
fichiers sont écrits à côté de l'exécutable, ce qui y sera refusé. `%APPDATA%` serait le bon
endroit sous Windows, au prix de l'usage nomade sur clé USB. Le choix actuel favorise la clé
USB. Ce n'est pas un oubli.

---

## 4. Ajouter ou modifier un exercice

Deux chemins, le même résultat. En ligne de commande :

```
python3 atelier_contenu.py lister
python3 atelier_contenu.py nouvelle-etape be_c ex15_matrices --titre "Exercice 15, les matrices"
python3 atelier_contenu.py verifier be_c
```

Ou par le mode auteur de la fenêtre, protégé par mot de passe.

Une étape est un dossier avec un `meta.json`, un `enonce.md`, un `starter.c` et un `corrige.c`.
Le `meta.json` décide comment la porte juge. Les champs qui comptent :

| champ | effet |
|---|---|
| `mode` | `programme`, `test_fourni`, ou `test_a_ecrire` |
| `entree` | ce qui est envoyé sur l'entrée standard |
| `sortie_attendue` | les fragments cherchés dans la sortie |
| `cran_debloque` | le niveau d'aide du tuteur que cette étape ouvre |
| `fichier_edite` | le nom du fichier que l'étudiant écrit |

**Lancez toujours `atelier_contenu.py verifier` après.** Il compile les corrigés contre les
portes et attrape les incohérences avant l'étudiant.

### Deux règles qui ne se devinent pas

**Un identifiant d'étape doit être unique dans tout `contenu/`, pas seulement dans son
parcours.** Le compagnon ne reçoit que l'identifiant, jamais le nom du parcours. Deux étapes
homonymes sont donc le même exercice pour lui, et il noterait l'une pour l'autre. Les deux
outils refusent déjà les homonymes, et un test bloque la construction si un homonyme entre
malgré tout. Ne désactivez pas cette garde en simplifiant.

**Si vous changez `contenu/be_c`, réalignez la liste notée** avec
`python3 atelier_contenu.py notation`. Un test le vérifie. La raison est en section 5.

---

## 5. Le compagnon Moodle : une démonstration, pas une dépendance

Le compagnon reçoit les portes franchies et pousse une note dans le carnet Moodle par LTI 1.3.
La chaîne a été prouvée de bout en bout en juillet 2026. **Elle ne doit plus servir en
production**, pour une raison simple : le service tourne sur un compte Render personnel, avec
des identifiants personnels. Une école ne peut pas dépendre de ça.

Le mode de suivi se règle par `ATELIER_SUIVI`, qui vaut `local` par défaut. En local, aucun
appel réseau n'est fait, même si un appairage traîne sur le disque. Pour la démonstration,
mettez `ATELIER_SUIVI=moodle`.

Si quelqu'un veut remettre la note automatique en service, il faut reprendre le déploiement à
son compte, et l'établissement devra déclarer l'outil LTI, ce que Sami ne pouvait pas faire
faute d'être administrateur Moodle.

**Deux pièges du compagnon, mesurés.** L'image Docker ne copie que `compagnon/`, donc le
serveur **ne voit jamais `contenu/`** ; c'est pourquoi `compagnon/etapes_notees.json` répète la
liste des étapes notées et doit être réaligné à la main. Et un redéploiement Render **efface la
base**, donc tous les appairages ; les clés RSA survivent car elles vivent en variables
d'environnement, donc l'identité LTI ne change pas.

---

## 6. Ce qui ne va pas encore

Par ordre d'importance. Ce sont des faits mesurés, pas des impressions.

### La fusion des branches n'est pas finie

Le projet a vécu sur deux branches qui ont divergé le 3 juillet, et **aucune des deux n'est
complète** : l'une a le packaging et le tuteur multi-moteur, l'autre a le compagnon, le mode
auteur et la notation. La branche `livraison-windows` les réunit, mais sa résolution a gardé un
seul côté sur les fichiers en conflit, ce qui a fait disparaître treize tests, quatre fonctions
de `moodle_sync.py`, et le câblage du mode auteur dans la fenêtre.

Symptôme visible : la fenêtre n'ouvre plus le mode auteur, et `ATELIER_SUIVI=local` n'empêche
plus les envois. Deux contrôles rapides :

```
grep -c dialogue_niveaux fenetre.py    # doit valoir 2
grep -c ATELIER_SUIVI moodle_sync.py   # doit valoir 3
```

**C'est la première chose à finir.** Le détail est dans
`NOTE-LINUX-2026-07-20-verif-livraison-windows.md`.

### La porte du parcours noté ne vérifie pas le code

`porte_programme` juge **la sortie standard, et jamais le code**. Un programme qui affiche les
bonnes lignes sans rien calculer franchit la porte. Testé sur les quatorze exercices de `be_c`,
**quatorze sur quatorze tombent**. Le message d'échec donne en plus les lignes à copier :

```c
int main(void) { printf("short : 12\nint : 260\nchar : A\n...\n"); return 0; }
```

Décision prise, pas encore faite : **deux parcours**, un à porte étanche pour la note, un libre
pour s'entraîner. La piste retenue est de tester chaque exercice avec **plusieurs jeux
d'entrées**, ce qu'un affichage figé ne peut pas satisfaire. Ça demande un champ `cas` dans les
`meta.json` et une boucle dans `porte_programme`.

Deux défauts liés, plus petits. La comparaison se fait en sous-chaîne, donc `short : 120` est
accepté quand on attend `short : 12`, alors qu'une valeur trop courte est refusée. Et
**plusieurs énoncés demandent `scanf` alors que le champ `entree` est vide**, ce qui rend
l'exercice impossible à réussir en suivant la consigne. Les quatorze énoncés sont à relire.

### Le poids du livrable

213 Mo de zip, dont 567 Mo de w64devkit décompressé. Acceptable, mais c'est le premier chiffre
qu'on vous reprochera.

### Le fichier de progression est modifiable au Bloc-notes

`progression.json` est du JSON lisible. Il était prévu de le rendre compact et signé.
**Dites-le honnêtement si vous le faites** : la clé voyagera dans l'exécutable, donc ce sera de
l'obfuscation et pas de la sécurité. Ça empêche l'édition opportuniste, rien de plus.

---

## 7. Pièges connus, qui coûteront du temps à qui les ignore

**Le bug d'accents revient.** `subprocess.run(..., text=True)` sans `encoding` décode dans
l'encodage local, UTF-8 sous Linux et cp1252 sous Windows français. gcc écrit en UTF-8, donc
l'étudiant lit « fenÃªtre ». Il est réapparu trois fois, parce que le poste qui écrit la faute
ne peut pas la voir. `tests/test_encodage_subprocess.py` l'interdit maintenant. Ne le
désactivez pas, ajoutez `encoding="utf-8"`.

**Les fenêtres de console sous Windows coûtent cher.** Tout `subprocess` doit recevoir
`creationflags=chemins.SANS_FENETRE`. Ce n'est pas cosmétique : mesuré, ça divise le temps de
compilation par 2,4 et supprime une variance de 600 ms. Attention en mesurant, depuis un parent
qui possède déjà une console le drapeau semble inutile ; il faut mesurer sans console, comme
l'application réelle.

**SmartScreen bloque l'exécutable.** Il n'est pas signé, donc Windows affiche « Windows a
protégé votre ordinateur ». Beaucoup d'étudiants s'arrêteront là en croyant à un virus. La
parade est documentée dans le guide de l'étudiant. Signer coûte de l'argent.

**Les tests qui lancent un sous-processus doivent poser la racine dans `sys.path`.** Compter
sur le dossier courant marche avec un Python ordinaire et échoue avec un Python embarqué, celui
du bundle.

**Les deux postes commitent sous le même nom.** N'attribuez jamais un commit à une machine
d'après son auteur git. Ce sont les fichiers `NOTE-LINUX-*.md` et `NOTE-WINDOWS-*.md` qui
racontent qui a fait quoi et pourquoi.

---

## 8. Comment lire l'historique

Le projet a été développé par deux postes, Linux et Windows, qui se répondaient **par commits
et par notes**, jamais par messagerie. Les fichiers `NOTE-LINUX-*.md` et `NOTE-WINDOWS-*.md` à
la racine sont cette conversation. Ils contiennent le raisonnement derrière les décisions, les
mesures, et les erreurs reconnues.

Ils ont fait leur travail et n'ont plus d'intérêt opérationnel. **Rangez-les dans
`historique/`** plutôt que de les supprimer : quand vous vous demanderez pourquoi une chose est
faite d'une certaine façon, la réponse y est presque toujours.

Même chose pour les fichiers `PLAN-*.md`, `SPEC-*.md` et `BRIEFING-*.md`, qui décrivent des
intentions parfois abandonnées. **Ne les lisez pas comme une description de l'existant.**
