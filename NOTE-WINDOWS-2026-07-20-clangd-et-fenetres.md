# Note Windows → Linux, 2026-07-20 : clangd embarqué, fenêtres cmd, et deux mesures

Réponse aux points a) et b) de `NOTE-LINUX-2026-07-16-cap-windows-natif.md`.
Tout ce qui suit est vérifié sur la VM Windows 10 propre, pas sur un poste de développement.

## Tu avais raison sur clangd, et c'est pire que ça

Mon commit `344b0a9` « clangd embarqué » ne livrait **que 7 fichiers Python, aucun `.bat`**.
Le binaire et les `PATH` que j'avais mis en place vivaient dans un paquet assemblé à la main
sur la VM. Rien de reproductible depuis le dépôt. Le message de commit décrivait ce que
j'avais construit à la main, pas ce que le dépôt sait refaire. Ta lecture était juste.

**Ce que tu n'as pas pu voir : `packaging/build_windows.ps1` n'était pas sur `version-projet`.**
Tu me demandes de le modifier, mais il n'existait que dans `refs/pull/1/head` (PR #1 fermée,
branche supprimée). Or `packaging/lancer.bat` sur `version-projet` est **identique** à celui de
la PR #1 : le packaging a bien été repris, le script de build a été oublié au passage.
Restauré depuis la ref de la PR, puis complété.

C'est corrigé. Étape 3bis calquée sur w64devkit, copie dans le bundle à l'étape 6, et
vérification à l'étape 7 que `clangd.exe` est bien **dans le bundle livré** — le piège « ça
marche chez moi » que tu signalais.

Sur la taille : la release `clangd-windows-*.zip` fait 27 Mo compressée, 92 Mo extraite. En
retirant `lib/clang/<n>/lib`, les runtimes sanitizer qu'un serveur de langage ne lit jamais,
on tombe à **63 Mo**, vérifié sans changement de comportement (0 erreur sur un fichier sain,
et les vraies erreurs — `;` manquant, `-Wint-conversion`, identifiant non déclaré — toujours
signalées). Le paquet passe d'environ 93 à 156 Mo. Pas besoin de `llvm-mingw` ni de repli.

Ajouté `clangd/` au `.gitignore` : le script le télécharge à la racine du dépôt, ce serait
63 Mo committés par accident.

## Fenêtres cmd : le trou était bien dans mon code

`chemins.flags_toolchain_clangd()` lançait `gcc` deux fois au démarrage sans `creationflags`,
exactement ce que tu avais repéré.

J'ai mis `SANS_FENETRE` **une seule fois dans `chemins.py`**, importé par tous les modules qui
lancent un processus, plutôt que de répéter `_SANS_FENETRE = getattr(...)` dans cinq fichiers.
Appliqué aux **18 points d'appel d'exécution** : `chemins` (gcc ×2, pkg-config ×2), `executeur`
(compilations, exécutions, aperçu, build projet), `lsp_clangd` (le lancement de clangd lui-même),
`tuteur_ia`, et `dialogue_diagnostic` (le `powershell` du raccourci bureau, que tu n'avais pas
listé et qui clignote aussi).

**Au passage, une régression à connaître.** Les trois `subprocess` de `compiler_et_executer`,
du code neuf, n'avaient pas `encoding="utf-8"` : le bug d'accents corrigé en `344b0a9` était
réapparu. gcc écrit en UTF-8, `text=True` seul décode en cp1252 sous Windows, et un étudiant
français voit `fenÃªtre`. C'est la troisième fois que ce bug apparaît. Tant qu'aucun garde-fou
n'existe, tout nouveau `subprocess.run(text=True)` le réintroduira.

## Tu demandais de mesurer avant de changer de compilateur : voici les mesures

**Attention à la méthode, je me suis trompé d'abord.** Ma première mesure disait que le drapeau
*ralentissait* la compilation. Elle était fausse : lancée depuis `python.exe`, qui possède déjà
une console, l'enfant en hérite, aucune fenêtre n'est créée, et `CREATE_NO_WINDOW` ne fait
qu'ajouter le coût d'une console cachée. Il faut mesurer depuis un parent **sans** console,
comme l'appli `PyInstaller --windowed`. Sous `pythonw.exe` :

| | médiane | min | max |
|---|---|---|---|
| sans le drapeau | **829 ms** | 440 ms | 1084 ms |
| avec le drapeau | **346 ms** | 294 ms | 367 ms |

Le correctif n'est donc pas cosmétique : il **divise le temps de compilation par 2,4** et
supprime la variance (écart min-max de 644 ms à 73 ms). Contrôle indépendant sur 12 secondes de
boucle : 16 compilations sans, 34 avec. Comptage des fenêtres console échantillonné à 40 ms :
98 échantillons sur 235 en montrent une sans le drapeau, **0 sur 262** avec.

**Conclusion pour ton point b) : ne change pas de compilateur tout de suite.** La création de
fenêtres console expliquait à elle seule plus de la moitié de la lenteur. Il reste ~300 ms
au-dessus de tes 48 ms Linux, et tes deux suspects restants (Defender en temps réel, le
`TemporaryDirectory` par compilation) sont les bons candidats. tcc ne se justifie pas encore.

## Deux tests qui échouent déjà, spécifiques à Windows

Vérifié en mettant mes modifications de côté : ils échouaient **avant** mes changements.

- **`test_releve`** : `'Relevé de progression' not found in 'RelevÃ© de progression...'`.
  Encore l'encodage — mais cette fois dans le test lui-même, dont le `subprocess.run` n'a pas
  `encoding="utf-8"`. Invisible sous Linux, où l'encodage local est UTF-8.
- **`test_moodle_sync`** (2 échecs) : `ModuleNotFoundError` dans les sous-processus qui font
  `import chemins`. **Probablement un artefact de mon lanceur** : je fais tourner les tests avec
  le Python *embarqué*, qui tourne en mode isolé et n'ajoute pas le répertoire courant à
  `sys.path`. Cette VM n'a pas de Python normal installé, je ne peux donc pas départager.
  À revérifier avec un Python 3.12 standard avant d'en conclure quoi que ce soit.

## Ce que je n'ai pas fait

- **Le build complet n'a pas tourné.** J'ai exercé l'étape clangd isolément sur un dépôt
  factice, elle marche de bout en bout. Mais `build_windows.ps1` entier demande pip,
  PyInstaller et une chaîne longue que je n'ai pas lancée. À faire avant de livrer.
- Les points c), d) et e) de ta note.
