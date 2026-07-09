# Démarrage, brancher l'atelier TP C sur un cours Moodle

Ce document est le point de départ. Il explique, pas à pas, comment mettre le
suivi de progression en route dans un cours. Pour les détails de configuration
de l'outil, voyez `GUIDE-MOODLE-integration-enseignant.md`.

## 1. Le service compagnon est déjà en route

Le service qui reçoit la progression et écrit les notes tourne à l'adresse
`https://compagnon-tp-c.onrender.com`. Il n'y a rien à lancer au quotidien.

Il est hébergé sur un plan gratuit qui met le service en veille après un moment
sans visite. Le premier lancement d'activité le réveille en quelques secondes,
la file d'attente de l'atelier absorbe ce délai, l'étudiant ne voit rien. Si un
jour il faut le redéployer ou repartir de zéro, la marche à suivre et les
variables d'environnement sont dans le guide.

## 2. Créer l'activité dans le cours, côté enseignant

L'outil est déjà déclaré dans le cours bac à sable comme outil préconfiguré. On
crée alors une activité en le choisissant, sans retaper d'adresse.

1. Ouvrez le cours et activez le mode édition.
2. Dans une section, cliquez sur « Ajouter une activité ou une ressource ».
3. Choisissez « Outil externe ».
4. Dans le champ « Outil préconfiguré », sélectionnez le compagnon du TP C. Sur
   Moodle 4.5, un outil externe se crée uniquement à partir d'un outil
   préconfiguré, il n'y a plus d'ajout manuel par URL.
5. Donnez un nom à l'activité, celui que verront les étudiants.
6. Dépliez la section « Note ». Réglez le type sur « Point » et le maximum sur
   `100`. Vérifiez que l'option qui accepte les notes de l'outil est active.
7. Enregistrez et revenez au cours.

Moodle crée alors une colonne dans le carnet, reliée à cette activité, où le
score s'inscrira.

À titre d'exemple concret, une activité de démonstration a été créée ainsi dans
le cours bac à sable, cours 4665. Elle s'appelle « Atelier TP C, suivi de
progression », sa note maximale est 100 et elle accepte les notes de l'outil.

## 3. Lancer et se connecter, côté étudiant

1. L'étudiant ouvre l'activité depuis le cours. Une page s'affiche avec un code
   de sept caractères du style `72W-HWD`, valable dix minutes et à usage unique.
2. Dans l'atelier de bureau, il clique sur « Connecter à Moodle » et colle le
   code.
3. Il travaille normalement. Chaque exercice validé remonte tout seul au carnet.

## 4. Vérifier que le démarrage a réussi

- La page du code s'affiche à l'ouverture de l'activité. C'est la preuve que le
  lancement signé fonctionne et que l'outil est bien relié au cours.
- Après la connexion, l'atelier affiche « Connecté à Moodle ».
- Un exercice validé fait apparaître un score dans la colonne du carnet, pour un
  étudiant inscrit. Le score vaut cent fois le nombre d'exercices réussis divisé
  par le nombre total d'étapes du parcours. Une étape sur quatorze du parcours
  `be_c` vaut donc environ 7,1 points.

Un point à connaître pour les essais. Si vous ouvrez l'activité avec votre propre
compte enseignant, la case du carnet restera vide. Moodle n'écrit une note que
pour un compte notable dans le cours, et un enseignant ne l'est pas. Ce n'est pas
une panne, la note s'inscrit normalement pour un vrai étudiant. La chaîne
technique complète a d'ailleurs été vérifiée de bout en bout, le détail est dans
`SUIVI-MOODLE-TEST-LINUX-2026-07-09.md`.

## 5. Si quelque chose cloche

- Code refusé. Il ne vaut que dix minutes et qu'une fois. Rouvrez l'activité pour
  en obtenir un nouveau.
- Rien ne remonte. Vérifiez dans l'atelier que le bouton indique « Connecté à
  Moodle ». Sinon, refaites la connexion avec un code frais.
- Après une longue coupure, l'appairage peut être perdu car le disque du service
  gratuit est effacé aux redéploiements. L'étudiant rouvre l'activité et se
  reconnecte. Pour une vraie promotion, il faudra héberger le compagnon sur une
  machine de l'école.
