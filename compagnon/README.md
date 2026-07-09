# Compagnon LTI Moodle

## Rôle du service

Le compagnon est le pont entre l'app bureau du TP C et le carnet de notes de
Moodle. Un étudiant clique l'activité dans son cours, le compagnon lui donne
un code court à coller dans l'app bureau. Une fois l'appairage fait, chaque
porte que l'étudiant passe dans l'app est signalée au compagnon, qui recalcule
le score de progression et le pousse dans le carnet via le service AGS de
Moodle. Le modèle suivi est celui du Matlab Grader, déjà utilisé sur le Moodle
du site pour un usage comparable.

## Variables d'environnement

- `MOODLE_ISS` : l'URL de la plateforme Moodle, `https://moodle.inp-toulouse.fr`.
  Elle est connue à l'avance, propre à l'établissement.
- `MOODLE_CLIENT_ID` : l'identifiant client donné par Moodle après
  l'enregistrement de l'outil. Il se récupère dans les détails de
  configuration de l'outil, une fois celui-ci enregistré dans un cours.
- `MOODLE_DEPLOYMENT_ID` : l'identifiant de déploiement, récupéré au même
  endroit que `MOODLE_CLIENT_ID`.
- `MOODLE_AUTH_LOGIN_URL` : l'URL standard d'initiation de connexion du
  module LTI de Moodle, `https://moodle.inp-toulouse.fr/mod/lti/auth.php`.
- `MOODLE_AUTH_TOKEN_URL` : l'URL standard du jeton du même module,
  `https://moodle.inp-toulouse.fr/mod/lti/token.php`.
- `MOODLE_KEY_SET_URL` : l'URL standard du jeu de clés publiques de Moodle,
  `https://moodle.inp-toulouse.fr/mod/lti/certs.php`.
- `TOOL_PRIVATE_KEY` et `TOOL_PUBLIC_KEY` : la paire de clés RSA de l'outil.
  Elles se génèrent avec `python -m compagnon.cles`, qui les imprime en PEM.
  Elles ne se stockent jamais sur le disque du service, seulement en
  variables d'environnement, pour que l'identité LTI du compagnon survive
  aux redéploiements.
- `FLASK_SECRET` : une chaîne aléatoire propre au déploiement, qui signe les
  sessions Flask.
- `TOTAL_ETAPES` : le nombre d'étapes du TP, utilisé pour calculer le
  pourcentage de progression affiché dans le carnet.
- `COMPAGNON_BASE` : optionnelle, le chemin du fichier SQLite. Par défaut,
  le compagnon utilise `compagnon/compagnon.sqlite3`.

## Enregistrement dans Moodle

Le service doit d'abord tourner quelque part, avec une URL connue, par
exemple sur Render. Dans le cours Moodle concerné, le menu Plus donne accès
à « Outils externes LTI », puis « Ajouter outil ». On choisit la
configuration manuelle, en version LTI 1.3, et on renseigne les champs avec
les valeurs affichées sur la page d'aide du compagnon, à sa racine. Le type
de clé publique est une URL de jeu de clés, keyset. Dans les services à
activer, il faut cocher IMS LTI Assignment and Grade Services et choisir
l'option de synchronisation des notes. La confidentialité se règle sur le
partage du nom, et la case « Afficher dans le sélecteur d'activités » se
coche aussi.

Une fois l'outil enregistré, on ouvre ses détails de configuration depuis le
menu de la ligne dans la liste des outils. On y copie l'ID client et l'ID de
déploiement, à reporter dans les variables `MOODLE_CLIENT_ID` et
`MOODLE_DEPLOYMENT_ID` du service, puis on redéploie.

Reste à créer l'activité dans le cours : mode édition activé, ajout d'une
activité avec l'outil LTI enregistré, note maximale 100. La description de
l'activité doit contenir la limite voulue par la spec sur la portée de la
note : « Suivi de progression de l'atelier TP C. Ce score reflète
l'avancement, ce n'est pas une note d'examen. »

## Contrainte de déploiement

Le compagnon stocke l'état OIDC du lancement LTI dans un cache en mémoire,
SimpleCache. Ce cache vit dans le processus, il n'est pas partagé entre
processus. Avec plusieurs travailleurs gunicorn, l'appel `/lti/login` et
l'appel `/lti/launch` d'un même lancement peuvent tomber sur deux
travailleurs différents, et le second ne retrouve pas l'état écrit par le
premier : le lancement échoue, de façon intermittente, difficile à
reproduire.

Le `CMD` du Dockerfile ne fixe donc pas de nombre de travailleurs et garde
le défaut de gunicorn, un seul worker. Il ne faut pas ajouter `-w` avec un
nombre supérieur à un sans remplacer d'abord ce cache en mémoire par un
stockage partagé entre processus.

## Données personnelles

Le compagnon stocke le nom et l'identifiant Moodle de l'étudiant, le cours,
et des horodatages d'étapes. Il ne stocke ni mot de passe, ni adresse mail,
ni contenu de code.

Tant que le compagnon est hébergé hors de l'école, seuls des comptes de
test du bac à sable doivent y passer. Le passage à de vrais étudiants
suppose la migration sur une machine de l'école, à demander à l'encadrant.

## Limites de l'hébergement gratuit Render

L'offre gratuite de Render a deux défauts connus, acceptés en phase bac à
sable. La machine s'endort après un quart d'heure sans trafic et se réveille
en une trentaine de secondes au premier appel suivant. Le disque est effacé
à chaque redéploiement, donc les appairages de test faits avant un
redéploiement sont perdus et doivent être refaits. Les clés RSA de l'outil
vivent en variables d'environnement plutôt que sur le disque justement pour
cette raison : elles doivent survivre aux redéploiements, sans quoi
l'identité LTI du compagnon changerait à chaque fois.

## Migration vers une machine de l'école

Toute la configuration du compagnon, secrets LTI compris, tient en
variables d'environnement, et le service est empaqueté en conteneur. La
migration vers une machine de l'école consiste donc à lancer le même
conteneur avec les mêmes variables ailleurs, un déploiement de plus, pas une
réécriture. L'argument à porter auprès de l'encadrant pour obtenir cette
machine est simple : le précédent outil Matlab Grader tourne déjà sur le
Moodle du site, avec le même besoin d'hébergement côté école.

## Journal des validations

Les validations manuelles effectuées sur Render et sur Moodle se consignent
ici, avec la date, ce qui a marché, et les surprises corrigées.
