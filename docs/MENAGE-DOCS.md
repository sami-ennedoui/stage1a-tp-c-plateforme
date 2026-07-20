# Ménage de la documentation, à faire après la fusion

Les trois guides de `docs/` remplacent l'existant. Rien n'a été supprimé pour l'instant, parce
qu'une partie des anciens fichiers ne vit que sur `livraison-windows` et que les effacer depuis
l'autre poste entrerait en conflit avec la fusion en cours.

Voici la liste, à exécuter en une fois quand la fusion sera close.

## À supprimer

| fichier | pourquoi |
|---|---|
| `docs/01-guide-utilisateur.md` | remplacé par `guide-etudiant.md` |
| `docs/02-guide-auteur.md` | remplacé par `guide-enseignant.md` |
| `docs/03-README-projet.md` | remplacé par `reprise-du-projet.md` |
| `docs/04-doc-technique.md` | idem, après récupération du §4 |
| `docs/pdf/*.pdf` | rendus des quatre ci-dessus |
| `DOC-gestion-niveaux.md` | doublon à 70 % du guide auteur, plus une note de coordination périmée |
| `packaging/README-2A.txt` | décrit le parcours `perso`, abandonné, donc un autre produit |
| `DEMARRAGE-MOODLE.md` | voir ci-dessous, à supprimer en priorité |
| `GUIDE-MOODLE-integration-enseignant.md` | voir ci-dessous, à supprimer en priorité |

## Deux fichiers à supprimer sans attendre

**`GUIDE-MOODLE-integration-enseignant.md` contient des identifiants de déploiement en clair**,
un `MOODLE_CLIENT_ID` et un `MOODLE_DEPLOYMENT_ID`. Le dépôt est destiné à être transmis. Ces
valeurs n'ont plus d'usage puisque le compagnon devient une démonstration, mais elles ne
devraient jamais avoir été écrites là. À retirer, et à considérer comme divulguées.

Il documente aussi `TOTAL_ETAPES` comme une variable à régler, alors qu'elle est ignorée depuis
le 16 juillet 2026 et remplacée par `compagnon/etapes_notees.json`. Suivre ce document
aujourd'hui produirait des notes fausses.

**`DEMARRAGE-MOODLE.md` affirme une chose démentie par la mesure.** Il écrit que le réveil du
service prend quelques secondes et que « l'étudiant ne voit rien ». Les mesures de juillet
donnent **32,8 secondes** de réveil sur un service qui dort quasiment en permanence. Les deux
fichiers se contredisent aussi entre eux sur la longueur du code d'appairage, six ou sept
caractères.

## À garder tel quel

- `docs/guide/guide.md` et ses captures, **le temps d'en extraire les mesures Render et la
  section sur les droits du compte enseignant**. C'est la justification factuelle du passage au
  mode local, elle ne doit pas disparaître avec le fichier. Une fois recopiée en annexe, le
  reste peut partir.
- `RECONSTRUCTION.md`, qui contient du savoir non reconstituable : le piège PyInstaller qui
  n'embarque pas un module absent du dossier de build et fait planter l'exe au démarrage, la
  régénération des captures et des PDF, et les commandes exactes de publication d'une release.
  **À corriger avant de le garder** : les chemins codés en dur pour un poste nommé, les tailles
  périmées, et l'absence de l'étape clangd.

## À ranger dans `historique/`

Tous les `NOTE-LINUX-*.md`, `NOTE-WINDOWS-*.md`, `PLAN-*.md`, `SPEC-*.md`, `BRIEFING-*.md`,
`REPONSE-*.md`, `REMARQUES-*.md`, `TACHE-*.md`, `DECISION-*.md`, `ETAT-*.md`.

Ne pas les supprimer. Ils portent le raisonnement derrière les décisions, et c'est ce qu'on
regrette de ne pas avoir. Mais ils ne décrivent pas l'existant et ne doivent pas être lus comme
tels.

## Un point à trancher, qui touche le contenu et pas la doc

Deux documents se contredisent sur une question que l'étudiant se pose tout de suite.
`GUIDE.md` dit que les exercices sont indépendants et qu'on peut les faire dans l'ordre qu'on
veut. Le programme, lui, verrouille une étape tant que les précédentes ne sont pas franchies.

C'est le code qui a raison aujourd'hui. La décision des **deux parcours**, un à porte étanche
et un libre, est exactement ce qui doit trancher cette phrase. Les nouveaux guides décrivent le
comportement actuel, à savoir le déverrouillage progressif, et devront être repris le jour où
le parcours libre existera.
