# L'atelier C, guide de l'étudiant

Tu vas écrire du C sans rien installer. L'atelier apporte son propre compilateur.

---

## Démarrer

Décompresse l'archive quelque part où tu peux écrire, ton bureau ou une clé USB, puis
double-clique **`lancer.bat`**.

**Ne lance pas l'application depuis l'archive zip sans l'avoir décompressée.** Elle a besoin
d'écrire à côté d'elle pour retenir où tu en es.

### Windows va t'avertir, c'est normal

Au premier lancement, tu verras un écran bleu qui dit « Windows a protégé votre ordinateur ».
Ce n'est pas un virus. L'application n'est simplement pas signée, parce qu'une signature est
payante et que ce projet est un travail d'école.

Clique **Informations complémentaires**, puis **Exécuter quand même**.

### Si rien ne se passe

Double-clique **`diagnostic.bat`**. Il affiche ce que l'atelier trouve ou ne trouve pas, et te
dit quoi envoyer à ton enseignant. Laisse la fenêtre ouverte pour lire.

---

## L'écran

À gauche, la liste des exercices. Au centre, l'énoncé en haut et ton code en dessous. En bas,
la console. À droite, le tuteur.

Un exercice est verrouillé tant que tu n'as pas franchi les précédents.

---

## Les deux boutons qui comptent

**Compiler** compile ton programme et l'exécute. La console te montre le résultat, ou les
erreurs du compilateur. Ce bouton ne valide rien, il te sert à voir ce que fait ton code.

**Tester** franchit la porte. Si ton programme répond à ce que l'énoncé demande, la porte
s'ouvre, l'exercice est validé et le suivant se débloque. Sinon la console te dit ce qui
manque.

**Prends l'habitude de compiler souvent.** Une erreur de compilation trouvée tout de suite se
corrige en une minute. La même erreur trouvée après trente lignes coûte beaucoup plus.

---

## Lire les erreurs du compilateur

C'est la compétence la plus utile du semestre. Le compilateur écrit toujours la même chose :
le fichier, la ligne, puis le problème.

```
programme.c:7:5: error: expected ';' before 'printf'
```

Ligne 7, il manque un point-virgule **avant** `printf`, donc à la fin de la ligne 6. Le
compilateur signale l'endroit où il s'est aperçu du problème, qui est souvent juste après
l'endroit où il faut corriger.

**Corrige toujours la première erreur d'abord, puis recompile.** Une seule faute en provoque
souvent dix autres, qui disparaissent d'un coup.

Pendant que tu écris, les fautes sont aussi soulignées directement dans l'éditeur.

---

## Le tuteur

Le tuteur répond à une question sur ton exercice. Il t'explique, il te met sur la piste, mais
**il ne te donnera pas la solution**, c'est délibéré et le filtre est automatique.

Tu peux joindre ton code et le contenu de la console à ta question, avec les cases prévues.
Fais-le, une question accompagnée du message d'erreur reçoit une bien meilleure réponse.

L'aide devient plus détaillée à mesure que tu avances dans le parcours.

Le tuteur est optionnel. S'il n'est pas configuré sur ta machine, l'atelier fonctionne
normalement, tu perds seulement ce bouton.

---

## Où en est ta progression

Elle est enregistrée sur ta machine, dans le dossier de l'atelier, et nulle part ailleurs. Rien
n'est envoyé sur internet.

Deux conséquences. Si tu changes d'ordinateur, ta progression ne suit pas. Et si tu supprimes
le dossier, tu repars de zéro.

**Garde le dossier de l'atelier tel quel.** Si tu veux sauvegarder ton travail, copie le
dossier entier, pas seulement tes fichiers `.c`.

---

## Questions fréquentes

**La fenêtre de l'énoncé est trop petite.** Tire la séparation entre l'énoncé et l'éditeur pour
l'agrandir.

**J'ai perdu mon code en changeant d'exercice.** Chaque exercice garde son propre code. Reviens
sur l'exercice, il est là.

**La porte refuse alors que mon programme a l'air bon.** Lis le message en entier. Il dit
exactement quel morceau manque dans ta sortie. Le plus souvent c'est un détail d'affichage,
une majuscule, un espace, un mot au singulier au lieu du pluriel.

**Rien ne compile, même le code de départ.** Lance `diagnostic.bat` et montre le résultat à ton
enseignant. Le compilateur n'est probablement pas trouvé.

**Le tuteur ne répond pas.** Il n'est pas installé sur cette machine. Le reste de l'atelier
marche.
