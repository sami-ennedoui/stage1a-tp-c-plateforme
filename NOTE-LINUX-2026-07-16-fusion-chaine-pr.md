# Note Linux → Windows, 2026-07-16 : fermeture de la chaîne des PR

Pour le Claude Windows. On va fusionner `moodle-sur-release` dans `version-projet`, ce qui
ferme les PR #1 et #2 d'un coup. La fusion sort **7 conflits**. J'en ai résolu 4, ceux qui sont
à moi. Je te laisse les 3 fichiers d'appli, ils sont à toi et je n'y touche pas.

Rien n'est poussé pour l'instant. Sami tranche avant.

## Pourquoi une seule fusion et pas deux

`windows-packaging-tuteur-multimoteur` est **contenu en entier** dans `moodle-sur-release`,
vérifié avec `git merge-base --is-ancestor`. La PR #2 est un fast-forward. Fusionner
`moodle-sur-release` dans `version-projet` règle donc les deux PR en une fois. La PR #1 se
fermera toute seule, la #2 est à fermer à la main.

## Ce que j'ai résolu : mes 4 fichiers

Le protocole de `REPARTITION-TACHES.md` te donne les fichiers d'appli. Ces quatre-là n'en sont
pas, et tu n'y as jamais touché. Je les ai mesurés un par un.

| fichier | ce qui s'oppose | résolution |
|---|---|---|
| `chemins.py` | on a écrit **les mêmes lignes** des deux côtés, git ne se dispute que sur la place de `import os` | `version-projet`, il a `ATELIER_SUIVI` en plus |
| `moodle_sync.py` | add/add, 157 lignes contre 108 | `version-projet`, sur-ensemble vérifié ligne à ligne |
| `tests/test_moodle_sync.py` | add/add | `version-projet`, il a déjà tous tes tests |
| `.gitignore` | on ajoute chacun nos lignes | union, **je garde tes 3 lignes de build** |

Sur le `.gitignore`, tes lignes `/w64devkit/`, `/.build/` et `/_bundle/` restent. Ce sont les
sorties de `build_windows.ps1` et de `build_linux.sh`, sans elles le dépôt se salit au premier
build. Mon `.gitignore` ne les a pas, c'est moi qui suis en retard, pas toi.

## L'interface `moodle_sync` : 3 signatures sur 4 ne bougent pas

> **Corrigé le 2026-07-16 en fin de journée. La version d'origine de cette section disait les
> quatre signatures identiques et concluait « tu peux reprendre ta `fenetre.py` telle quelle,
> sans une seule ligne de changement ». C'était vrai à l'écriture, et faux deux heures plus
> tard : ton propre `d8b62a4` a changé `appairer`. Suivre ce conseil casserait l'appairage.
> Je laisse la trace plutôt que de réécrire l'histoire.**

Ta `fenetre.py` appelle quatre fonctions de `moodle_sync` : `actif`, `appairer`, `rejouer` et
`signaler_porte`. Trois sont **identiques** entre les deux branches, vérifiées une à une :
`actif`, `rejouer`, `signaler_porte`. Mon `moodle_sync.py` ajoute `desaccord_url`,
`signaler_deja_faits` et `dernier_score`, et ne retire rien.

**`appairer` a divergé, et c'est toi qui l'as fait bouger, pour de bonnes raisons.**

```
version-projet     : def appairer(...) -> tuple[bool, str, list]
moodle-sur-release : def appairer(...) -> tuple[bool, str]
```

Ta reprise multi-poste renvoie `etapes_faites` en troisième valeur. Les deux `fenetre.py`
déballent donc différemment :

```
version-projet     fenetre.py:389 : reussi, message, deja_faits = moodle_sync.appairer(...)
moodle-sur-release fenetre.py:274 : reussi, message              = moodle_sync.appairer(...)
```

C'est un piège pour la résolution de `fenetre.py`, qui te revient. Si tu gardes la ligne de
`moodle-sur-release`, le premier appairage lève `ValueError: too many values to unpack`, et
seulement à cet instant, chez l'étudiant, pas chez toi. Garde la ligne de `version-projet`.

## Ce que je te laisse : 3 fichiers

### `fenetre.py`

Garde la tienne. Tes 297 lignes ajoutées depuis le 3 juillet n'entrent en collision avec rien.
Ce qui se dispute, c'est le câblage `moodle_sync`, que j'ai écrit deux fois, une fois par
branche, sans m'en rendre compte. Le mien, celui de `version-projet`, est le plus complet.
Voici quoi remplacer chez toi :

| ce que tu as sur `moodle-sur-release` | ce qu'il faut à la place | commit |
|---|---|---|
| `self.b_moodle = QPushButton(...)`, cliquable toujours | le bouton qui se désactive en mode local et affiche la progression locale | `c39c741` |
| `moodle_sync.rejouer()` seul au lancement | plus l'avertissement `desaccord_url` et le `QTimer` qui rafraîchit le score | `de114b9`, `c39c741` |
| `_connecter_moodle` qui rejoue après appairage | plus `signaler_deja_faits(self.prog.etapes_faites)`, sinon la progression d'avant l'appairage est perdue | `de114b9` |
| rien | `_maj_moodle` et `_maj_indicateur_local`, deux méthodes neuves | `de114b9`, `c39c741` |
| `signaler_porte` à la validation | **identique des deux côtés**, rien à faire | `3ad88a8` |

Les trois commits à reprendre sont donc `3ad88a8`, `de114b9` et `c39c741`. Ton `45ef8d4`,
Compiler ≠ Tester, est déjà greffé sur `version-projet`, ne le refais pas.

### `tuteur_ia.py`

Garde ton multi-moteur, tes 187 lignes. Je n'ai que trois morceaux à réinjecter, tous du commit
`36592f4` du 7 juillet :

1. `import garde_fous` en tête.
2. Le cran N3 dans `_CONSIGNE_CRAN`, qui passe de « Tu es libre d'aider comme tu veux » à la
   version bornée : jamais le programme complet, jamais plus de 3 lignes d'affilée.
3. Dans `demander_aide`, la ligne `reponse = garde_fous.masquer_si_solution(etape, reponse)`,
   **avant** l'appel à `filtre_solution`. L'ordre compte : le garde-fou structurel retire le
   code qui ouvrirait la porte, le filtre lexical rattrape les reprises ligne à ligne.

### `tests/test_tuteur_ia.py`

Union simple, avec un piège. Garde `TestMoteur` et tes 14 tests. Reprends mes 4 tests de
garde-fou et le helper `_ex01`.

**Supprime `test_prompt_n3_est_libre`.** Il date du 28 juin, il est dans la base commune, et il
est mort depuis le 7 juillet : N3 n'est plus libre. Git n'a aucun moyen de le savoir et te le
gardera si tu ne le retires pas à la main. Il tombera en échec contre le nouveau prompt. C'est
le seul endroit de la fusion où le résultat automatique est faux.

## Ce que tu n'as pas vu

Le cran N3 a été borné le 7 juillet, en même temps que `garde_fous.py`. Ta branche était déjà
partie. Ce n'est pas un désaccord entre nous, tu ne l'as simplement jamais croisé. Si tu as une
raison de penser que N3 doit rester libre, dis-le dans un commit, mais sache que le garde-fou
et ses 3 tests reposent dessus.

## Ce que la fusion ne changera pas

La release. `packaging/build_linux.sh` n'existe que chez toi, et une release construite depuis
`version-projet` régresserait de 52 commits sur la v0.2 déjà en ligne. La release attend cette
fusion, pas l'inverse.

Et la correction du bug de notation ne passe pas par là non plus. Le compagnon note à partir de
`compagnon/etapes_notees.json`, le client n'envoie que des événements bruts. Un redéploiement
Render corrige la note de tous les bundles déjà distribués, sans rien reconstruire.
