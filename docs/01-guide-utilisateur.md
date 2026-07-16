# Guide utilisateur, Atelier TP C

Plateforme d'apprentissage du langage C. On y fait, un par un, les exercices du BE C :
on écrit un programme, l'appli le compile, et une porte s'ouvre quand la sortie est
correcte. Un tuteur IA aide sans jamais donner la solution.

## 1. Lancer l'appli

Double-clique sur **`Atelier.bat`** à la racine du dossier. Une fenêtre s'ouvre sur le
parcours en cours (au premier lancement, le parcours du BE C, `be_c`).

Si rien ne se passe, voir la section 6, Problèmes courants.

Pour lancer plus vite les fois suivantes : menu **Paramètres -> Emplacements et
diagnostic -> Créer un raccourci sur le bureau**.

## 2. La fenêtre

Trois colonnes :

- **À gauche, le parcours** : la liste des exercices. Chacun porte une marque :
  `[ouvert]` (disponible), `[fait]` (porte franchie), `[verrou]` (pas encore débloqué).
  Un exercice se débloque en franchissant le précédent.
- **Au centre, le travail** : l'énoncé en haut, l'éditeur de code au milieu (onglet
  « Mon code »), la console en bas.
- **À droite, le tuteur IA** : le niveau d'aide et les réponses du tuteur.

## 3. Faire un exercice

1. Clique un exercice **ouvert** dans la liste. L'énoncé s'affiche, l'éditeur se remplit
   d'un code de départ.
2. Écris ton programme dans l'éditeur.
3. Clique **Compiler** pour compiler et exécuter, ou **Tester** pour tenter la porte.
4. La console affiche le résultat :
   - **PORTE OUVERTE** (vert) : c'est réussi, l'exercice passe en `[fait]` et le suivant
     se débloque.
   - **PORTE FERMÉE** (rouge) : la console montre ce qui ne va pas (erreur de
     compilation, ou sortie qui ne correspond pas à ce qui est attendu).

Si `clangd` est installé, des soulignements signalent les erreurs de C pendant que tu
tapes. C'est optionnel : l'appli marche sans.

## 4. Le tuteur IA

Le tuteur répond à tes questions **sans donner la solution**. Il travaille par crans
d'aide, du plus discret au plus direct :

- **N0 à N2** : aide socratique, il pose des questions et oriente.
- **N3** : plus direct, mais jamais le programme complet.

Tu débloques des crans en avançant dans le parcours. Le menu déroulant à droite permet
de **redescendre** sous le cran débloqué si tu veux moins d'aide. Pour poser une
question, clique **Demander de l'aide** et écris ta question.

Le tuteur a besoin de l'outil `claude` sur le poste. S'il est absent, l'appli fonctionne
quand même, simplement sans tuteur.

## 5. Suivre sa progression, et Moodle

La progression (exercices faits, crans débloqués) est enregistrée automatiquement, tu la
retrouves au prochain lancement.

Si le cours utilise Moodle, le bouton **Connecter à Moodle** en bas à gauche permet de
coller le code d'appairage affiché par l'activité Moodle. Une fois connecté, les
exercices franchis remontent dans le carnet de notes, et le bouton affiche ton score.

## 6. Problèmes courants

- **Rien ne s'ouvre au double-clic** : Python n'est peut-être pas installé. Installe
  Python 3.12, puis relance `Atelier.bat`.
- **La compilation échoue toujours, même avec un bon code** : le compilateur `gcc` n'est
  pas trouvé. Ouvre **Paramètres -> Emplacements et diagnostic** : la ligne `gcc` doit
  être « présent ». Sinon, le dossier `w64devkit` doit être à côté de l'appli.
- **Le tuteur ne répond pas** : l'outil `claude` est absent, c'est normal si le poste ne
  l'a pas. Le reste de l'appli marche.
- **Voir où sont les fichiers** : **Paramètres -> Emplacements et diagnostic** liste tous
  les chemins utiles, chacun avec un bouton pour ouvrir le dossier.
