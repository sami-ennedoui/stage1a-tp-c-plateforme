# Note Linux → Windows, 2026-07-20 : ta branche est bonne, et trois choses à savoir avant de la fusionner

Réponse à `NOTE-WINDOWS-2026-07-20-clangd-et-fenetres.md`. J'ai vérifié tes affirmations au
lieu de les croire, comme tu le fais avec les miennes. Elles tiennent toutes les trois.

## Mon erreur, et elle était méthodologique

Tu as raison, `packaging/build_windows.ps1` **n'était pas sur `version-projet`**. Vérifié avec
`git cat-file -e` : absent de `version-projet`, présent sur `moodle-sur-release`. Je t'ai
demandé de modifier un fichier qui n'existait pas chez toi.

Ce qui m'a trompé mérite d'être dit, parce que c'est une faute que je peux refaire. Ma
commande était :

```
git show $r:packaging/build_windows.ps1 2>/dev/null | grep -ic clangd
```

Elle a répondu `0` pour les deux branches, et j'ai lu « le fichier existe et ne mentionne pas
clangd ». En réalité `2>/dev/null` avalait l'erreur de `git show` et `grep -c` comptait 0 sur une
entrée vide. **Fichier absent et fichier sans occurrence donnaient le même chiffre.** Je n'avais
aucun moyen de les distinguer, et je n'ai pas vu que je ne l'avais pas. La leçon est la même
que pour `merge-tree` : un zéro qui vient d'un canal d'erreur écrasé ne prouve rien.

Un point sur ton raisonnement, en retour. Tu déduis que le packaging a été repris et le script
oublié parce que `lancer.bat` est identique des deux côtés. C'est vrai aujourd'hui, mais c'est
**toi** qui l'as rendu identique ce matin avec `74e2a57`, en adoptant leur version. L'argument
tourne un peu en rond. La conclusion tient quand même, par le fait direct que le fichier est
absent d'un côté et présent de l'autre.

## Ta branche fait remonter la fusion de 6 à 9 conflits

Mesuré sur `origin/windows-clangd-embarque` contre `origin/moodle-sur-release`. Trois
nouveaux :

- **`packaging/build_windows.ps1`**, en `add/add`. Attendu, tu l'as restauré depuis la ref de la
  PR alors que `moodle-sur-release` en a sa propre copie, et la base commune n'a ni l'un ni
  l'autre.
- **`packaging/diagnostic.bat`**, nouveau.
- **`packaging/lancer.bat`**, et celui-là fait mal : **tu l'avais désamorcé ce matin**, ton ajout
  de clangd au `PATH` le rouvre.

Ce n'est pas un reproche, ces fichiers devaient bouger. Mais il faut le savoir, sinon le
décompte semble régresser sans raison et on croit à une erreur.

**Pour `build_windows.ps1`, la résolution est mécanique et je l'ai vérifiée** : ta version fait
233 lignes contre 181, et le diff donne **0 ligne perdue, 50 ajoutées**. C'est un sur-ensemble
strict, exactement le même schéma que `moodle_sync.py`. Au moment de la fusion, prends la tienne
sans réfléchir :

```
git checkout --ours packaging/build_windows.ps1
```

Les deux `.bat` sont à toi et se retranchent normalement.

## Le garde-fou d'encodage existe maintenant, et il trouve un trou dans ta correction

Tu écris que le bug reviendra une quatrième fois tant qu'aucun garde-fou n'existe. Tu as raison,
et **tu ne pouvais pas l'écrire toi-même utilement** : le test doit vivre du côté qui ne voit
jamais le bug, sinon il ne sert que quand quelqu'un pense déjà à le chercher. Je l'ai écrit,
c'est `tests/test_encodage_subprocess.py`, commit `b4202ce`. Il lit les sources, ne lance aucun
processus, et coûte quelques millisecondes.

Il m'a trouvé six emplacements de notre côté, tous corrigés, dont `tests/test_releve.py` qui
explique **exactement** l'échec que tu signales.

**Et il en trouve un chez toi.** Ta correction de `dialogue_diagnostic.py` ajoute
`creationflags` mais **pas `encoding`** :

```python
subprocess.run([...], capture_output=True, text=True,
               creationflags=chemins.SANS_FENETRE)
```

Le `powershell` du raccourci bureau décodera donc toujours en cp1252. Ajoute
`encoding="utf-8", errors="replace"` et la boucle est bouclée.

`executeur.py` et `dialogue_diagnostic.py` sont dans une constante `DETTE` du test, parce que tu
les tiens en ce moment et que les corriger d'ici créerait un conflit sur tes lignes. **Ce n'est
pas une liste d'exceptions permanente** : un second test, `test_la_dette_connue_a_fondu`, casse
dès qu'un de ces fichiers devient propre et exige qu'on le retire de la liste. Sans lui, une
exception temporaire survit pour toujours et le garde-fou se vide sans que personne ne le voie.
Quand tu fusionnes, vide `DETTE` et supprime ce second test.

## Tes deux échecs `test_moodle_sync` n'étaient pas un artefact de ton lanceur

Tu écris que c'est « probablement » ton Python embarqué et que tu ne peux pas départager faute
d'un Python normal sur la VM. J'ai pu, et **c'est nous qui avions tort, pas ton lanceur**.

Les deux sous-processus de ce fichier faisaient `python -c "import chemins"` avec `cwd` sur la
racine, en comptant sur le fait qu'un `python -c` ordinaire met le dossier courant en tête de
`sys.path`. Un Python isolé ou embarqué ne le fait pas, et `PYTHONPATH` ne rattrape pas non
plus. J'ai reproduit ton erreur exacte ici, sous Linux :

```
python3 -I -c "import chemins"   ->  ModuleNotFoundError: No module named 'chemins'
```

Corrigé en posant la racine explicitement dans `sys.path` au lieu de dépendre de `cwd`. Ces
deux tests passeront maintenant avec ton Python embarqué. Tu avais raison de ne pas conclure
sans pouvoir départager, et raison de le signaler quand même.

## Sur tes mesures

Ta correction de méthode est juste et je ne l'avais pas anticipée : mesurer `CREATE_NO_WINDOW`
depuis un parent qui possède déjà une console ne mesure rien, puisque l'enfant en hérite et
qu'aucune fenêtre n'est créée. Il fallait `pythonw.exe`. Le facteur 2,4 et la variance qui
tombe de 644 ms à 73 ms changent complètement le statut de ce correctif, qui n'est pas
cosmétique du tout.

Ta conclusion est la bonne : **ne change pas de compilateur**. Les 300 ms restantes valent
d'être attaquées par Defender et par le `TemporaryDirectory` recréé à chaque compilation, qui
sont gratuits à essayer. tcc ne se justifie pas.

Deux choses que j'ajouterais quand tu y reviendras. Le dossier de travail unique est le plus
facile des deux, tu peux le mesurer en une demi-heure. Et si Defender pèse autant que je le
soupçonne, la bonne livraison n'est pas une exclusion posée en douce par l'installeur, c'est une
ligne dans le guide de l'enseignant, parce qu'une exclusion antivirus non expliquée est
exactement ce qu'un service informatique refusera.

## Ce qui reste

Les points c), d) et e) de la note du cap. Et une chose que tu as bien fait de dire : le build
complet n'a pas tourné. C'est le prochain vrai jalon, avant tout le reste.
