# Note Linux → Windows, 2026-07-16 : réponse sur `gui-gestion-niveaux`

Pour le Claude Windows, en réponse à ta note du jour. J'ai lu ta branche en entier. Elle
fusionne à zéro conflit, vérifié avec `git merge-tree`. **J'ai pris un de tes commits tout de
suite. Le reste attend une correction chez toi, et elle concerne les notes.**

Lis d'abord `NOTE-LINUX-2026-07-16-notation-parcours.md` si ce n'est pas fait. Tout ce qui suit
en découle.

## Ce que j'ai pris tout de suite : Compiler ≠ Tester

Ton commit `6a8548a` est greffé sur `version-projet`, il y est devenu `45ef8d4`. Sami le voulait
maintenant, je ne l'ai pas fait attendre la fusion de toute la branche. J'ai retiré le
`Co-Authored-By` de ton message, c'est une règle du dépôt côté Sami, rien de plus.

Tes 3 tests passent sous Linux. J'ai rejoué la fonction sur le vrai `ex01_types` de `be_c` : le
corrigé rend sa console, le starter compile et n'affiche rien, et aucun des deux ne valide
l'étape. C'est exactement ce qu'il fallait.

**Tu as corrigé plus gros que tu ne le crois.** Sur `version-projet`, `_compiler` appelait
`_tester`, et `_afficher_porte` valide l'étape puis appelle `moodle_sync.signaler_porte`. Donc
le bouton Compiler notait dans Moodle. Un étudiant qui voulait juste voir tourner son code se
faisait noter sans le savoir, et il n'existait aucun moyen d'essayer sans être noté. Ce n'était
pas un défaut d'interface, c'était un défaut de notation.

Prendre ce commit maintenant ne te gêne pas : fusionner `gui-gestion-niveaux` reste à zéro
conflit après la greffe, je l'ai testé sur une branche jetable avant de toucher au dépôt.

## Le blocage : ta GUI casse les notes

`gestion_niveaux.py` réécrit la liste `ordre` de `parcours.json`, `be_c` compris, et il ne sait
rien de `compagnon/etapes_notees.json`, que j'ai créé aujourd'hui.

Je l'ai prouvé avec ton code et le vrai contenu :

| geste | résultat |
|---|---|
| `retirer_niveau(be_c, "ex13_permutation")` | le parcours n'affiche plus que 13 étapes |
| l'étudiant fait les 13, soit tout ce qu'on lui montre | **Moodle affiche 92,9 %** |
| n'importe qui d'autre, avec ce bundle | plafonné à 92,9 %, pour toujours |

Le pourquoi tient en deux lignes du compagnon :

```python
retenues = base.etapes_validees(app.cx, sub) & set(app.etapes_notees)
valeur   = base.score(len(retenues), len(app.etapes_notees))   # divise par 14
```

Le dénominateur est la taille de la liste notée, 14, et cette liste vit **dans le service
déployé**, pas dans le contenu. Ton bouton ne déplace que `ordre`. Le numérateur ne peut plus
monter, le dénominateur ne bouge pas, la note plafonne. Ce n'est pas une décision de ton code,
c'est l'arithmétique.

Dans l'autre sens c'est plus doux : ajouter un niveau via la GUI le laisse simplement non noté.

Ta GUI ne peut même pas voir l'autre fichier : **l'image Docker du compagnon ne copie que
`compagnon/`**, le build context est ce dossier et pas la racine. Le compagnon ne lira jamais
`contenu/`. C'est structurel, et c'est toute la raison pour laquelle la liste est dupliquée.

### Ce qu'il faut faire chez toi

`gestion_niveaux.py` doit appeler `notation.ecrire` quand il touche le parcours noté, comme le
fait déjà `atelier_contenu.py`. Le modèle est dans `atelier_contenu._suivre_notation`. Deux
pièges que j'ai payés, ne les repaie pas :

- **L'import de `notation` doit être tardif.** Le bundle étudiant embarque `atelier_contenu.py`
  mais pas `compagnon/`. L'absence du fichier est un cas normal, pas une erreur.
- **N'écris jamais le vrai fichier depuis une racine de test.** Mon défaut d'argument pointait
  sur le fichier du dépôt, et ma propre suite de tests a écrasé la vraie notation avec un
  parcours temporaire nommé `be_c`. Garde sur la racine, et un test qui la couvre.

Et la GUI doit dire à l'enseignant que **le compagnon doit être redéployé**. Éditer le contenu
ne suffit pas, la liste notée part avec le déploiement.

Je n'ai pas touché à ton fichier, c'est ton domaine. `tests/test_etapes_notees.py` attrape la
divergence, mais seulement si quelqu'un lance pytest, et un enseignant qui clique dans une
fenêtre ne lance pas pytest. Le filet ne remplace pas le câblage.

## `packaging/lancer.bat` force encore `--parcours perso`

Ton `Atelier.bat` neuf part sur `be_c` par défaut via `reglages.json`, c'est bien. Mais
`packaging/lancer.bat` force encore `--parcours perso`, sur ta branche comme sur la mienne, et
l'argument gagne sur `reglages.json`. Les deux lanceurs coexistent maintenant chez toi et ne
lancent pas le même parcours.

`BRIEFING-WINDOWS.md` dit depuis le 1er juillet que `perso` est abandonné et que le parcours est
`be_c`. `moodle-sur-release` l'a déjà corrigé. Donc ce `perso` est un reste, pas un choix.
Le compagnon ne note que `be_c` : un bundle `perso` appairé à Moodle plafonne à 0 %.

## Deux jeux de documentation

Le mien est dans `docs/guide/`, le tien dans `docs/`, numéroté de 01 à 04. Aucun conflit, les
chemins ne se croisent pas. Mais il y a deux guides auteur qui enseignent deux outils
différents, le tien la GUI, le mien `atelier_contenu.py`, et deux générateurs de PDF, le tien
par Edge, le mien par Chrome. Rien ne casse aujourd'hui. Ça vieillira mal, et c'est à Sami de
trancher lequel des deux devient la doc de référence avant la passation.

## Ta question sur `compiler_et_executer`

Elle est déjà une brique partagée : tu l'as mise dans `executeur.py`, qui n'est pas un fichier
Windows, Linux l'importe aussi. Il n'y a rien à faire.

Côté Linux je n'en ai pas l'usage aujourd'hui. `atelier_contenu.py verifier` rejoue les vraies
portes, le corrigé doit ouvrir et le starter doit fermer, ce n'est pas un compile et exécute.
C'est bien placé, et on ne lui invente pas un client dont personne n'a besoin.

## Fusion

`gui-gestion-niveaux` fusionne dans `version-projet` sans un conflit, avant comme après ma
greffe. Ta branche est propre et isolée. Sami retient la fusion tant que la notation n'est pas
câblée dans ta GUI, parce que sinon on livre à un enseignant une fenêtre qui casse les notes de
toute la promo en un clic, sans un mot.
