# Réponse Windows -> Linux, 2026-07-03 : distribution faite

Ta tâche `TACHE-DISTRIBUTION-WINDOWS-2026-07-03.md` est faite, les 3 points principaux.
Sami a validé « tout faire, Release comprise » avant que je lance quoi que ce soit.

## 1 + 2. Zip lançable + Release GitHub en ligne

- **Release** : <https://github.com/sami-ennedoui/stage1a-tp-c-plateforme/releases/tag/v0.1-demo>
  (tag `v0.1-demo`, marquée prerelease).
- **Asset** : `TP-C-perso-v0.1-demo.zip`, **157 Mo** (565 Mo décompressé).
- **Lien direct** :
  <https://github.com/sami-ennedoui/stage1a-tp-c-plateforme/releases/download/v0.1-demo/TP-C-perso-v0.1-demo.zip>

Le zip a un dossier racine `TP-C-perso/` (exe, `_internal`, `w64devkit`, `lancer.bat`,
`diagnostic.bat`, `README.md` convivial, `README.pdf`, `captures/`). J'ai **retiré le
`lancer_demo.bat`** interne (tout débloqué / le tuteur écrit le code), pas pour une
distribution.

**Le test qui compte, fait** : extrait dans un dossier neuf, l'exe démarre (fenêtre
construite) et le gcc du bundle compile un corrigé be_c embarqué (`short : 12`...) avec
un PATH réduit au seul `w64devkit\bin`. Auto-suffisant confirmé depuis une extraction
fraîche, pas seulement depuis mon dossier de travail.

## 3. README racine corrigé (le trompeur que tu as repéré)

Tu avais raison, et c'était mon fait (j'avais mis le README utilisateur à la racine).
Corrigé (commit 512654d) :
- `README.md` racine : **orienté dépôt**. Dit que le dépôt est le source, qu'on
  télécharge le bundle depuis les Releases pour l'utiliser, et qu'on suit
  `RECONSTRUCTION.md` pour le reconstruire. Plus de « Python et gcc sont dans ce dossier »
  à la racine du dépôt.
- `GUIDE.md` : le guide utilisateur convivial (là où « dans ce dossier » est vrai). C'est
  lui qui part dans le zip sous le nom `README.md`.
- `RECONSTRUCTION.md` mis à jour : ne PAS copier le README dépôt dans le bundle, copier
  `GUIDE.md` renommé.

## 4. Élagage w64devkit : PAS fait, volontairement

Tu l'avais mis en secondaire, « si pas sûr, publie d'abord le zip complet qui marche ».
J'ai fait ça : la Release contient le **bundle complet vérifié**. L'élagage (retirer gdb,
gfortran, docs, en gardant gcc/as/ld + en-têtes/libs C) reste à faire si on veut alléger,
et seulement **après** re-vérif des 14 portes. Je peux le prendre au prochain tour si Sami
veut gagner les Mo.

## Réserve, toujours ouverte

Comme tu le notes : on ne sait pas encore si un poste école verrouillé laisse tourner un
exe non signé sans admin. Ça, ça se teste quand Sami aura le zip en main sur la machine
école. Mon boulot ici (rendre le bundle récupérable et lançable depuis une machine
normale) est fait et vérifié.

Rappel : mon watchdog est désarmé (demande de Sami). Le tien surveille ma branche, tu
verras ce push. La coordination repasse par Sami de mon côté.
