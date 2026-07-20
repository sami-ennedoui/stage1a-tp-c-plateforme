# Note Linux → Windows, 2026-07-16 : la police de la console, à vérifier chez toi

Pour le Claude Windows. Sami a demandé si la console affiche correctement le rectangle de
l'exercice 5. J'ai testé. **Sous Linux, oui.** Mais en testant j'ai trouvé une fragilité qui
ne peut se voir que sur Windows, et je ne peux pas la trancher d'ici. C'est pour toi.

## Ce qui est en jeu

`be_c/ex05_rectangle` demande de dessiner un rectangle avec deux boucles imbriquées. La sortie
attendue est de l'art ASCII, six lignes de dix tirets :

```
----------
----------
----------
----------
----------
----------
```

Un rectangle ne tient debout que si la console est en chasse fixe. Si la police est
proportionnelle, les lignes n'ont plus la même largeur et le dessin part de travers. L'étudiant
voit alors un résultat qui a l'air faux alors que son code est bon, alors que la porte, elle,
compare du texte et s'ouvre quand même. C'est la pire combinaison possible : le programme est
correct, la porte est verte, et l'écran donne tort à l'étudiant.

## Ce que j'ai vérifié, sous Linux

L'exercice 5, corrigé chargé, porte franchie, capture à l'appui : **le rectangle est droit**.
Mesuré, pas regardé de loin. Dix caractères font 90 pixels que ce soient des tirets, des `i`
ou des `W`. Rien à signaler.

## La fragilité, et pourquoi elle est invisible ici

Il y a deux polices dans le tableau, et une seule est protégée.

`fenetre.py` vers la ligne 96 pose sur l'éditeur et la console une liste de familles **plus**
un `setStyleHint(QFont.StyleHint.Monospace)`. C'est le `StyleHint` qui fait tout le travail.
J'ai vérifié : **aucune** des familles demandées, ni JetBrains Mono, ni Fira Code, ni
DejaVu Sans Mono, n'existe sur mon poste. L'éditeur est quand même en chasse fixe, uniquement
grâce au `StyleHint`. Sans lui, Qt tombe sur `Noto Sans`, une police proportionnelle.

Mais `_afficher_porte`, ligne 367, n'utilise pas cette police. Il repasse par `setHtml` avec :

```python
f'<pre style="font-family:monospace;color:{theme.TEXTE};white-space:pre-wrap;">'
```

**Ce CSS n'a pas de `StyleHint`.** Il demande une famille littéralement nommée « monospace ».
Or « monospace » n'est pas une police, c'est un alias générique. Sous Linux, fontconfig connaît
cet alias et le résout en `Noto Sans Mono`. C'est fontconfig qui sauve la mise, pas le code.

**Windows n'a pas de fontconfig et aucune police ne s'appelle « monospace ».**

## Ce que fait Qt quand la famille est introuvable, mesuré

J'ai simulé le cas en demandant une famille qui n'existe pas. Qt ne se rabat pas sur une
police à chasse fixe, il prend la police par défaut, qui est proportionnelle :

| Famille demandée dans le CSS | Qt résout en | 10 tirets | 10 `i` | 10 `W` | rectangle |
|---|---|---|---|---|---|
| `monospace`, sous Linux | Noto Sans Mono | 71,9 px | 71,9 px | 71,9 px | droit |
| une famille introuvable | Noto Sans | 38,6 px | 30,9 px | 111,6 px | **de travers** |

Voilà à quoi ressemblerait le rectangle si « monospace » ne se résout pas : un `W` est trois
fois plus large qu'un `i`.

## La question que je ne peux pas trancher, et qui est pour toi

**Qt, sous Windows, résout-il la famille « monospace » vers une vraie police à chasse fixe ?**

Si oui, il n'y a aucun bug et cette note ne coûte que sa lecture. Si non, le rectangle de
l'exercice 5 est de travers sur le poste de chaque étudiant, et personne ne l'a jamais vu
parce que nous développons la console sous Linux.

Je penche pour le second cas, sans en être sûr. Deux choses vont dans ce sens. La résolution
d'alias est faite par `QFontconfigDatabase`, qui n'existe pas sous Windows. Et le packaging
n'embarque aucune police, j'ai vérifié, donc rien ne rattrape le coup.

Attention à un piège si tu creuses : **Qt impose lui-même « monospace » à toute balise
`<pre>`**, même quand le widget porte une police proportionnelle. Je l'ai mesuré. Donc
supprimer simplement notre ligne CSS ne supprimerait pas la dépendance à cet alias.

## Le correctif, si le test est mauvais

Une ligne. Ne pas demander l'alias générique, mais la famille **réellement résolue** par la
police du widget, qui existe forcément puisque Qt l'a choisie. Sous Linux cela donne
`Noto Sans Mono`, sous Windows ce que le `StyleHint` aura donné, `Courier New` sans doute.

```python
famille = QFontInfo(self.console.font()).family()
self.console.setHtml(
    f'<span style="color:{couleur};font-weight:bold;font-size:15px;">{titre}</span>'
    f"<pre style=\"font-family:'{famille}';color:{theme.TEXTE};white-space:pre-wrap;\">"
    f'{html.escape(sortie)}</pre>')
```

Il faut importer `QFontInfo` depuis `PyQt6.QtGui`. Testé sous Linux, le rectangle reste droit
et la police résolue est la même qu'avant, donc rien ne change de ce côté. **Je ne l'ai pas
commis** : `fenetre.py` est à toi selon `REPARTITION-TACHES.md`, et surtout toi seul peux
vérifier le résultat sur un vrai Windows. Regarde l'exercice 5 à l'écran, c'est le test.

## Autre chose, mineur

Après une validation, `_afficher_porte` appelle `_remplir_liste`, qui fait `self.liste.clear()`.
La ligne courante retombe alors à -1 et la sélection disparaît de la liste des exercices.
L'étape, l'énoncé, le code et la console restent en place, j'ai vérifié, donc rien n'est perdu.
C'est seulement le surlignage qui s'en va. À toi de voir si ça vaut un `setCurrentRow`.
