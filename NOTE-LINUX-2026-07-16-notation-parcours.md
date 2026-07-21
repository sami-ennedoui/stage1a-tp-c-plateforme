# Note Linux → Windows, 2026-07-16 : la note comptait les mauvaises étapes

Pour le Claude Windows. Poussé sur `version-projet`, commit `8642a99`. Un bug de notes,
prouvé et corrigé. **Rien à faire chez toi, mais la cause part de `fenetre.py` et tu dois la
connaître avant d'y toucher.**

## Ce qui se passait

Un étudiant faisait 10 des 14 exercices de `be_c`. Moodle affichait 71,4 %, ce qui est juste.
Il s'entraînait ensuite sur `perso` et faisait ses 4 exercices. **Sa note passait à 100 %**,
sans qu'il ait retouché à `be_c`.

Je ne l'ai pas déduit, je l'ai fait tourner sur la vraie API du compagnon avec le vrai
contenu :

| | avant | après |
|---|---|---|
| 10 des 14 exercices de `be_c` | 71,4 % | 71,4 % |
| puis les 4 exercices de `perso` | **100 %** | 71,4 % |
| puis `be_c` terminé | 100 % | 100 % |

## La cause, et pourquoi elle te regarde

`fenetre.py:372` appelle `moodle_sync.signaler_porte(self.etape.id)`. **L'id part seul, sans
le nom du parcours**, et cet appel est le même quel que soit le parcours ouvert.

Côté compagnon, `etapes_validees` comptait les ids distincts et divisait par `TOTAL_ETAPES`.
Les ids ne se répètent pas d'un parcours à l'autre, je l'ai vérifié : 30 ids pour 5 parcours,
zéro collision. Donc les étapes de `perso` s'ajoutaient à celles de `be_c`.

C'était atteignable pour de vrai : le bundle embarque tous les parcours et le guide apprend
`--parcours` au lecteur.

Détail qui a orienté le diagnostic : `releve.py:25`, le mode local, ne compte que les étapes
**du parcours** qu'il a sous les yeux. Il faisait déjà l'intersection. C'est le mode local qui
avait raison depuis le début et le compagnon qui avait tort. Ma note du 16 juillet prétendait
que les deux modes donnaient le même chiffre : c'était faux dès qu'un second parcours entrait
en jeu.

## Ce qui a changé, côté compagnon seulement

Le compagnon reçoit maintenant la **liste** des étapes notées au lieu d'un nombre, dans
`compagnon/etapes_notees.json`. Le score ne retient que les étapes de cette liste, et le
dénominateur est la taille de la liste. `notation.py` porte le tout.

`TOTAL_ETAPES` disparaît par la même occasion. C'était le second symptôme de la même cause :
le compagnon comptait des étapes sans savoir lesquelles il notait. La variable est ignorée et
le compagnon le dit dans ses journaux au démarrage.

**Je n'ai pas touché à `fenetre.py` ni à `moodle_sync.py`.** Corriger côté compagnon suffit et
ne change rien au protocole. Envoyer le nom du parcours dans l'événement serait plus propre,
mais ça toucherait ton fichier et la file de synchronisation, pour un gain nul aujourd'hui.
Si tu le fais un jour, sache que le compagnon filtre déjà, donc les deux se compléteraient
sans se gêner.

## Ce que tu dois savoir si tu touches à `fenetre.py`

Si tu ajoutes un appel à `signaler_porte` ailleurs, ou si tu changes le parcours lancé par
`packaging/lancer.bat`, souviens-toi que **le compagnon ne note que `be_c`**. Aujourd'hui ta
branche `windows-portable-clangd` lance `--parcours perso`, et `moodle-sur-release` lance
`--parcours be_c`. Les deux ne peuvent pas être le bundle noté. Si un étudiant reçoit le
bundle `perso` et qu'il est appairé à Moodle, il plafonnera à 0 %, puisque aucune de ses
étapes n'est dans la liste notée. C'est le pendant exact du bug que je viens de corriger, et
je ne sais pas laquelle des deux branches est celle que tu distribues.

## Un piège que j'ai créé et refermé

`atelier_contenu.py` tient maintenant `etapes_notees.json` à jour tout seul. En l'écrivant,
**la suite de tests a écrasé le vrai fichier du dépôt** avec le contenu d'un dossier
temporaire, parce qu'un test crée un parcours nommé `be_c` dans un temp et que mon défaut
d'argument pointait sur le vrai fichier. Une garde l'interdit et un test la couvre. Si tu
ajoutes un jour un défaut d'argument qui écrit dans le dépôt, tu sais ce qui t'attend.

## Tests

151 passent : 128 côté atelier, 23 côté compagnon. Un point pour toi : **flask n'est installé
nulle part sur ce poste**, la suite du compagnon ne tourne qu'avec un environnement monté à la
main depuis `compagnon/requirements.txt`. Si tu la lances chez toi, prévois-le.

## Ce qui reste à faire, et qui n'est pas pour toi

Le compagnon en ligne doit être redéployé. Tant que ce n'est pas fait, il note encore sur
l'ancienne règle. C'est chez Sami, pas chez toi.
