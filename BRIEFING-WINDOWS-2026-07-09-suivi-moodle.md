# Briefing Windows, 2026-07-09 : suivi Moodle intégré à la version distribuée

Pour le Claude Code qui travaille côté Windows sur l'empaquetage. Ce commit ajoute la
remontée de progression vers Moodle à la version que les étudiants téléchargent. Voici
ce que tu dois savoir pour démarrer sans te tromper.

## Ce qui a changé sur la branche

Trois pièces côté app, plus un lanceur Linux. Aucune autre modification.

- `moodle_sync.py`, nouveau module. Il parle au serveur compagnon, gère l'appairage par
  code court et une file locale d'événements. Bibliothèque standard seulement, aucune
  dépendance nouvelle.
- `chemins.py`, deux constantes ajoutées, `MOODLE_SYNC_FICHIER` et `COMPAGNON_URL`.
- `fenetre.py`, un bouton « Connecter à Moodle » sous la liste du parcours, et un appel
  qui signale chaque porte passée. Sans appairage, tout est inerte, l'app se comporte
  exactement comme avant.
- `packaging/lancer.sh`, le lanceur Linux, sans effet sur le build Windows.

## Effet sur ton build

Rien à changer dans `build_windows.ps1`. `moodle_sync.py` est un module importé par
`fenetre.py`, donc PyInstaller le ramasse tout seul par analyse des imports. Le point
d'entrée reste `packaging/entree_be_c.py`, le parcours reste `be_c`.

## Droits admin

Le suivi Moodle n'ajoute aucune dépendance, donc les exigences du build sont identiques
à celles de la release v0.1-demo que ce PC a déjà produite. Reconstruis avec
`-SkipInstall`, l'environnement est déjà prêt et rien ne demande l'admin. w64devkit est
déjà extrait dans le dépôt, PyInstaller et pip tournent sans élévation.

```
powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1 -SkipInstall -Zip
```

## Le serveur compagnon

Il est déjà déployé et vivant sur `https://compagnon-tp-c.onrender.com`. La constante
`COMPAGNON_URL` pointe déjà dessus, tu n'as rien à configurer. L'app appelle ce serveur,
qui écrit la note dans le carnet Moodle. Tu n'as pas à toucher au serveur.

## À faire pour livrer

1. Fusionner cette PR dans `windows-packaging-tuteur-multimoteur`.
2. Rebuild avec la commande ci-dessus, sur la branche à jour.
3. Nouvelle release GitHub, incrémenter la version, par exemple `v0.2-demo`, en
   remplaçant le zip. Le lien de téléchargement dans Moodle pointe vers la page des
   releases, donc il suivra tout seul.

## Un détail à connaître

L'écriture de la note dans le carnet ne fonctionne que pour un compte étudiant, un compte
qui a une ligne dans le carnet. Un compte enseignant reçoit un refus 400 de Moodle, c'est
normal, sa règle interne interdit de noter un enseignant. Pour les vrais étudiants tout se
passe bien. Ne cherche donc pas à corriger ce 400 si tu testes avec un compte enseignant.

## Mise à jour du 2026-07-10

Depuis ce briefing, l'intégration a été testée et documentée côté Linux. Rien de tout ça
ne change ton travail de build, mais voici l'état à jour pour que tu partes du bon pied.

- La chaîne a été prouvée de bout en bout, appairage, remontée d'événement, poussée de la
  note vers Moodle. Le détail est dans `SUIVI-MOODLE-TEST-LINUX-2026-07-09.md`.
- Un défaut serveur a été corrigé, sans rapport avec le build. Le dénominateur du score
  valait six au lieu de quatorze, il est passé à quatorze. C'est réglé côté serveur, tu
  n'as rien à faire.
- La documentation côté Moodle est écrite : `GUIDE-MOODLE-integration-enseignant.md` et
  `DEMARRAGE-MOODLE.md`. Une activité de démonstration a été créée dans le cours bac à
  sable et validée.
- Le build Linux est publié en pré-release GitHub sous le tag `v0.2-demo-linux`, séparé
  de Windows. La release Windows en ligne reste l'ancienne `v0.1-demo`, sans Moodle.

Ton travail reste exactement celui de la section « À faire pour livrer » ci-dessus :
fusionner la PR numéro 2, reconstruire l'exécutable avec la commande donnée, publier une
release Windows à jour. Un état des lieux complet est dans `ETAT-ET-SUITE-2026-07-10.md`.
