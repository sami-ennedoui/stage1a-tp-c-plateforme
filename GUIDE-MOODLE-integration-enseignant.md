# Intégrer l'atelier TP C à un cours Moodle

Ce guide explique comment brancher l'atelier de bureau sur le carnet de notes
d'un cours Moodle, pour que la progression des étudiants y remonte toute seule.
Il s'adresse à l'enseignant qui prépare le cours. Il décrit la configuration
réellement en place sur le bac à sable « BAS stage QCM et IA », cours 4665, et
sert de modèle pour la reproduire ailleurs.

## Comment ça marche

L'intégration repose sur LTI 1.3, la norme d'interopérabilité de Moodle. Il y a
deux morceaux à relier.

D'un côté, un petit service en ligne, le compagnon, tourne à l'adresse
`https://compagnon-tp-c.onrender.com`. C'est lui qui reçoit les validations
d'exercices, calcule un score et l'écrit dans le carnet par le service AGS de LTI.

De l'autre, Moodle doit connaître ce service comme un « outil externe ». Une fois
l'outil déclaré, on ajoute une activité au cours. Quand l'étudiant ouvre cette
activité, Moodle lance le compagnon et lui transmet de façon signée qui est
l'étudiant et où écrire sa note.

La liaison se configure donc dans les deux sens. Moodle a besoin des adresses du
compagnon. Le compagnon a besoin des adresses et des identifiants de Moodle.

## Côté Moodle, déclarer l'outil externe

Cette étape se fait une seule fois. Selon les droits, elle se fait au niveau du
site par un administrateur, ou au niveau du cours par l'enseignant, dans la
gestion des outils externes. On crée un outil à la main avec ces valeurs.

- Version LTI : LTI 1.3
- URL de l'outil : `https://compagnon-tp-c.onrender.com/lti/launch`
- URL d'initiation de connexion : `https://compagnon-tp-c.onrender.com/lti/login`
- URI de redirection : `https://compagnon-tp-c.onrender.com/lti/launch`
- Type de clé publique : URL du jeu de clés
- URL du jeu de clés publiques : `https://compagnon-tp-c.onrender.com/.well-known/jwks.json`

Il faut ensuite activer les bons services et le partage d'identité.

- Service IMS LTI Assignment and Grade Services : choisir l'option qui autorise
  la synchronisation des notes et la gestion de la colonne. C'est ce service qui
  permet au compagnon d'écrire au carnet.
- Partager le nom de l'étudiant avec l'outil : toujours. Le compagnon affiche le
  prénom sur la page du code, sans le nom la page reste utilisable mais moins
  claire.
- Accepter les notes de l'outil : toujours.

Après l'enregistrement, Moodle attribue à l'outil un identifiant client et un
identifiant de déploiement. Ces deux valeurs servent à configurer le compagnon.
Sur le déploiement en place, l'identifiant client est `5oPdEmm4mYJWgAO` et
l'identifiant de déploiement est `4`.

## Côté compagnon, renseigner les adresses de Moodle

Le compagnon lit sa configuration dans des variables d'environnement, réglées ici
sur Render. Elles décrivent la plateforme Moodle et l'identité de l'outil.

- `MOODLE_ISS` : `https://moodle.inp-toulouse.fr`
- `MOODLE_CLIENT_ID` : l'identifiant client rendu par Moodle, ici `5oPdEmm4mYJWgAO`
- `MOODLE_DEPLOYMENT_ID` : l'identifiant de déploiement, ici `4`
- `MOODLE_AUTH_LOGIN_URL` : `https://moodle.inp-toulouse.fr/mod/lti/auth.php`
- `MOODLE_AUTH_TOKEN_URL` : `https://moodle.inp-toulouse.fr/mod/lti/token.php`
- `MOODLE_KEY_SET_URL` : `https://moodle.inp-toulouse.fr/mod/lti/certs.php`
- `TOTAL_ETAPES` : le nombre d'étapes du parcours distribué, `14` pour `be_c`

Les clés RSA de l'outil, une privée et une publique, sont aussi dans
l'environnement. Le jeu de clés publiques servi à l'adresse `.well-known` en
découle. Il ne faut jamais les régénérer sans refaire la déclaration côté Moodle.

## Ajouter l'activité au cours

Dans le cours, on ajoute une activité « Outil externe » et on choisit l'outil
préconfiguré. On donne un nom à l'activité, celui que verront les étudiants. Sur
le bac à sable, cette activité s'appelle « Test ».

Il faut vérifier deux réglages de note. Le type de note est un point, avec un
maximum de 100. L'option qui accepte les notes de l'outil doit rester active.
Moodle crée alors une colonne dans le carnet, reliée à cette activité. C'est dans
cette colonne que le score s'inscrira.

## Ce que fait l'étudiant

Le déroulé est court.

1. L'étudiant ouvre l'activité depuis le cours. Le compagnon affiche une page
   avec un code de sept caractères du style `72W-HWD`. Ce code est valable dix
   minutes et ne sert qu'une fois.
2. Dans l'atelier de bureau, il clique sur « Connecter à Moodle » et colle le
   code.
3. À partir de là, chaque exercice validé remonte tout seul. L'étudiant n'a plus
   rien à faire, il travaille normalement.

Le score envoyé vaut cent fois le nombre d'exercices réussis divisé par le nombre
total d'étapes du parcours. Pour `be_c`, une étape sur quatorze vaut donc environ
7,1 points sur 100.

## Le carnet de notes

La note apparaît dans la colonne de l'activité et se met à jour à chaque nouvel
exercice validé. Si Moodle est lent ou momentanément injoignable, le compagnon
garde la note en attente et la repousse tout seul un peu plus tard. L'étudiant ne
voit jamais d'erreur pour autant.

## Dépannage

Un compte enseignant ne reçoit pas de note. Si vous testez l'activité avec votre
propre compte enseignant, la case du carnet restera vide et les journaux du
compagnon montreront un refus. C'est voulu par Moodle, qui n'écrit une note que
pour un compte notable dans le cours, et un enseignant ne l'est pas. Prendre le
rôle « Étudiant » depuis le compte enseignant ne change rien, c'est un simple
aperçu. La note s'écrit sans problème pour un vrai étudiant inscrit.

Un code refusé. Le code ne vaut que dix minutes et qu'une seule fois. Il suffit
de rouvrir l'activité dans le cours pour en obtenir un nouveau.

Un appairage perdu après une coupure. Le service tourne sur un hébergement
gratuit dont le disque est effacé à chaque redéploiement. Un appairage fait avant
un redéploiement est alors perdu. L'étudiant rouvre l'activité, récupère un
nouveau code et se reconnecte. Pour une vraie promotion, il faudra héberger le
compagnon sur une machine de l'école, ce qui règle aussi la question des données
personnelles.

## État vérifié

Cette configuration a été testée de bout en bout depuis Moodle. Le lancement
signé, l'appairage, l'obtention du jeton du service de notes et la poussée du
score vers la bonne colonne fonctionnent. Le détail du test est dans
`SUIVI-MOODLE-TEST-LINUX-2026-07-09.md`. La seule chose non encore visible est le
chiffre dans une case du carnet, faute d'un compte étudiant pour l'essayer, ce
qui se confirmera au premier étudiant de la promotion.
