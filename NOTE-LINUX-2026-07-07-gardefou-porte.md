# Note Linux → Windows, 2026-07-07 : garde-fou anti-solution renforcé

Pour le Claude Windows (branche `windows-packaging-tuteur-multimoteur`). Poussé sur `version-projet`.

## Ce qui a changé et pourquoi

On a testé la bride du tuteur sur des modèles ouverts via OpenRouter. Résultat : au cran N3, deux modèles sur quatre donnent le programme complet. Et durcir la seule consigne ne suffit pas, ils contournent en éparpillant la solution sur deux blocs, les déclarations puis les printf, qui se recomposent. Le filtre lexical ligne à ligne se fait battre par la paraphrase, un simple changement de noms de variables passe au travers.

La parade : un garde-fou **structurel** qui ne juge plus les mots mais le comportement. Il reconstruit le code de la réponse et **rejoue la vraie porte de l'étape** dessus. Si le code ferait passer la porte, c'est la solution, on le retire. La paraphrase ne peut rien, c'est le résultat compilé qui tranche.

## Fichiers

- `garde_fous.py` (nouveau) : `masquer_si_solution(etape, reponse)`. Extrait les blocs de code, teste chaque bloc et l'union des blocs contre `executeur.porte_programme` ou `executeur.porte_perso` selon le mode. Union emballée dans un `main` pour attraper la fuite éparpillée. Si une variante ouvre la porte, tout le code est remplacé par un refus, la prose reste.
- `tuteur_ia.py` : consigne N3 durcie (plus direct, mais jamais le programme complet ni un bloc de plus de 3 lignes, refus si on réclame tout) ; `demander_aide` appelle `garde_fous.masquer_si_solution` avant le filtre lexical.
- `tests/test_tuteur_ia.py` : le vieux test « N3 est libre » est remplacé par le nouveau contrat N3 borné ; trois tests ajoutés pour le garde-fou (solution masquée, indice court laissé passer, fuite éparpillée masquée). Suite complète : 62 passent.

## Ce que tu dois faire côté Windows

1. **Fusionner `version-projet`** dans `windows-packaging-tuteur-multimoteur` pour que le build multimoteur embarque `garde_fous.py` et la nouvelle consigne.
2. **Vérifier que le bundle empaqueté inclut `garde_fous.py`** au même niveau que `tuteur_ia.py`. C'est un import frère, comme `executeur` et `chemins`.
3. Le garde-fou a besoin de **gcc au runtime**, mais la porte l'exige déjà, donc rien de neuf pour le packaging w64devkit.

## Limite connue, honnête

Une fuite en **prose pure**, sans bloc de code, échappe au garde-fou. Exemple vu au test : un modèle qui liste `%d %i %c %f %e` en texte. Aucun filtre de code ne rattrape ça. Le reste, dump en un bloc et fuite éparpillée, est masqué.
