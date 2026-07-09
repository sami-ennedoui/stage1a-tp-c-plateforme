# Spec — Compagnon LTI Moodle

Date : 2026-07-07
Emplacement du code : `compagnon/` dans ce repo, module `moodle_sync.py` côté app.

## 1. But

Faire remonter la progression de l'étudiant depuis l'app bureau vers le carnet de notes
Moodle du cours, sans rien changer au fonctionnement local de l'app. L'étudiant appaire
son app une fois avec un code court obtenu dans Moodle. Ensuite chaque porte passée
alimente automatiquement une colonne du carnet de notes. Le prof voit qui en est où,
en temps réel, sans dépôt de fichier ni saisie manuelle.

Le suivi Moodle est un bonus, jamais une condition. Une app jamais appairée fonctionne
exactement comme aujourd'hui.

## 2. Constats sur le Moodle de l'école

Vérifié le 2026-07-07 sur `https://moodle.inp-toulouse.fr`, avec un compte enseignant
sur le cours bac à sable « BAS stage QCM et IA », id 4665.

- Moodle 4.5, interface en français.
- Un enseignant du cours peut ajouter un outil externe LTI au niveau du cours. La page
  « Outils externes LTI » du cours affiche le bouton « Ajouter outil ».
- Le site utilise déjà ce modèle : GapsMoov et Matlab Grader sont enregistrés comme
  outils LTI au niveau du site. Matlab Grader est le précédent exact de ce qu'on
  construit, un outil d'exercices externe dont les notes remontent dans le carnet.
- Les web services sont fermés. Pas de création de jeton possible, service mobile
  désactivé. La voie API REST est donc exclue, LTI est la seule voie automatique.
- Ni VPL ni CodeRunner ne sont installés. Installer un plugin demanderait la DSI.

## 3. Vue d'ensemble

Trois acteurs, chacun ne connaît que son voisin.

```
Moodle                          Compagnon                        App bureau
  |                                 |                                |
  |-- 1. clic, lancement LTI ----->|                                |
  |<- 2. page « ton code : KX7-3PF »                                |
  |                                 |<- 3. l'étudiant colle le code -|
  |                                 |-- 4. jeton d'appairage ------->|
  |                                 |<- 5. « porte perso_P1 passée » |
  |<- 6. note écrite au carnet ----|                                |
```

Le compagnon est un service web Python, Flask, base SQLite, bibliothèque pylti1p3
pour le protocole LTI 1.3. Flask plutôt que FastAPI parce que pylti1p3 fournit un
adaptateur Flask prêt à l'emploi et rien pour FastAPI. Ordre de grandeur visé :
trois à cinq cents lignes.

L'app bureau ne parle jamais à Moodle. Moodle ne parle jamais à l'app. Le compagnon
fait le pont et porte seul la complexité LTI.

## 4. Parcours étudiant, l'appairage

1. Dans le cours Moodle, une activité « TP C, suivi de progression » pointe vers le
   compagnon. L'étudiant clique.
2. Moodle lance le compagnon en LTI 1.3 et lui transmet, signés, l'identifiant de
   l'étudiant, son nom d'affichage et le contexte du cours.
3. Le compagnon affiche un code court à usage unique, six caractères lisibles, valable
   dix minutes.
4. Dans l'app, un champ « Connecter à Moodle ». L'étudiant colle le code. L'app appelle
   le compagnon, échange le code contre un jeton permanent, et range ce jeton dans
   le fichier `moodle_sync.json`, à côté de `progression.json`. Pas dans
   `espace_session`, qui est la copie de travail du parcours projet et peut être
   réinitialisée.
5. C'est fini. L'étudiant ne refait jamais cette manipulation, sauf s'il change de
   machine, et dans ce cas il reclique simplement l'activité pour obtenir un nouveau
   code. Un nouvel appairage remplace l'ancien pour le même étudiant.

Code expiré ou déjà utilisé : l'app affiche un message clair qui renvoie vers
l'activité Moodle. Aucun état n'est perdu.

## 5. Remontée des notes

À chaque porte passée, l'app envoie au compagnon l'identifiant de l'étape, le résultat
et l'horodatage, authentifiés par le jeton d'appairage. Le compagnon recalcule le score
global de l'étudiant, le nombre d'étapes distinctes validées rapporté au total, et
l'écrit dans le carnet de notes par le service de notes du LTI Advantage, nommé AGS.
Le compagnon ne connaît pas le contenu de l'app, le total d'étapes est donc une valeur
de configuration du déploiement, à côté des réglages LTI. Ce canal est
serveur à serveur, authentifié par les clés échangées à l'enregistrement de l'outil.
Il ne dépend d'aucune session étudiante ouverte.

Dans le carnet du prof : une colonne « TP C », un score sur 100 par étudiant, mis à
jour en direct.

En v1, une seule colonne globale. Une colonne par étape, le choix des parcours comptés
et le tableau de bord prof sont hors périmètre, voir section 12.

## 6. Le compagnon en détail

### 6.1 Points d'entrée HTTP

Côté LTI, imposés par le protocole :

- `GET/POST /lti/login` : initiation OIDC, Moodle appelle en premier.
- `POST /lti/launch` : le lancement proprement dit, vérifie la signature, crée le code
  d'appairage, affiche la page au code.
- `GET /.well-known/jwks.json` : la clé publique du compagnon, que Moodle vérifie.

Côté app :

- `POST /api/appairage` : reçoit un code, rend un jeton permanent ou une erreur claire.
- `POST /api/evenements` : reçoit une liste d'événements « porte passée », jeton en
  en-tête. Une liste et non un seul événement, pour que la file locale de l'app se
  vide en un appel.

### 6.2 Base de données

SQLite, trois tables.

- `appairages` : identifiant Moodle de l'étudiant, nom d'affichage, contexte du cours,
  jeton permanent, date. Une ligne par étudiant, remplacée en cas de nouvel appairage.
- `evenements` : journal brut de tout ce que les apps envoient, étape, horodatage,
  jeton émetteur, date de réception. Jamais écrasé. Le score est toujours recalculé
  depuis ce journal, jamais stocké comme vérité.
- `config_lti` : les URL et identifiants donnés par Moodle à l'enregistrement de
  l'outil, une ligne par déploiement. Une pour le bac à sable, une plus tard pour le
  vrai cours.

### 6.3 Enregistrement dans Moodle

Fait une fois par déploiement, par l'enseignant, page « Outils externes LTI » du
cours, bouton « Ajouter outil ». Les champs à renseigner viennent du compagnon : URL
de l'outil, URL d'initiation de connexion, URI de redirection, URL du jeu de clés
publiques. Services à activer dans le formulaire Moodle : le service de notes, avec
l'envoi vers le carnet, et le partage du nom de l'utilisateur. Le compagnon documente
ces valeurs sur une page d'aide accessible à sa racine.

## 7. Côté app bureau

Un module nouveau, `moodle_sync.py`, aucun changement de comportement ailleurs.

- Aucune UI dans le module, comme `executeur.py`.
- Deux fonctions publiques : `appairer(code)` et `signaler_porte(id_etape)`.
- Une file locale dans le même fichier `moodle_sync.json`, où chaque événement est
  ajouté avant toute tentative d'envoi. La file se rejoue au lancement de l'app et à
  chaque nouvel événement. Un événement n'est retiré de la file qu'après accusé de
  réception du compagnon.
- Sans appairage enregistré, `signaler_porte` ne fait rien et ne coûte rien.
- Bibliothèque standard seulement, `urllib`, pas de dépendance nouvelle.

Dans l'existant, deux points de contact : `progression.py` appelle `signaler_porte`
là où il enregistre une réussite, et la fenêtre gagne un champ discret « Connecter à
Moodle » qui appelle `appairer`.

## 8. Pannes

Trois cas, tous non bloquants pour l'étudiant.

- Compagnon injoignable depuis l'app : l'événement reste dans la file locale, rejoué
  plus tard. L'app n'affiche rien de plus qu'un indicateur discret d'état de
  synchronisation.
- Moodle injoignable depuis le compagnon : l'événement est en base, la note est
  marquée « à pousser », un rejeu périodique la pousse dès que Moodle répond.
- Serveur gratuit endormi : le premier appel après une pause met une trentaine de
  secondes. La file locale absorbe ce délai, l'étudiant ne le voit pas.

## 9. Triche et portée de la note

Le message « porte passée » est déclaratif. Une app modifiée peut l'envoyer sans avoir
rien compilé. C'est accepté et assumé : ce score mesure la progression pour le suivi
pédagogique, il n'est pas certificatif. Le certificatif reste dans les QCM Moodle.
C'est la philosophie de la plateforme : la porte prouve à l'étudiant que son code
marche, pas au prof que l'étudiant n'a pas triché. Cette limite sera écrite dans la
description de l'activité Moodle pour que personne ne prête à cette colonne plus
qu'elle ne dit.

## 10. Données personnelles

Le compagnon stocke le nom et l'identifiant Moodle de l'étudiant, le cours, et des
horodatages d'étapes. Ni mot de passe, ni adresse mail, ni contenu de code.

Règle de déploiement : tant que le compagnon est hébergé hors de l'école, seuls des
comptes de test du bac à sable y passent. Le passage aux vrais étudiants exige la
migration sur une machine de l'école, à demander à l'encadrant avec le précédent
Matlab Grader comme argument.

## 11. Hébergement

Prototype sur Render, offre gratuite : HTTPS fourni, déploiement par push Git. Deux
défauts connus et acceptés en phase bac à sable : la machine s'endort après un quart
d'heure sans trafic et se réveille en une trentaine de secondes, et le disque est
effacé à chaque redéploiement, donc les appairages de test sont à refaire après un
déploiement. Les clés RSA de l'outil vivent en variables d'environnement, jamais sur
le disque, pour que l'identité LTI du compagnon survive aux redéploiements.

Le compagnon est empaqueté en conteneur, toute la configuration en variables
d'environnement, secrets LTI compris. La migration vers une machine de l'école doit
être un déploiement de plus, pas une réécriture.

## 12. Hors périmètre v1

- Une colonne de carnet par étape ou par jalon.
- Le choix des activités depuis Moodle, dit Deep Linking.
- Un tableau de bord prof dans le compagnon.
- La génération du contenu Moodle depuis `contenu/`, QCM et leçons. C'est le chantier
  « pipeline de contenu », il aura sa propre spec.
- Toute forme de signature anti-triche des événements.

## 13. Tests

1. Tests unitaires du compagnon, client de test Flask : appairage nominal, code
   expiré, code réutilisé, réception d'événements, calcul du score, file « à pousser »
   quand Moodle ne répond pas. Les appels LTI sortants sont doublés par un faux Moodle
   local.
2. Tests unitaires de `moodle_sync.py` dans la suite existante : file locale, rejeu,
   comportement sans appairage, compagnon muet.
3. Test réel dans le bac à sable, le seul qui compte : enregistrer l'outil, cliquer
   comme étudiant, appairer une vraie app, passer une vraie porte, voir la note dans
   le carnet.

## 14. Ordre de construction

Le chemin risqué d'abord, le confort ensuite.

1. Squelette du compagnon : lancement LTI qui affiche le nom de l'étudiant, rien
   d'autre. Enregistré et cliqué dans le bac à sable.
2. Note poussée en dur dans le carnet depuis le compagnon. C'est ici que se cachent
   les surprises du protocole, on veut les voir en premier.
3. Appairage complet, code court contre jeton.
4. `moodle_sync.py` avec sa file, branché sur `progression.py`.
5. Calcul du score réel, page d'aide à l'enregistrement, rejeu périodique.
6. Tests, empaquetage conteneur, documentation de déploiement.
