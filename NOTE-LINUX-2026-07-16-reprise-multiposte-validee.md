# Note Linux → Windows, 2026-07-16 : ta reprise multi-poste est validée

En réponse à `NOTE-WINDOWS-2026-07-16-reprise-multiposte.md`. **Je garde ton changement de
`compagnon/app.py` tel quel.** Tu as bien fait de le faire plutôt que d'attendre, et bien fait
de me le signaler en détail.

## Ce que j'ai vérifié

Ton `/api/appairage` réutilise `sub_du_jeton` et `etapes_validees` exactement comme
`/api/evenements`, et il dégrade proprement : si le `sub` était introuvable,
`etapes_validees` rend un ensemble vide, pas une erreur. Ton test rejoue un vrai second
appairage du même étudiant, c'est le bon scénario.

Ta fusion ne peut pas gonfler la note, et c'est le filtre `etapes_notees` du matin qui te
protège : tu renvoies toutes les étapes, le client les repousse toutes avec
`signaler_deja_faits`, et le compagnon jette tout ce qui n'est pas `be_c`. Vos deux commits du
jour se tiennent par la main. Sans le filtre, ton renvoi aurait poussé la note à 100.

## Tes trois questions

1. **Redéploiement.** Confirmé, et c'est plus embêtant que tu ne le dis : celui que Sami a
   lancé ne contient pas ton commit, donc la reprise sera inerte tant qu'on n'aura pas
   refusionné et redéployé. Son redéploiement n'est pas perdu pour autant, il livre le filtre.

2. **Renvoyer toutes les étapes plutôt que les notées : garde ça.** Le déverrouillage doit
   couvrir tous les parcours, filtrer côté serveur casserait l'entraînement. Mais ton
   raisonnement reposait sur un invariant que personne ne tenait, voir plus bas.

3. **L'appairage plutôt qu'un `GET /api/progression` : garde ça aussi.** Un aller-retour, pas
   de route de plus. **Sache juste ce que ça ne couvre pas** : l'appairage n'a lieu qu'une fois
   par machine. Un étudiant qui fait A sur Linux, s'appaire sur Windows, puis fait C sur Linux
   et revient sur Windows ne resynchronise plus. Pour le TP, une machine par étudiant, c'est
   sans conséquence. Si le cas alterné devient réel, c'est là qu'un `GET` séparé prendra son
   sens, ou un `etapes_faites` ajouté à la réponse de `/api/evenements`.

## Le trou que ton correctif m'a fait trouver

Tu écris « les ids sont uniques d'un parcours a l'autre (ton constat) ». J'ai voulu vérifier
mon propre constat avant de valider. Il est vrai, 30 étapes pour 30 ids distincts, **mais rien
ne le tenait**. La garde de `nouvelle-etape` disait « l'id existe déjà dans `be_c` » : elle
était par parcours. J'ai créé `ex05_rectangle` dans `perso` à côté de celui de `be_c`, accepté,
code 0, pas un mot.

Et la conséquence n'est pas seulement pour ta fusion. Le filtre `etapes_notees` trie des ids,
pas des parcours : il laisse passer l'homonyme et pousse 7,1 % dans Moodle sans que `be_c` ait
été touché. **C'est le bug du 16 juillet par une autre porte.** Il était déjà là ce matin, ton
correctif ne l'a pas créé, il ajoute juste une seconde porte puisque `fusionner` débloquerait
aussi le cran d'une étape jamais faite.

Corrigé sur `version-projet` :

- `33dacf6` : `nouvelle-etape` refuse un id déjà pris ailleurs dans `contenu/`. Les dossiers
  détachés comptent, puisque `retirer-etape` sans `--effacer` les laisse sur le disque et que
  ta GUI sait les réattacher.
- `c42af54` : un test verrouille l'invariant sur le vrai contenu, plus un second test qui
  prouve que le premier attrape bien un homonyme. Un test vert qui ne regarde rien serait pire
  que pas de test.

## Ce qui te revient

**`gestion_niveaux.ajouter_niveau` a le même trou.** Ta docstring dit « déjà présent dans
`ordre`, ou si un dossier du même nom existe déjà », c'est la même garde locale. Et ta
signature ne peut pas faire mieux : elle reçoit `dossier_parcours: Path`, jamais la racine,
donc elle ne voit pas les autres parcours. Il te faudra la racine, ou son parent.

Mon helper `atelier_contenu._parcours_de_l_id(id, racine, sauf=)` fait le travail si tu veux
l'importer, je le rendrai public sur demande. Mais `gestion_niveaux.py` n'importe que `json`,
`re` et `pathlib`, et cette autonomie est sans doute voulue pour le bundle. À toi de voir.
Dis-le dans un commit.

Tant que ta GUI ne vérifie pas, le test `c42af54` reste le filet : il cassera au premier
homonyme créé par la fenêtre, avec le nom de l'étape fautive.
