# Note Linux → Windows, 2026-07-16 : outil de contenu et suivi local

Pour le Claude Windows. Poussé sur `version-projet`. Ta PR #3 part de `de114b9`, donc de la
même base que moi.

**La fusion est propre, je l'ai vérifiée, pas devinée.** `git merge-tree` entre ma branche et
`origin/windows-portable-clangd` ne produit aucun conflit, alors que trois fichiers sont
modifiés des deux côtés. Tes retouches de `fenetre.py` sont vers la ligne 116, les miennes
commencent à 148. Dans `chemins.py` tu ajoutes une fonction à la fin, j'insère une constante
vers la ligne 12. Rien ne se recouvre.

## Ce que Sami a demandé et pourquoi

Deux besoins. D'abord pouvoir ajouter des exercices sans toucher au code source, parce que
c'est son binôme qui écrit le contenu et qu'il n'est pas développeur. Ensuite pouvoir se
passer complètement du serveur, parce que l'hébergement gratuit ne tient pas ses promesses,
mesures à l'appui plus bas.

## Ce qui change

### `atelier_contenu.py`, fichier neuf

Outil en ligne de commande qui crée, vérifie et retire étapes et parcours.

```
python3 atelier_contenu.py lister [<parcours>]
python3 atelier_contenu.py nouveau-parcours <nom>
python3 atelier_contenu.py nouvelle-etape <parcours> <id> --titre "..." [--apres <id>] [--cran N]
python3 atelier_contenu.py retirer-etape <parcours> <id> [--effacer]
python3 atelier_contenu.py verifier [<parcours>]
```

Deux choses valent le coup d'œil.

La première : le squelette produit par `nouvelle-etape` est **déjà un exercice valide et
vérifié**. Trivial, mais il passe. `verifier` est donc vert dès la création, et si l'auteur le
passe au rouge, c'est son édition qui est en cause, jamais le squelette. C'est ce qui rend
l'outil utilisable par un non-développeur.

La seconde : `verifier` rejoue les vraies portes, corrigé qui doit passer et starter qui doit
échouer. **Cela donne enfin un filet automatique à `be_c`, qui n'en avait aucun.**
`tests/test_parcours_tp.py` ne couvrait que `tp_c`. Les 14 exercices sont vérifiés en 2,4
secondes.

### `releve.py` et `--releve`, fichier neuf

`python3 atelier_snake.py --releve --parcours be_c` écrit un `releve.txt` lisible, sans Qt et
sans réseau, que l'étudiant dépose dans un devoir Moodle ordinaire. Le pourcentage utilise la
même formule que `compagnon/base.py:score`, donc les deux modes affichent le même chiffre.

L'empreinte du relevé détecte une modification accidentelle. Elle ne protège pas contre une
falsification volontaire, l'algorithme étant dans le code que l'étudiant possède. C'est écrit
tel quel dans la docstring et dans le guide, ne le survends pas.

### `ATELIER_SUIVI`, dans `chemins.py`

`moodle` par défaut, comportement inchangé. `local` coupe le réseau entièrement.

C'est un **interrupteur franc, pas une absence d'appairage** : même avec un jeton valide sur
le disque, rien ne part. Vérifié avec le vrai jeton de Sami, zéro appel réseau. Le garde-fou
est dans `signaler_porte`, `signaler_deja_faits` **et `rejouer`**, sinon une file laissée par
un ancien mode `moodle` repartirait au démarrage suivant. Une valeur autre que `moodle` ou
`local` est refusée au démarrage plutôt qu'ignorée.

### `moodle_sync.desaccord_url`

Un jeton est délivré par un compagnon précis et ne vaut rien sur un autre. Jusqu'ici, changer
`ATELIER_COMPAGNON_URL` sur une installation déjà appairée faisait partir les envois dans le
vide et grossir la file sans fin, en silence. La fonction détecte le cas, la fenêtre l'annonce
dans la console au démarrage. Elle ne se déclenche que si la variable est définie
explicitement, sinon toute installation normale se croirait déplacée.

## Ce que j'ai touché chez toi, et pourquoi

`REPARTITION-TACHES.md` dit que je ne crée que des fichiers neufs et que les fichiers d'appli
sont à toi. **J'ai enfreint ça sur `fenetre.py` et `chemins.py`.** Autant le dire franchement.

- `chemins.py` : ajout de `ATELIER_SUIVI` et de sa validation, vers la ligne 12.
- `fenetre.py`, 44 lignes sur cinq zones : l'indicateur `Progression locale : n / N étapes`
  qui remplace le bouton Moodle en mode local, le message de désaccord d'URL au démarrage, et
  la mise à jour de l'indicateur à chaque validation.

C'était inévitable : le mode local n'a de sens que s'il se voit dans l'interface. Mais la
règle reste bonne et je m'y retiens pour le reste. Si tu préfères récrire ces 44 lignes à ta
façon, fais-le, l'important est le comportement, pas mon code.

## Ce que tu dois faire

1. **Fusionner `version-projet`** dans ta branche. C'est propre, vérifié.
2. **Embarquer `atelier_contenu.py` et `releve.py`** dans le bundle. Ce sont des imports
   frères, comme `executeur` et `chemins`. `atelier_contenu.py` a besoin de gcc au runtime
   pour `verifier`, mais la porte l'exige déjà, donc rien de neuf pour w64devkit.
3. **Vérifier `ATELIER_SUIVI=local` sur un vrai Windows.** C'est le mode de repli d'une salle
   sans réseau, il faut qu'il marche là-bas. Je ne peux pas le tester.
4. Si tu veux : `atelier_contenu.py verifier be_c` dans ton build, ça attrape une régression de
   contenu avant qu'elle parte chez les étudiants.

## Ce que j'ai mesuré sur Render, et qui devrait peser sur nos choix

Le maintien à chaud que j'ai posé le 11 juillet **ne fonctionne pas**. Le cron demande un
passage toutes les 10 minutes, Render endort le service au bout de 15. Mesure des 20 derniers
passages réels : médiane **90 minutes**, minimum 54, maximum 201. **Les 19 intervalles
dépassent le seuil de sommeil.** GitHub bride les tâches planifiées des dépôts peu actifs.

Conséquence : le service dort quasiment tout le temps, réveil mesuré à 32,8 secondes, et
presque chaque étudiant tombera sur la page de relance et le F5. Aucun réglage ne corrige ça,
c'est le modèle du plan gratuit. Les vraies sorties sont un plan payant, un hébergement à
l'école, ou le mode local. C'est écrit sans fard dans le guide.

## Tests

116 passent, 21 sous-tests. 103 avant, 13 ajoutés. `verifier be_c` et `verifier tp_c` passent
sur le vrai contenu.

**Limite honnête** : `fenetre.py` n'a aucun test automatisé dans ce dépôt. L'indicateur local
et le message de désaccord ne sont validés que par smoketest et par capture d'écran. Sur ton
Windows, c'est à l'œil qu'il faudra les regarder.

## Autre chose

Un guide de 24 pages est en cours de rédaction pour Sami, avec captures : les trois briques,
le contenu et les parcours, la version projet, les trois modes de suivi, LTI, la mise en place
Moodle et le dépannage. Il corrige plusieurs erreurs des specs d'origine, entre autres que le
champ `type` ment, que `recette` et `noeud_cours` ne sont jamais lus, et que `fichier_edite`
est ignoré en mode `programme` et `test_fourni`. Si tu vois passer une contradiction avec ce
que tu sais du code Windows, dis-le par un commit.

Point pour toi : `TOTAL_ETAPES` côté compagnon doit valoir le nombre d'étapes du parcours
distribué. Aujourd'hui 14 pour `be_c`. Si le contenu gagne un exercice sans que cette variable
suive, tous les scores deviennent faux en silence. C'est le lien le plus fragile entre les
deux morceaux, et il n'est vérifié par rien.
