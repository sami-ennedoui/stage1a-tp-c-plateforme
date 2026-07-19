# Note Linux → Windows, 2026-07-16 : la version Windows devient le produit

Sami change de cap. La version Windows n'est plus un portage de la version Linux, c'est **la**
version. Ce sont les derniers jours de son stage, donc l'objectif n'est plus d'ajouter des
fonctions, c'est de livrer quelque chose de fini et de documenté que quelqu'un d'autre pourra
reprendre. Cette note remplace la répartition des tâches précédente pour tout ce qui suit.

## Ce que tu peux arrêter de suivre

Pour t'éviter de porter du contexte devenu inutile :

- **Le compagnon LTI, Render, l'appairage, la note Moodle.** Sami quitte le compagnon Render.
  Ne construis plus rien dessus. **Mais ne l'arrache pas non plus tout de suite**, la
  destination n'est pas décidée, voir la dernière section.
- **Les histoires de branches et de PR.** C'est réglé. Il ne reste que `version-projet` et
  `moodle-sur-release`, et zéro PR ouverte.
- **`compagnon/`, `atelier_contenu.py`, `releve.py`, le mode `ATELIER_SUIVI=local`.** Côté
  Linux, sans effet sur ton travail.

## Le préalable qui ne change pas : finis la fusion

Tes quatre fichiers, `fenetre.py`, `executeur.py`, `tuteur_ia.py` et `tests/test_tuteur_ia.py`,
restent à désamorcer. Ce n'est pas du travail perdu même avec le nouveau cap : `main` doit
réunir le packaging, le README et le client, qui vivent aujourd'hui sur deux branches
différentes. Tout ce qui suit se construit dessus. La méthode et les pièges sont dans
`NOTE-LINUX-2026-07-16-menage-branches-et-desamorcage.md`.

Rappel du piège qui coûterait cher : `appairer` renvoie 3 valeurs sur `version-projet` et 2 sur
`moodle-sur-release`. Garde la ligne de `version-projet`.

---

## a) Le LSP : il existe déjà, et il ne marche pas chez l'étudiant

**J'ai vérifié, et c'est un vrai trou.** `lsp_clangd.py` fait 377 lignes, il est complet, et
`chemins.flags_toolchain_clangd()` aligne bien clangd sur le gcc de w64devkit. Le travail
d'intégration est fait.

Mais `clangd_disponible()` est un simple `shutil.which("clangd")`, et **clangd n'est embarqué
nulle part**. `build_windows.ps1` ne le mentionne pas une seule fois, il ne télécharge que
w64devkit, qui fournit gcc et MinGW mais **pas** clangd. clangd appartient à LLVM, c'est un
autre paquet.

Donc sur une machine étudiante fraîche, `which("clangd")` rend None, la GUI désactive
silencieusement le LSP, et personne ne voit jamais l'autocomplétion ni les erreurs en direct.
Le commit `344b0a9`, « clangd embarqué », n'embarque en réalité que les **drapeaux** de clangd.
Le nom du commit m'a induit en erreur avant que je regarde.

Ce qu'il reste à faire, et c'est peu :

1. Télécharger clangd dans `build_windows.ps1`, comme tu le fais déjà pour w64devkit. La
   release officielle `clangd-windows-*.zip` de `clangd/clangd` sur GitHub fait dans les 50 Mo,
   contre 93 Mo pour le bundle actuel. Vérifie la taille avant de t'engager, si c'est trop
   lourd, `llvm-mingw` ou un clangd allégé sont des solutions de repli.
2. L'ajouter au `PATH` dans `lancer.bat`, comme w64devkit.
3. Vérifier sur la VM que `clangd_disponible()` rend bien True dans le bundle, pas dans ton
   dépôt de développement où clangd est peut-être installé par ailleurs. **C'est le piège
   classique : ça marche chez toi et pas chez l'étudiant.**

Le label `self.label_lsp` existe déjà dans la fenêtre. Fais-lui dire quelque chose d'explicite
quand clangd manque, plutôt que de se taire.

## b) La fenêtre de terminal et la lenteur : deux problèmes distincts

Sami les cite ensemble, ce sont deux causes différentes et une seule est résolue.

**La fenêtre cmd qui clignote est déjà corrigée, chez toi.** C'est
`creationflags=_SANS_FENETRE` dans l'`executeur.py` de `moodle-sur-release`, avec
`_SANS_FENETRE = getattr(subprocess, "CREATE_NO_WINDOW", 0)`. Ce correctif est justement dans
un des quatre fichiers que tu démêles. **Garde ta version, elle a raison.** Le
`version-projet` ne l'a pas. Même chose dans `tuteur_ia.py`.

Attention, il faut le passer à **tous** les `subprocess.run`, pas seulement à la compilation.
`chemins.flags_toolchain_clangd()` lance `gcc -dumpmachine` puis `gcc -E -v` au démarrage, sans
`creationflags`. Ces deux appels feront clignoter une fenêtre au lancement. Le lancement de
clangd lui-même aussi. Vérifie tous les points d'appel.

**La lenteur est un autre sujet, et je te demande de mesurer avant de changer de compilateur.**
Référence mesurée ici sous Linux : `porte_programme` complète, gcc plus exécution plus
jugement, tient en **48 ms**. gcc seul prend 47 ms. Autrement dit sous Linux tout le coût est
dans gcc, et gcc est déjà rapide.

Si c'est beaucoup plus lent sous Windows, gcc n'est probablement pas le coupable principal.
Trois suspects, par ordre de probabilité :

1. **Windows Defender.** Il analyse en temps réel chaque `.exe` nouvellement écrit. L'atelier
   en produit un à chaque clic sur Compiler ou Tester, dans `%TEMP%`. C'est souvent le premier
   poste de dépense, et de loin.
2. **`tempfile.TemporaryDirectory()` à chaque appel.** `_compiler_et_lancer` crée et détruit un
   dossier temporaire par compilation. Sous Windows, création de dossier, écriture, suppression
   coûtent bien plus cher que sous Linux. Un dossier de travail unique, réutilisé, serait
   gratuit à implémenter.
3. **Le coût de lancement d'un processus.** Il est structurellement plus élevé sous Windows, et
   gcc en enchaîne plusieurs, `cc1`, `as`, `ld`.

Mesure d'abord, avec un chronomètre autour de `_compiler_et_lancer`, puis en désactivant
temporairement la protection en temps réel de Defender sur le dossier de travail. Si Defender
explique l'essentiel, changer de compilateur ne servira à rien, et l'ajout d'une exclusion de
dossier documentée pour l'enseignant réglera le problème.

Si gcc reste le coupable après mesure, **tcc**, le Tiny C Compiler, est le bon candidat. C'est
un exécutable unique d'environ 300 Ko, souvent dix fois plus rapide que gcc. Son défaut est que
ses avertissements sont bien plus pauvres, or `-Wall` fait partie de la pédagogie ici. La
combinaison qui garde les deux : tcc pour le bouton Compiler, qui doit être instantané, gcc
pour la porte, qui juge et peut se permettre 200 ms. À ne faire que si la mesure le justifie,
parce que ça double la chaîne d'outils à embarquer et à maintenir.

## c) La progression locale, dans un fichier illisible

Aujourd'hui `progression.json` est du JSON lisible et indenté :

```json
{ "etapes_faites": ["ex01_types", "ex02_operateurs"], "cran_max": 1 }
```

Un étudiant l'ouvre et se donne toutes les étapes. Sami veut un fichier minuscule et non
lisible, avec un mot de passe dans la plateforme pour le modifier.

**Dis-lui la vérité sur ce point, et écris-la dans la doc : c'est de l'obfuscation, pas de la
sécurité.** La clé de déchiffrement voyage forcément dans l'exécutable, donc un étudiant
déterminé gagnera toujours. Ce qu'on empêche, c'est l'édition opportuniste au Bloc-notes, et
c'est déjà beaucoup. Promettre plus serait mentir.

Ce que je propose, et qui reste petit :

- Un format compact, par exemple les identifiants joints par un séparateur puis compressés en
  `zlib` puis encodés en base64. Quelques dizaines d'octets.
- Une signature `hmac` en queue, avec une clé fixe dans le code. Le fichier modifié à la main
  ne vérifie plus, et la plateforme le détecte au lieu de charger n'importe quoi.
- **Décide ce qui se passe quand la signature casse**, c'est le vrai choix de conception. Tout
  effacer punit l'étudiant qui a juste copié son fichier d'un poste à l'autre. Je conseille
  d'avertir, de repartir d'une progression vide, et de garder l'ancien fichier à côté sous un
  autre nom.

Le mot de passe existe déjà et tu peux le réutiliser tel quel : `auteur.py`, avec
`verifier(saisi)` et `definir(nouveau)`, stocke une empreinte SHA-256 dans `auteur.json`. Si tu
veux bien faire, remplace ce SHA-256 nu par `hashlib.pbkdf2_hmac`, un SHA-256 simple se casse
au dictionnaire. Ce n'est pas urgent, c'est un mot de passe local.

**Où vit le fichier, c'est la question à trancher avant d'écrire une ligne.** Aujourd'hui
`chemins.RACINE / "progression.json"`, donc à côté de l'exécutable. Bien pour une clé USB,
mauvais si le bundle est installé dans `C:\Program Files`, où l'écriture est refusée.
`%APPDATA%` est le bon endroit sous Windows, mais casse l'usage nomade. Choisis en connaissance
de cause et documente-le, parce que c'est la première question que posera celui qui reprendra.

## d) Le tuteur : remettre le toggle, et accepter n'importe quelle IA

**Le multi-moteur existe déjà chez toi**, sur `moodle-sur-release`, et il est bien fait :
`_MOTEURS = ("claude", "codex")`, la variable `ATELIER_AI` force un moteur, sinon le premier
trouvé sur le `PATH` gagne, et `_moteur_choisi()` rend None proprement quand il n'y a rien.
Garde tout ça, c'est ta version qui a raison sur ce fichier.

Ce qui manque, c'est que `_commande()` code en dur la forme de l'appel :

```python
if binaire == "codex":
    return ["codex", "exec", "--skip-git-repo-check", ...] + [prompt]
return [binaire, "-p"] + [prompt]
```

Un troisième moteur demande donc de modifier le code. Sami veut qu'il suffise de donner la
commande. La forme que je te propose, avec un emplacement explicite pour le prompt :

```
ATELIER_AI_CMD = "claude -p {prompt}"
ATELIER_AI_CMD = "codex exec --skip-git-repo-check {prompt}"
ATELIER_AI_CMD = "ollama run qwen2.5-coder {prompt}"
```

Découpe avec `shlex.split`, puis remplace le jeton `{prompt}`. Trois points à ne pas rater.
Garde `claude` et `codex` en valeurs par défaut, pour que rien ne casse si personne ne
configure. Si `{prompt}` est absent de la commande, passe le prompt sur l'entrée standard
plutôt que d'échouer, beaucoup d'outils marchent comme ça. Et **ne construis jamais la commande
par concaténation de chaîne avec `shell=True`**, un énoncé contenant une apostrophe suffirait à
tout casser, sans parler du reste.

Range ça dans `reglages.py`, qui existe déjà et gère les réglages locaux, plutôt que dans une
variable d'environnement seule. L'enseignant doit pouvoir le changer sans toucher au système.

**Le toggle.** Il n'existe pas. Les deux `QCheckBox` de ta fenêtre servent au dialogue d'aide,
« Joindre mon code » et « Joindre le rendu de la console ». Il faut donc un vrai interrupteur
qui coupe le tuteur, visible, et dont l'état survit au redémarrage, donc encore `reglages.py`.
Sami en a besoin pour les séances où l'IA n'est pas autorisée. Quand le tuteur est coupé, cache
le panneau plutôt que de le griser, et coupe-le vraiment côté code, un bouton désactivé mais un
`demander_aide` encore appelable ne vaut rien.

## e) Ce que j'ajoute, et le trou qu'il faut connaître

### La porte est franchissable sans écrire une ligne de C, sur les 14 exercices

Trouvé et mesuré aujourd'hui. `porte_programme` juge **la sortie standard et jamais le code**.
Chaque fragment de `sortie_attendue` est cherché en sous-chaîne dans ce que le programme
affiche. Donc ceci ouvre la porte de l'exercice 1, « les types de variables » :

```c
int main(void) {
    printf("short : 12\nint : 260\nchar : A\nfloat : 3.500000\ndouble : 2.500000e+00\n");
    return 0;
}
```

Pas une variable, pas un type. **J'ai testé les 14 étapes de `be_c` : 14 sur 14 tombent.** Et
le pire, c'est que le message d'échec **donne les lignes à copier**. Le cycle est : cliquer
Tester, lire « Il manque ceci dans ta sortie », coller dans un `printf`, porte ouverte. Trente
secondes par exercice, sans aucune IA.

Deux défauts plus petits, sur le même mécanisme. La comparaison en sous-chaîne accepte
`short : 120` quand elle attend `short : 12`, donc une valeur fausse plus longue passe alors
qu'une valeur fausse plus courte est refusée. Et l'énoncé de l'exercice 1 demande d'utiliser
`scanf` alors que le champ `entree` est vide, donc tout `scanf` lit la fin de fichier et
l'étudiant obtient des variables non initialisées. Un étudiant qui suit l'énoncé **ne peut pas**
passer.

**La décision de Sami : deux parcours.** Un parcours à porte étanche, et un parcours libre où
l'on peut aller à n'importe quel niveau. Ça tombe bien, le système multi-parcours existe déjà
et c'est exactement ce qu'il sait faire.

Ce qui te concerne directement :

- **Les identifiants d'étapes doivent rester uniques dans tout `contenu/`**, entre les deux
  parcours. Ta garde `_id_pris_ailleurs` de `5420e21` le tient déjà, et le test `c42af54` est le
  filet. Ne les retire pas en simplifiant.
- Le parcours libre doit ignorer le verrouillage. Regarde `progression.etape_deverrouillee`, et
  préfère un champ dans `parcours.json`, par exemple `"libre": true`, plutôt qu'un test sur le
  nom du parcours. Un test sur le nom se casse au premier renommage.
- Pour la porte étanche, la piste est de tester avec **plusieurs jeux d'entrées** au lieu d'un
  seul. Un `printf` littéral peut satisfaire un jeu, pas deux. Ça demande un champ `cas` dans
  les `meta.json` et une boucle dans `porte_programme`. Ça répare aussi l'incohérence des
  énoncés, puisque `scanf` redevient possible et utile.
- **Les 14 énoncés sont à relire** pour dire ce que la porte vérifie vraiment. C'est du contenu,
  pas du code, et c'est probablement le plus long. Vois avec Sami qui s'en charge.

### Le champ de l'énoncé est trop petit, et il est figé

Vérifié dans ta `fenetre.py` : le panneau central est un `QVBoxLayout` avec des facteurs
d'étirement fixes, `centre.addWidget(self.enonce, 2)`, puis 5 pour les onglets et 3 pour la
console. L'étudiant ne peut donc rien redimensionner, quelle que soit la longueur de l'énoncé.

Remplace ce `QVBoxLayout` par un `QSplitter` vertical avec les mêmes proportions par défaut.
L'utilisateur tire alors les séparateurs à sa guise. Sauve les tailles avec
`splitter.saveState()` dans `reglages.py` et restaure-les au lancement, sinon il refait le
réglage à chaque démarrage. C'est un changement peu risqué et très visible.

### Trois choses que je conseille pour une livraison propre

**SmartScreen.** Un exécutable non signé téléchargé depuis GitHub déclenche « Windows a protégé
votre ordinateur ». Beaucoup d'étudiants s'arrêteront là en croyant à un virus. Une signature
de code coûte de l'argent, donc ce n'est pas la solution ici. Mets une capture d'écran du
message dans le guide, avec la marche à suivre, « Informations complémentaires » puis « Exécuter
quand même ». Une capture vaut mieux que trois paragraphes.

**Teste sur la VM Windows propre, pas sur ton poste de développement.** Elle existe déjà, dans
`scratch-stage1a/win10-vm/`. C'est le seul endroit où le trou de clangd, une exclusion Defender
manquante ou un `PATH` incomplet se voient. Ton poste a des outils installés que l'étudiant n'a
pas, et c'est exactement ce qui masque ce genre de bugs.

**Un seul document de reprise.** Sami s'en va. Le dépôt contient aujourd'hui trois jeux de docs
qui se recouvrent, et une dizaine de notes de coordination entre nous deux qui n'intéresseront
personne d'autre. Il faut un document unique qui réponde à quatre questions : comment
reconstruire le bundle, comment ajouter un exercice, comment changer le mot de passe du mode
auteur, et où vivent les fichiers de l'étudiant. Les notes `NOTE-LINUX-*` et `NOTE-WINDOWS-*`
peuvent partir dans un sous-dossier `historique/`, elles ont fait leur travail.

---

## Le compagnon Moodle : tranché, il devient une démo

Sami a répondu. **Le compagnon reste, mais comme démo seulement.** Sa raison est nette et elle
ferme le sujet : le service tourne sur son compte Render personnel, l'école ne peut pas dépendre
de ses identifiants. Le produit livré ne parle donc à aucun serveur.

**C'est fait, côté Linux, commit `a61658e`.** Il n'y avait qu'une ligne à changer dans
`chemins.py`, le défaut de `ATELIER_SUIVI` passe de `"moodle"` à `"local"`. Tout l'interrupteur
existait déjà : `signaler_porte`, `signaler_deja_faits` et `rejouer` sortent immédiatement, et
la fenêtre remplace le bouton Moodle par un indicateur de progression locale. Preuve
comportementale, un processus neuf sans la variable dans son environnement franchit une porte
et fait zéro appel réseau.

Ce que ça veut dire pour toi :

- **Ne retire rien.** `moodle_sync` et le compagnon restent dans le dépôt, inertes. Le mode
  Moodle devient un opt-in explicite, pour la démo et la soutenance.
- **Ne mets pas `ATELIER_SUIVI` dans `lancer.bat`.** Le défaut suffit, et un défaut qui se
  contredit dans un lanceur est un piège pour celui qui reprendra.
- **Attention à trois sens du mot démo, qui ne sont pas le même axe.** Il y a le drapeau
  `--demo` de `atelier_snake.py`, qui débloque tout et fait écrire le code par le tuteur. Il y a
  `packaging/lancer_demo.bat`, qui pose ce drapeau. Et maintenant `ATELIER_SUIVI=moodle`, qui
  est autre chose encore. Ne les mélange pas au packaging. Si tu ajoutes un lanceur pour la
  démo Moodle, donne-lui un nom qui ne dise pas seulement « demo ».
- La progression locale du point c) devient donc **le seul** enregistrement de ce que fait
  l'étudiant. Ça relève son importance, et ça rend le choix de son emplacement encore plus
  structurant.

Corollaire sur le tuteur, même raison. L'école ne pourra pas utiliser les identifiants de Sami
non plus. C'est exactement pourquoi le point d) demande une commande configurable : chaque
établissement met son propre moteur et ses propres accès. Vérifie bien que l'atelier reste
pleinement utilisable sans aucun moteur IA disponible, compiler, tester et jouer doivent
marcher seuls. `_moteur_choisi()` rend déjà None proprement, garde ce comportement.
