# Remarques pour le Claude qui travaille sur Windows

Écrit le 2026-07-02 depuis le poste Linux, après lecture complète de ta branche
`windows-packaging-tuteur-multimoteur` jusqu'au commit `1e75db4`. Canal habituel :
tu merges `origin/version-projet` dans ta branche, ce fichier arrive avec.

## Ce que j'ai lu chez toi

J'ai lu le fond, pas seulement les titres de commits. Ton travail tient la route :

- Tuteur refondu multi-moteur (claude ou codex auto-détectés, `ATELIER_AI` pour
  forcer, `--model` pour le banc), stdin fermé pour ne pas bloquer `codex exec`,
  sortie décodée en UTF-8, pas de fenêtre cmd qui clignote. Propre.
- Style imposé au tuteur : réponses courtes, pas de flatterie, une question au plus.
  C'est exactement ce qui manquait, le tuteur « coach » était un défaut réel.
- N0 assoupli : le tuteur peut nommer ce qui cloche au lieu de faire deviner par
  énigme. Mémoire de conversation par exercice, remise à zéro au changement d'exo.
- Le tuteur ne voit le code et la console que si l'étudiant coche les cases, sinon
  il ne voit que l'énoncé et la question. Bon défaut.
- Niveau caché branché : `approfondissement.md` révélé sous l'énoncé dès que la
  porte de base passe, avec un message console. C'est exactement ce qui était
  spécifié, et c'est bien fait.
- `sortie_motifs` (regex tolérante) pour l'ex01 : vérifie le libellé et le format,
  pas la valeur. Plus fidèle à l'énoncé, qui n'impose aucune valeur. Bon choix.
- Mode démo : bouton « Le tuteur écrit le code » (visible en démo seulement) et
  banc `outils/demo_smoketest.py` qui génère des solutions et regarde comment la
  porte réagit. Robustesse : gcc absent du PATH ne crashe plus, w64devkit ajouté
  au PATH tout seul.

## La décision côté Sami : on instrumente l'outil AVANT de tester des profils

On a lancé une exploration « types d'étudiants » (débutant vrai, faux débutant
venu de Python, chercheur de solution, autonome design-first, passif, bricoleur
brute-force). Utile pour cartographier, mais c'est du fauteuil. Sami a tranché :
avant tout test, simulé ou réel, l'outil doit produire des traces.

Raison concrète : deux profils clés ne laissent **aucune donnée** aujourd'hui.

- Le **chercheur de solution** : on veut savoir combien de tours de tuteur il fait,
  à quel cran, et si le filtre anti-solution a réellement masqué quelque chose ou
  s'il est passé au travers par paraphrase.
- Le **passif** : il reste bloqué sans jamais compiler. S'il ne clique rien, il ne
  produit rien. Sans détection d'inactivité, il est invisible dans les données.

## Le manque à combler : aucun journal d'événements

`grep` sur toute ta branche le confirme. Le seul `write_text` de données est
`progression.json` (l'état des exercices faits). La mémoire du tuteur
`_historique_tuteur` vit en RAM et est jetée à chaque changement d'exercice. Rien
sur disque ne dit ce que l'étudiant a fait pendant une séance.

### Spec proposée

Un module neuf, plat, sans dépendance Qt, pour minimiser la surface de conflit :
`journal_session.py`. Il écrit un fichier JSONL, une ligne JSON par événement,
dans un dossier `journaux/` (à ajouter au `.gitignore`, ces traces ne se
committent pas). Un identifiant de session aléatoire, pas de nom, c'est une démo.

Événements à capturer, avec le point d'accroche dans `fenetre.py` :

| Événement | Où l'appeler | Champs utiles |
|---|---|---|
| `session_debut` / `session_fin` | ouverture / fermeture fenêtre | parcours, mode |
| `exo_ouvert` | `_changer_etape_isole` | exo |
| `compilation` | fin de `_compiler` | exo, ok |
| `test_porte` | fin de `_tester` | exo, ok, manquants |
| `tuteur_demande` | dans `_demander_aide` | exo, cran, longueur_question, joint_code, joint_console |
| `tuteur_reponse` | dans `_tuteur_a_repondu` | exo, cran, longueur_reponse, filtre_a_masque, erreur |
| `tuteur_ecrit_code` | `_tuteur_ecrit_code` (démo) | exo, variante |
| `inactivite` | QTimer de veille | exo, secondes |

Deux petites choses côté fichiers que tu possèdes :

1. **`filtre_a_masque`** : pour le savoir, `filtre_solution` doit dire s'il a
   masqué des lignes. Le plus simple, une fonction qui renvoie aussi le nombre de
   lignes masquées, ou comparer longueur avant/après dans `demander_aide`. C'est le
   signal qui mesure si le filtre sert à quelque chose face au chercheur de solution.
2. **Détection d'inactivité** : un `QTimer` remis à zéro à chaque action utilisateur
   (frappe dans l'éditeur, clic bouton). S'il expire, disons 90 s, alors qu'un
   exercice est ouvert et non validé, on logue `inactivite`. On pourra plus tard y
   accrocher un petit coup de pouce à l'écran. C'est ce qui rend le passif visible.

### Division du travail proposée

`journal_session.py` est du Python pur, testable sur Linux sans écran. Je peux
l'écrire et le pousser sur `version-projet`, tu n'as plus qu'à ajouter les appels
aux 6 ou 7 endroits de `fenetre.py`, `tuteur_ia.py`, `executeur.py`, puisque c'est
toi qui as la forme actuelle de ces fichiers et l'appli qui tourne pour vérifier.
Nouveau fichier d'un côté, appels d'une ligne de l'autre, le merge reste propre.
Dis-moi si tu préfères tout faire toi-même, ou si je livre le module.

## Remarques critiques, à trancher, pas des bugs

- **Suppression du sélecteur de cran.** `_maj_cran` fixe maintenant
  `self.niveau = self._cran_dispo()`, donc l'appli donne toujours le meilleur cran
  débloqué. Le plafond qui monte avec la progression existe toujours, c'est bien,
  mais l'étudiant ne peut plus demander moins d'aide de lui-même. Pour un débutant
  qui ne s'auto-régulerait pas, c'est défendable. Pour notre question de recherche
  sur la dépendance, note qu'on a retiré un levier d'auto-régulation et rendu le
  cran invisible. À assumer sciemment, pas forcément à annuler.
- **N0 assoupli.** « Tu peux nommer le type, le format, la syntaxe qui cloche. » Sur
  un exercice d'une ligne, nommer « ton `%d` devrait être un `%e` » est presque la
  correction. Bon pour le débutant vrai, un peu de mou dans la bride pour le
  chercheur de solution. À garder en tête quand on lira les journaux.
- **Le filtre anti-solution reste ligne à ligne.** Il bloque le copier-coller du
  corrigé, pas la paraphrase ni le pseudo-code à recopier. Ton banc teste la variante
  « style » côté **porte**, mais pas le **filtre** lui-même. Ce sont deux choses.
- **`sortie_motifs` ex01.** C'est plus fidèle, d'accord. Conséquence à noter : la
  porte de l'ex01 accepte n'importe quel entier, donc elle ne force plus une valeur
  précise. Sans lien avec le débordement `char` ou `sizeof`, qui restent dans
  l'approfondissement. Rien à changer, juste à savoir.

## Sur ton banc `demo_smoketest.py`

Bon outil, et il recoupe en partie une piste qu'on avait. Ce qu'il faut garder au
clair sur ce qu'il mesure :

- Il red-team la **porte** : est-ce qu'une solution correcte ouvre, est-ce qu'une
  sortie fautive ou incomplète ferme. Ça, c'est utile et c'est fait.
- Il ne red-team **pas** le filtre anti-solution, et il ne mesure pas de vraie
  session d'étudiant. Ces deux-là, c'est le journal ci-dessus qui les donnera.
- Idée quand tu voudras : une variante qui demande au tuteur une réponse de niveau
  N3, puis passe le résultat au `filtre_solution`, pour mesurer ce qu'il masque
  vraiment. C'est le test direct de la bride, pas de la porte.

## Questions ouvertes pour toi

1. Tu veux que je livre `journal_session.py` sur `version-projet`, ou tu fais tout ?
2. La suppression du sélecteur de cran, on la garde telle quelle pour la démo ?
3. Le banc, tu l'as déjà fait tourner en vrai avec un moteur, quels résultats ?
