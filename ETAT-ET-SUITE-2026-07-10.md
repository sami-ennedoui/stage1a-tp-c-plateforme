# État des lieux et suite, 10 juillet 2026

Point de reprise du chantier « remontée de progression du TP C vers Moodle ». Ce
document résume où on en est et par où continuer. Il pointe vers les autres
documents pour le détail.

## Où on en est

La chaîne complète fonctionne, du côté application, du côté serveur et du côté
Moodle. Un étudiant lance l'activité dans le cours, obtient un code, le colle dans
l'atelier, et chaque exercice validé remonte tout seul au carnet de notes.

Ce circuit a été prouvé de bout en bout. Le lancement signé, l'appairage, la
remontée de l'événement, le calcul du score et la poussée vers la bonne ligne de
note passent tous. La seule chose non encore visible est le chiffre dans une case
du carnet, parce que les essais se font sur un compte enseignant, que Moodle
refuse de noter. Ce n'est pas une panne, c'est une règle de Moodle, et un vrai
étudiant sera noté normalement.

## Ce qui est fait

- Le service compagnon est déployé et vivant sur `https://compagnon-tp-c.onrender.com`.
- L'intégration côté application est portée sur la branche distribuée, dans la
  PR numéro 2.
- Le build Linux est empaqueté, testé, et publié en pré-release GitHub sous le
  tag `v0.2-demo-linux`.
- La documentation côté Moodle est écrite : un guide d'intégration pour
  l'enseignant et un guide de démarrage rapide.
- Une activité de démonstration a été créée dans le cours bac à sable, « Atelier
  TP C, suivi de progression », et validée de bout en bout.
- Un défaut a été corrigé au passage : le dénominateur du score valait six au lieu
  de quatorze, ce qui gonflait la note. Il est maintenant à quatorze.

## Ce qui reste

1. Le côté Windows. Sami fournira un poste avec droits administrateur. Il faudra y
   refaire les tests et la documentation. En parallèle, le binôme fusionne la PR
   numéro 2, reconstruit l'exécutable Windows avec le suivi Moodle, et publie une
   release Windows à jour. La release Windows en ligne est encore l'ancienne, sans
   Moodle.
2. La confirmation visuelle du score dans le carnet, au premier vrai étudiant.
3. La migration du compagnon vers une machine de l'école avant d'ouvrir aux vrais
   étudiants, pour la question des données personnelles.
4. Quelques correctifs différés, listés dans le journal de développement, à
   traiter avant la vraie promotion.

## Repères utiles

- Service compagnon : `https://compagnon-tp-c.onrender.com`, piloté par l'API
  Render, identifiant de service `srv-d97q3seq1p3s73f9d8d0`.
- Cours bac à sable « BAS stage QCM et IA », identifiant 4665. Outil préconfiguré
  numéro 4. Deux activités LTI : « Test » et « Atelier TP C, suivi de progression ».
- Documents à lire pour le détail : `GUIDE-MOODLE-integration-enseignant.md` pour
  la configuration, `DEMARRAGE-MOODLE.md` pour la mise en route, et
  `SUIVI-MOODLE-TEST-LINUX-2026-07-09.md` pour le test de bout en bout. Côté
  Windows, `BRIEFING-WINDOWS-2026-07-09-suivi-moodle.md`.

## Pour reprendre

L'accès à Moodle passe par le cookie de session déposé dans le fichier
d'environnement. Il expire au bout de quelques heures. S'il est périmé, il faut le
rafraîchir depuis le navigateur avant de reprendre les opérations sur Moodle.
