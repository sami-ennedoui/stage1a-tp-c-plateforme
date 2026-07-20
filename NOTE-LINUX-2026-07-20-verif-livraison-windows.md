# Note Linux → Windows, 2026-07-20 : vérification de `livraison-windows`

Nouveau partage des rôles, décidé par Sami : **le poste Windows est désormais la plateforme
principale de développement.** Le poste Linux ne produit plus de code produit, il documente et
il vérifie. Cette note est donc un rapport de vérification, pas une demande de changement de
cap. Tu décides quoi en faire.

## Ce que ton travail apporte, et qui est solide

Le build tourne enfin en entier et produit un livrable vérifié sur un PATH réduit à `system32`.
C'était le jalon qui manquait depuis le début. Les deux défauts que tu ne pouvais voir qu'en
construisant sont réels et bien diagnostiqués : le `QThread` de `ClientClangd` qui ne crashait
pas tant que clangd était absent de la machine de build, et les journaux de session écrits dans
le bundle qu'on s'apprêtait à zipper, qui rendaient le livrable non reproductible.

Et tu corriges toi-même un chiffre de ta note précédente, 93 vers 156 Mo, qui était faux. Le
vrai poids est 721 Mo de bundle pour 213 Mo de zip, dont 567 Mo de w64devkit. Ta conclusion est
juste et elle change la priorité : **le poids vient du compilateur, pas du serveur de langage.**

## Mais la fusion a résolu six fichiers d'un seul côté, et c'est mesuré

`livraison-windows` est bien la vraie fusion : `moodle-sur-release` d'un côté, ton
`windows-clangd-embarque` de l'autre, qui porte `version-projet` jusqu'à `396284b`. Il ne lui
manque que mes deux derniers commits.

Pour les fichiers en conflit, la résolution a gardé `moodle-sur-release` :

| fichier | `version-projet` | `livraison-windows` | effet |
|---|---|---|---|
| `moodle_sync.py` | 163 lignes | 108 | perd `desaccord_url`, `signaler_deja_faits`, `dernier_score`, `etapes_faites` |
| `tests/test_moodle_sync.py` | 270 lignes, 20 tests | 114 lignes, **7 tests** | 13 tests disparaissent |
| `fenetre.py` | 577 lignes | 678 | garde ton tuteur, perd le mode auteur |

Sur `fenetre.py` ce n'est pas une perte sèche, c'est un échange. Tu gagnes `journal_session`,
l'historique du tuteur et le multi-moteur. Tu perds le câblage du mode auteur :
`dialogue_niveaux` passe de 2 références à **0**. Les fichiers `gestion_niveaux.py`,
`dialogue_niveaux.py`, `auteur.py` et `reglages.py` sont toujours là, mais **plus rien ne les
ouvre**. Ta propre GUI de gestion des niveaux, et ta `synchroniser_notation`, sont
inaccessibles depuis la fenêtre.

Ta reprise multi-poste `d8b62a4` est partie aussi : `appairer` est revenu à
`tuple[bool, str]`. C'est cohérent avec le `fenetre.py` retenu, qui déballe deux valeurs, donc
pas de plantage. Mais la fonction n'existe plus.

## Le défaut qui compte, parce qu'il est silencieux

`chemins.py` a gardé **notre** côté, donc il déclare toujours `ATELIER_SUIVI` avec `"local"`
par défaut. `moodle_sync.py` a gardé **le vôtre**, qui n'a jamais connu ce mode et ne le teste
nulle part, zéro garde contre trois. La fusion est donc incohérente avec elle-même : elle
annonce un mode qu'elle n'applique plus.

Vérifié en exécutant ta branche, pas en la lisant :

```
mode declare par chemins : local
appels reseau en mode LOCAL, jeton present : 1
URL contactee : https://exemple.test/api/evenements
```

Un poste réglé sur `local` envoie donc quand même. Comme le défaut est maintenant `local` et
que Sami a décidé que le produit ne parle à aucun serveur, c'est le contraire de ce qui est
promis. Sans appairage rien ne part, donc l'étudiant type n'est pas touché, mais la garantie
n'existe plus.

## Pourquoi la suite est verte quand même, et c'est le vrai enseignement

**175 tests passent sur ta branche.** Plus que sur `version-projet`. La suite ne voit rien.

La raison mérite d'être retenue pour la suite du projet : **la même résolution a emporté le
module et ses tests.** Les 13 tests qui auraient crié sont partis avec le code qu'ils
gardaient. Une suite verte prouve seulement que ce qui reste est cohérent avec ce qui reste.

C'est exactement ce que la vérification côté Linux peut attraper et pas la tienne, puisque ta
machine te dit vert. C'est aussi pourquoi je te l'écris au lieu de le corriger.

## Comment refaire la résolution

Pour les deux `add/add`, la réponse est mécanique et déjà prouvée. Le fichier de
`moodle-sur-release` est **notre fichier copié le 9 juillet**, identité de blob à l'appui :

```
moodle-sur-release:moodle_sync.py            = d0433eb = version-projet @ b420b75
moodle-sur-release:tests/test_moodle_sync.py = 84f6512 = version-projet @ 80953ce
```

Il n'a jamais été retouché depuis, un seul commit. Donc :

```
git checkout --ours moodle_sync.py tests/test_moodle_sync.py
```

Aucun de vos 7 tests ne manque à nos 20. Rien ne se perd.

**`fenetre.py` est le seul qui demande un vrai travail à la main**, parce que les deux côtés y
ont écrit. Ni `--ours` ni `--theirs` ne conviennent. Il faut reprendre ta version actuelle et y
remettre le câblage du mode auteur, c'est-à-dire ce qui ouvre `dialogue_niveaux`, plus
`auteur.py` et `reglages.py`. Si tu remets aussi `d8b62a4`, alors `appairer` reprend trois
valeurs et la ligne d'appel doit suivre. Sinon, laisse les deux à deux valeurs, en cohérence.

Un repère pour vérifier ta résolution sans lancer la GUI :

```
git show <ta-resolution>:fenetre.py | grep -c dialogue_niveaux   # doit valoir 2, pas 0
git show <ta-resolution>:moodle_sync.py | grep -c ATELIER_SUIVI  # doit valoir 3, pas 0
```

## Deux choses de mon côté

Il te manque mes deux derniers commits de `version-projet`, `b4202ce` et `9525eb6`. Le premier
est le garde-fou d'encodage que tu réclamais. Il signale que ta correction de
`dialogue_diagnostic.py` ajoute `creationflags` mais pas `encoding`.

Et **l'horloge de ta VM est fausse**. Tes commits portent le fuseau `-07:00` alors que ton
horloge murale affiche l'heure de Paris, donc ils sont datés d'environ sept heures dans le
futur. Tes 38 commits antérieurs sont en `+02:00`, c'est apparu avec la VM, dont Windows met le
fuseau sur Pacifique par défaut. Ça ne casse rien dans git, qui raisonne par topologie, mais
tout classement par date entre nos deux postes est faux, et la date du document de reprise le
sera aussi. Une minute à régler dans la VM.
