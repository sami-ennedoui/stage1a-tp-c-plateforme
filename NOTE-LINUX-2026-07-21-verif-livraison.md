# Note Linux → Windows, 2026-07-21 : vérification de `livraison`, et ce qui reste à réunir

Rôle : le poste Linux documente et vérifie. Ceci est un rapport de vérification de ta branche
`origin/livraison`, faite dans un worktree détaché, pas une demande de changement.

## Ce que j'ai vérifié, et qui tient

J'ai repris chacun de tes douze commits sur les points où une erreur coûterait cher. Résultat :

- **La fusion est réparée.** `moodle_sync.py` a retrouvé ses trois gardes `ATELIER_SUIVI`, plus
  `desaccord_url` et `signaler_deja_faits`. Le mode auteur est de nouveau atteignable, par la
  classe `DialogueNiveaux` que ton menu ouvre. Mon repère « `grep dialogue_niveaux` doit valoir
  2 » était trop littéral, tu es passé par la classe et non par le module, c'est aussi bon. Tu
  as même cité le repère dans un commentaire, c'est la bonne façon de répondre à une vérif.
- **Le mode local ne parle plus au réseau.** J'avais mesuré un appel sortant en mode local sur
  la fusion précédente ; il a disparu.
- **Le facteur dix est corrigé.** `a & b = 170` ne franchit plus la porte de `a & b = 17`.
- **`dialogue_diagnostic.py` a reçu son `encoding`.** C'est le trou que je t'avais signalé, où
  ta correction précédente ajoutait `creationflags` mais pas `encoding`. Fermé.
- **216 tests passent**, dont ton `test_portes_etanches.py`.

## Sur les portes étanches, ton commit est exact et honnête, je le confirme

Je l'ai testé et j'allais écrire que 13 étapes sur 14 tombent encore devant un `printf`
littéral. Puis j'ai lu ton message de commit, qui le dit lui-même : « la mécanique est prête, le
contenu ne l'est pas, et la porte reste donc percée tant que les `cas` ne sont pas écrits. »

Nous mesurons donc la même chose. Ta mécanique `cas`, plusieurs jeux d'entrées, est la bonne et
ton test la verrouille sur du contenu factice. Mais aucune des 14 étapes de `be_c` n'a encore
de `cas`, donc en pratique la porte reste franchissable par recopie de la sortie. Un point que
je précise, parce qu'il n'est pas évident : **`sortie_motifs` sur `ex01` ne rend pas la porte
étanche non plus.** Le motif `short\s*:\s*-?\d+` accepte n'importe quel entier, donc
`printf("short : 1")` passe. `sortie_motifs` répare le vrai défaut que j'avais signalé, la
valeur imposée et le `scanf` sans entrée, mais l'étanchéité viendra des `cas`, pas des motifs.
Et pour `ex01` qui n'a pas d'entrée, il faudra d'abord réécrire l'énoncé pour qu'il lise une
donnée, comme tu l'écris toi-même.

Le champ `libre` dans `parcours.json`, porté par l'objet et non déduit du nom, est exactement
ce que la note demandait. Rien à redire.

## Ce qui reste à réunir : nos deux branches ont divergé

`livraison` ne descend pas de `version-projet`. Il lui manque mes cinq derniers commits, et à
`version-projet` il manque tes douze. Ce n'est pas un conflit, c'est deux moitiés à joindre.

Ce que `version-projet` a et que `livraison` n'a pas :

- **Trois guides neufs**, `docs/guide-etudiant.md`, `docs/guide-enseignant.md`,
  `docs/reprise-du-projet.md`. Ils remplacent `docs/01-04`, `GUIDE.md` et `DOC-gestion-niveaux.md`,
  que ta branche a encore. Tu as déjà commencé le même ménage en retirant les deux docs Moodle,
  on va donc dans le même sens. `docs/MENAGE-DOCS.md` liste ce qui doit partir et ce qui doit
  être gardé, dont les mesures Render à recopier en annexe avant de supprimer `guide/guide.md`.
- **Le garde-fou d'encodage**, `tests/test_encodage_subprocess.py`. Il lit les sources et refuse
  tout `subprocess` qui décode sans `encoding`. **Sur ta branche, il attraperait encore quatre
  appels** : `compagnon/tests/test_cles.py` deux fois, `docs/build_pdf.py`, `docs/guide/faire_pdf.py`.
  Je les ai déjà corrigés sur `version-projet`, donc les réunir suffit, il n'y a rien à refaire.

Pas de conflit de doc en vue : mes guides sont des fichiers neufs, tes anciens docs sont ceux
qu'ils remplacent, et tu as déjà retiré les deux que j'avais signalés.

## Comment réunir, à ton choix

`livraison` est la branche la plus complète, elle contient tout sauf mes cinq commits, qui sont
de la doc et un garde-fou sans risque. Le plus simple est de les rejouer sur `livraison` :

```
git checkout livraison
git cherry-pick 396284b..origin/version-projet   # tout ce que version-projet a en plus
```

La borne basse `396284b` est ton propre commit « le compagnon Moodle est tranché », le dernier
que nos deux branches partagent. La plage prend donc tous les miens qui suivent : le garde-fou
d'encodage et ses corrections, les trois guides, `MENAGE-DOCS.md`, et les notes de vérification
dont celle-ci. Ils ajoutent des fichiers neufs sous `docs/`, un test, et corrigent des
`subprocess`. Aucun ne touche à `fenetre.py`, `executeur.py`, `moodle_sync.py` ni au contenu,
donc rien qui entre en collision avec ton travail. Si un `cherry-pick` accroche, ce sera sur les
quatre `subprocess` que tu n'as pas encore corrigés, et la résolution est de garder ma version,
celle qui ajoute `encoding`.

Ensuite `livraison` peut devenir `main`. C'est toi qui décides du moment, tu tiens la
plateforme de développement.

## Un détail qui n'est pas de ton ressort

L'horloge de ta VM est toujours réglée sur le fuseau Pacifique, tes commits sont datés
`-07:00`. Ça ne gêne pas git, mais toute date affichée dans le dépôt sera fausse de sept heures,
y compris celle qu'un lecteur lira sur le document de reprise. Une minute à corriger dans les
réglages Windows quand tu y penseras.
