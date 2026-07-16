# Note Windows -> Linux, 2026-07-16 (soir) : reprise de progression multi-poste

Pour le Claude Linux. **J'ai touche a `compagnon/app.py`, ton domaine** : je te le
signale en detail pour que tu valides ou reprennes la main. Fait a la demande de Sami,
qui a constate le bug en direct et redeploie Render.

## Le bug constate

Sami a fait les 2 premiers exos de be_c sur la machine Linux. Sur la machine Windows,
apres appairage a Moodle, il repart au **niveau 1**. Cause : la progression
(deverrouillage des niveaux) vit dans `progression.json`, local a chaque poste. La note
Moodle s'agrege bien cote serveur, mais l'appli ne **redescend jamais** ce que le
compagnon sait deja. `signaler_deja_faits` ne fait que **monter** le local. `/api/appairage`
ne renvoyait que le jeton, `/api/evenements` que `{recu, score}`. La donnee existe
(`base.etapes_validees`) mais ne repartait pas vers le client.

## Ce que j'ai change

**Cote compagnon (ton domaine) :** `/api/appairage` renvoie desormais, en plus du jeton,
la liste des etapes validees de l'etudiant :

```python
sub = base.sub_du_jeton(app.cx, jeton)
faites = sorted(base.etapes_validees(app.cx, sub))
return jsonify({"jeton": jeton, "etapes_faites": faites})
```

Rien d'autre ne bouge cote serveur. Ca reutilise `sub_du_jeton` et `etapes_validees`,
exactement comme `/api/evenements`. Un test ajoute dans `compagnon/tests/test_app.py`
(`test_appairage_renvoie_les_etapes_deja_validees`) : valide 2 etapes, se re-appaire avec
un nouveau code, et verifie que l'appairage les renvoie. **11/11 tests compagnon passent**
(montes dans un venv depuis `compagnon/requirements.txt`, flask absent du poste sinon).

**Cote appli (mon domaine) :**
- `moodle_sync.appairer` renvoie maintenant `(ok, message, etapes_faites)`. Tolere un
  ancien compagnon qui ne fournit pas le champ (liste vide, pas d'erreur).
- `progression.fusionner(prog, ids, parcours)` : fonction pure qui ajoute les etapes
  faites ailleurs et remonte le cran. Un id inconnu du parcours courant est conserve mais
  ne change pas le cran (les ids ne se recoupent pas entre parcours).
- `fenetre._connecter_moodle` fusionne, sauve `progression.json`, et rafraichit la liste
  et le cran. Puis `signaler_deja_faits` comme avant.
- Tests : `test_progression` (3 sur fusionner), `test_moodle_sync` (2 sur le nouveau
  retour). Suite appli : 160 tests, seuls les 8 echecs SDL/Snake pre-existants restent.

## Ce qu'il faut savoir / decisions pour toi

1. **Redeploiement Render obligatoire.** Tant que le compagnon en ligne n'a pas cette
   version, `/api/appairage` ne renvoie pas `etapes_faites`, donc la reprise reste inerte
   (l'appli degrade proprement : liste vide). Le redeploiement que Sami lance maintenant ne
   contient PAS encore ce commit s'il part d'avant.
2. **Choix de renvoyer TOUTES les etapes validees**, pas seulement les notees : le
   deverrouillage cote appli doit couvrir tous les parcours, et les ids sont uniques d'un
   parcours a l'autre (ton constat : 30 ids, 5 parcours, zero collision), donc aucun faux
   deverrouillage. Si tu preferes filtrer, c'est cote serveur, dis-le.
3. Si tu juges que l'endpoint doit etre separe (`GET /api/progression`) plutot que greffe
   sur l'appairage, reprends-le : c'est ton protocole. J'ai choisi l'appairage parce que
   c'est le seul moment ou le client a besoin de la reprise, en un aller-retour.

Branche `gui-gestion-niveaux`. Fusionne toujours proprement dans `version-projet`.
