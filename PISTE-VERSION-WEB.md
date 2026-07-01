# Piste d'évolution : une version web du TP C

Statut : **note d'analyse**, aucune implémentation. La décision actuelle est de
**garder le livrable natif** (`.exe` PyInstaller + `w64devkit`, parcours `be_c`)
et de n'ouvrir le chantier web **que si l'idée est validée** par les encadrants
et les personnes qui testeront. Ce document sert de point de reprise.

## 1. D'où vient la question

L'idée initiale était : « et si on utilisait Docker pour ne développer que côté
Linux, puis déployer sur Windows, et éviter les tests Windows ? » Puis :
« l'interface web semble mieux ; le backend tournerait chez moi et je donne un
lien (github.io) à tester ».

Ces deux idées se heurtent à des contraintes techniques précises, résumées ici.

## 2. Ce que Docker fait et ne fait pas (pour ce projet)

- Docker n'est **pas un compilateur croisé**. Sous Windows, les conteneurs sont
  **Linux** (via WSL2). Un conteneur Linux ne produit ni n'exécute un `.exe`
  Windows natif. Donc « développer dans Docker (Linux) puis déployer un `.exe`
  Windows » **ne marche pas** pour ce livrable.
- Une **appli graphique** (PyQt6) dans un conteneur Linux nécessite un serveur X
  (VcXsrv / WSLg) pour s'afficher sur Windows : fragile, et plus lourd qu'un
  double-clic. Mauvais compromis pour un destinataire non technique.
- Docker ne permet **pas de sauter les tests Windows** d'un livrable Windows
  natif ; il les **cache**. Les bugs rencontrés étaient tous spécifiques à
  Windows et invisibles sous Linux :
  - nom du binaire `prog` vs `prog.exe` ;
  - `python312._pth` et `sys.path` (Python embeddable) ;
  - mojibake « cÅ“ur » (sortie UTF-8 décodée en cp1252) ;
  - fenêtre cmd qui clignote (appli `--windowed` lançant un process console) →
    `CREATE_NO_WINDOW` ;
  - crash du bouton Tester quand gcc n'est pas sur le PATH.
  Rappel : même Wine ne suffit pas à tester (l'import PyQt6 y échoue à cause de
  l'UCRT).

Conclusion : pour un livrable **Windows natif**, il faut construire et tester
**sur Windows**. Docker n'y change rien.

## 3. Le vrai verrou d'une version web : github.io est **statique**

GitHub Pages (`github.io`) n'héberge que du **statique** (HTML/CSS/JS). Il ne
peut **pas** exécuter gcc ni aucun code serveur. Or le cœur du TP est de
**compiler et exécuter du C**. Deux architectures permettent de contourner ça.

### Option A — tout dans le navigateur (WebAssembly)

Compiler et exécuter le C **côté client** via un compilateur C porté en **WASM**
(il tourne dans l'onglet de l'utilisateur).

- **Aucun backend** pour la compilation → site 100% statique → hébergeable sur
  github.io, gratuit, public. Le testeur ouvre l'URL, rien à installer, marche
  sur tout OS (et mobile).
- Les 14 exercices sont compatibles : `printf`, `scanf` (on injecte déjà
  l'entrée via `sortie_attendue` / `entree`), `math.h`, et l'écriture de fichier
  d'ex13 (système de fichiers virtuel en mémoire du runtime WASM).
- **Coût** : intégrer un compilateur C en WASM et brancher stdin / fichiers /
  code de sortie est la vraie partie technique. C'est faisable mais non trivial.

### Option B — un backend hébergé

Un serveur (conteneur Docker) compile / exécute le C ; le frontend statique
l'appelle par HTTP.

- Plus flexible (vrai gcc, tout le C standard), mais :
  - il faut **héberger le backend de façon publique** (pas seulement sur un PC
    perso derrière une box ; sinon tunnel type ngrok + machine allumée en
    permanence, ou un VPS / hébergeur cloud) ;
  - **sécurité** : exécuter du C d'inconnus = exécution de code arbitraire. Bac à
    sable obligatoire : conteneur jetable par soumission, pas d'accès réseau,
    limites strictes de temps et de mémoire, nettoyage systématique.

## 4. Le cas du tuteur IA (Claude / Codex)

Le **compilateur** peut être 100% navigateur (Option A). Le **tuteur**, lui,
appelle un modèle via une **clé API secrète**, qu'on ne peut pas mettre dans du
JS statique public (elle serait exposée). Trois options :

1. une **petite fonction serverless** (relais vers l'IA, la clé reste côté
   serveur) hébergée par le porteur du projet ;
2. chaque utilisateur fournit **sa propre clé** dans l'interface ;
3. **tuteur désactivé** dans la démo publique (les exercices fonctionnent sans).

Autrement dit, une démo publique « pure github.io » peut avoir la compilation
qui marche entièrement côté client, mais le tuteur demande au minimum une
fonction serverless ou une clé apportée par l'utilisateur.

## 5. Recommandation

Pour l'objectif « donner un lien qu'une personne teste sans rien installer » :
**Option A** (compilateur WASM, site statique sur github.io). Le seul morceau
nécessitant un mini-serveur est le tuteur IA, à rendre optionnel au début ou à
brancher plus tard via une fonction serverless.

C'est un **nouveau projet** (réécriture de l'interface PyQt vers le web), mené
en parallèle du livrable `.exe` actuel qui reste valable.

## 6. Décision et prochaine étape

- **Maintenant** : on garde le livrable natif (`.exe` + `w64devkit`, `be_c`,
  tuteur multi-moteur, mémoire de conversation, énoncés courts). Il est prêt et
  testé sur Windows.
- **Plus tard, si validé** : ouvrir le chantier web en commençant par un
  **prototype Option A** sur 1 ou 2 exercices (éditeur + compilation C en WASM
  dans le navigateur, tuteur mis de côté), pour vérifier que l'approche tient
  avant d'aller plus loin.
