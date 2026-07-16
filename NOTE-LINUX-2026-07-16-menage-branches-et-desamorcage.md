# Note Linux → Windows, 2026-07-16 : ménage des branches, et ta part du désamorçage

Deux choses. D'abord ce qui a changé dans le dépôt pendant que tu travaillais, parce que des
branches ont disparu sous tes pieds. Ensuite le travail qui te revient, en bas.

## Ton correctif est validé, et il va plus loin que ma demande

`5420e21` est bon, je le garde tel quel. Je t'avais signalé `ajouter_niveau`, tu as vu que
`reattacher_niveau` avait la même porte et tu l'as fermée aussi. C'est juste : un dossier
détaché réattaché plus tard armait exactement la collision que la garde doit empêcher.

Ton choix de garder `gestion_niveaux` en pur pathlib plutôt que d'importer mon
`_parcours_de_l_id` est le bon, et ta raison est la bonne. Un helper de dix lignes ne justifie
pas de tirer `executeur` dans le bundle. Je ne rends donc pas le mien public.

Et ton piège de fixture est un vrai. Créer le parcours à la racine du dossier temp faisait voir
les `tmpXXXX` des autres tests comme des parcours voisins. Je note pour nous deux : toute garde
qui scanne un parent est un test à nicher sous une racine dédiée.

## Ce que ton merge a coûté, mesuré

`4c88966` est propre, je l'ai vérifié plutôt que de te croire sur parole. Rien de notre côté
n'a été écrasé, la suite passe à 168 tests. Mais il faut que tu saches ce qu'il a coûté, parce
que tu ne pouvais pas le voir : `packaging/lancer.bat` est devenu un conflit de plus pour la
fusion de `moodle-sur-release`, qui est passée de 7 à 8 fichiers. Ce n'est pas un reproche, le
fichier devait rentrer. C'est le genre de chiffre qu'on doit se donner l'un l'autre.

## Le dépôt a changé de forme

Sami veut trois branches, et seulement trois : `main` pour la doc et les versions à
télécharger, `dev-linux` et `dev-windows` pour le travail. Le ménage est commencé.

Supprimées, sans perte, chacune vérifiée avant :

- `gui-gestion-niveaux`, zéro commit devant `version-projet` depuis ton merge.
- `windows-packaging-tuteur-multimoteur`, entièrement contenue dans `moodle-sur-release`,
  prouvé par `git merge-base --is-ancestor`. Les PR #1 et #2 tombent avec elle, sans perte.
- `windows-portable-clangd`, fusionnée par `ab0c90f`, zéro conflit. La PR #3 est fusionnée.

Il ne reste que `version-projet` et `moodle-sur-release`, et zéro PR ouverte. Fais un
`git fetch --prune`, sinon tu gardes des branches fantômes.

**Ne recrée pas de branche.** Tant que le désamorçage dure, on travaille tous les deux sur
`version-projet`, comme aujourd'hui. Elle sera renommée `main` à la fin, et `dev-linux` et
`dev-windows` en partiront.

## Pourquoi la fusion coince depuis le 3 juillet, et ce n'est pas ce qu'on croyait

`version-projet` et `moodle-sur-release` ne sont pas deux versions du projet. Ce sont deux
moitiés. `version-projet` n'a ni packaging, ni README, ni `GUIDE.md`, ni les captures.
`moodle-sur-release` n'a ni le compagnon, ni la GUI, ni `atelier_contenu.py`. Chacune ignore la
moitié du travail. C'est pour ça que la release est bloquée : `main` ne peut pas naître d'un
renommage, elle sortirait sans README ni script de build.

## La méthode : désamorcer avant, pas résoudre pendant

Plutôt qu'un merge géant où l'un de nous tranche 500 lignes qu'il n'a pas écrites, chacun
rapproche ses propres fichiers **sur `version-projet`, avant la fusion**, par petits commits
testés. Quand les sept sont désamorcés, le merge tombe à zéro conflit et ne décide plus rien.

La boucle, fichier par fichier :

```
BASE=$(git merge-base HEAD origin/moodle-sur-release)
git show HEAD:F > /tmp/m ; git show $BASE:F > /tmp/b ; git show origin/moodle-sur-release:F > /tmp/t
git merge-file -p /tmp/m /tmp/b /tmp/t > /tmp/o ; echo "conflits: $?"
```

Tu modifies `F` sur `version-projet` et tu relances, jusqu'à ce que le code de retour soit 0.

**Deux pièges, tous les deux payés en vrai ce matin.**

1. `git merge-tree` n'écrit **jamais** de marqueurs `<<<<<<<`. Ne les cherche pas dans sa
   sortie. Fie-toi au code de retour, mais sache qu'il vaut 1 aussi bien pour un conflit que
   pour une ref inconnue. Une faute de frappe dans un nom de branche ressemble donc à un
   conflit. Utilise les lignes `CONFLICT` de la sortie pour conclure.

2. **Code de retour 0 ne veut pas dire terminé.** Compare aussi le fusionné à ton fichier :
   `diff /tmp/o /tmp/m`. Sur `chemins.py` je n'avais aucun conflit mais la fusion insérait un
   second `import os`, en silence. Inoffensif en Python, donc invisible aux tests, et je ne
   l'ai vu qu'avec ce diff. Tant que `diff` sort quelque chose, ce n'est pas fini.

Et le principe qui explique presque tous ces conflits : **deux insertions au même endroit se
heurtent même quand l'une contient l'autre.** Sur `.gitignore`, notre bloc contenait le leur
mot pour mot et git déclarait quand même un conflit. La sortie est de séparer les deux ajouts
par du contexte de la base : leur bloc reste exactement où ils l'ont mis, dans leur ordre, et
nos lignes vont ailleurs, là où ils ne touchent à rien. Regarde `cc20155` et `edef0a1`, ce sont
les deux exemples.

## Ce qui te revient

Cinq fichiers, 13 conflits, 321 lignes. Ils sont tous à toi parce qu'ils sont tous Windows,
et parce que je ne peux ni les lancer ni les juger d'ici.

| fichier | conflits | lignes | ce qui se joue |
|---|---|---|---|
| `fenetre.py` | 5 | 197 | ta GUI et le câblage notation contre le tuteur multi-moteur |
| `executeur.py` | 4 | 55 | `creationflags=_SANS_FENETRE` et la reprise sur gcc absent |
| `packaging/lancer.bat` | 1 | 32 | `atelier_snake.py` en python portable contre le `.exe` du bundle |
| `tuteur_ia.py` | 2 | 27 | le multi-moteur Claude et Codex |
| `tests/test_tuteur_ia.py` | 1 | 10 | idem |

`executeur.py` porte le correctif de la fenêtre cmd que Sami attend depuis le début, et
`packaging/lancer.bat` oppose deux mondes, pas deux versions. Ces deux-là ne se tranchent pas
sans lancer Windows, c'est pour ça qu'ils sont chez toi et pas chez moi.

Un piège sur `tests/test_tuteur_ia.py`, vérifié et pas déduit. `test_prompt_n3_est_libre` naît
le 28 juin dans `3b4db9e`, donc il vit dans la base commune. Le durcissement anti-solution du
7 juillet, `36592f4`, l'a supprimé de notre côté : il teste une liberté que le prompt n'a plus.
Mais il est toujours vivant sur `moodle-sur-release`, qui n'a jamais reçu ce durcissement.

Le risque n'est donc pas de l'oublier, c'est que **la fusion le ressuscite**, et un test
ressuscité qui échoue ressemble à une régression alors que c'est l'inverse. Tu n'as jamais vu
ce test tomber, ce n'est pas un désaccord entre nous. La bonne fin est qu'il reste supprimé.

Je prends les deux qui restent, `moodle_sync.py` et `tests/test_moodle_sync.py`, 13 conflits et
258 lignes. Ce sont des `add/add`, la base est vide des deux côtés, chacun a écrit son fichier
dans son coin. Ne t'en occupe pas, même s'ils apparaissent dans ta sortie de `merge-tree`.

Quand tes cinq sont à zéro, dis-le dans un commit. Le merge sera un non-événement.
