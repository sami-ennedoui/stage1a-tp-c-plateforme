# Atelier TP C, guide de l'etudiant

Un atelier de bureau pour Windows : 14 exercices d'introduction au langage C. Pour
chaque exercice vous ecrivez un petit programme complet, vous cliquez pour compiler et
tester, et une porte s'ouvre quand la sortie est correcte.

![Vue d'ensemble de l'atelier](captures/01-vue-ensemble.png)

## A quoi ca sert

Les 14 exercices couvrent les bases du langage C : les types de variables et leur
format d'affichage, les operateurs, les structures de controle, les sous-programmes et
le passage par valeur, les structures (struct), les tableaux, les tableaux de caracteres
(chaines), l'ecriture dans un fichier texte, et pour finir l'equation du second degre.

Dans l'ordre, les exercices sont :

1. Les types de variables
2. Les operateurs
3. Les structures de controle
4. Deviner un nombre
5. Les structures de controle (rectangle)
6. Les sous-programmes
7. Les structures de variables (struct)
8. Les tableaux
9. Les tableaux de caracteres (chaines)
10. L'ecriture dans un fichier texte
11. Les sous-programmes (droite)
12. Une procedure avec passage par valeur
13. Les sous-programmes (permutation)
14. L'equation du second degre

Chaque exercice est autonome : un enonce en haut, un editeur de code au centre, une
console en bas, et un panneau tuteur optionnel a droite.

## Prerequis

Un Windows 64 bits. **Rien d'autre a installer** pour le coeur de l'atelier : Python et
le compilateur gcc sont deja fournis dans ce dossier.

## Comment lancer

1. Decompressez ce dossier ou vous voulez (le Bureau, par exemple).
2. Double-cliquez sur **`lancer.bat`**.

La fenetre s'ouvre sur le premier exercice.

Si quelque chose cloche, lancez d'abord **`diagnostic.bat`** : il verifie que gcc,
Python et l'affichage repondent, et affiche un message clair. Une fenetre s'ouvre, lit
le rapport, puis appuyez sur une touche pour la fermer.

## Si Windows affiche un avertissement au lancement

L'atelier n'est pas signe par un editeur connu (c'est un projet pedagogique, pas un
logiciel commercial). Apres un telechargement, Windows peut donc afficher **« Windows a
protege votre PC »** (SmartScreen) au premier lancement. C'est attendu, ce n'est pas un
virus.

- **Pour lancer quand meme** : cliquez sur **« Informations complementaires »** puis sur
  **« Executer quand meme »**. Aucun droit administrateur n'est requis.
- **Pour eviter l'avertissement des le depart** : avant de decompresser le zip, faites un
  **clic droit sur le fichier `.zip` -> Proprietes -> cochez « Debloquer » -> OK**, puis
  decompressez. Les fichiers extraits ne declencheront plus SmartScreen.

Si votre etablissement bloque l'execution (le bouton « Executer quand meme » est absent ou
grise), c'est une politique de securite du poste : rapprochez-vous du service informatique.

## Comment ca marche, exercice par exercice

1. Lisez l'enonce en haut de la fenetre.
2. Ecrivez votre programme dans l'editeur.
3. Cliquez sur **Compiler** pour compiler et executer votre programme. La console
   affiche **uniquement la sortie** de votre programme (ou les erreurs du compilateur).
   Ce bouton **n'ouvre pas la porte** : il vous sert a voir ce que fait votre code.
4. Cliquez sur **Tester** pour lancer les verifications. Si votre sortie est correcte, la
   **porte s'ouvre** et l'exercice est valide.

![Une erreur de compilation, ligne et colonne exactes](captures/02-erreur-compilation.png)

En cas d'erreur de compilation, le message pointe la **ligne et la colonne exactes**
(par exemple `programme.c:6:10: error: ...`), sans chemin de fichier parasite qui
brouillerait la lecture.

Si la porte s'ouvre, c'est gagne. Sinon, le message vous explique precisement ce qui
manque dans votre sortie (« Il manque ceci dans ta sortie : ... »), et reaffiche la
sortie obtenue pour comparer. Les exercices sont independants : faites-les dans l'ordre
que vous voulez.

### Le niveau cache

Quand vous validez certains exercices, un **niveau cache** se debloque : un **bandeau
vert** apparait sous le titre ENONCE et un approfondissement s'ajoute au bas de l'enonce.
Il va un peu plus loin que la consigne de base, pour ceux qui veulent creuser. Tous les
exercices n'en ont pas ; quand il y en a un, il n'apparait qu'apres avoir franchi la
porte.

![Porte ouverte et niveau cache debloque](captures/03-porte-ouverte-niveau-cache.png)

## Le tuteur IA (optionnel)

Un bouton **Demander de l'aide** peut vous repondre pendant un exercice, **sans jamais
donner la solution toute faite**. Il repond court et direct, nomme ce qui cloche et le
concept en jeu, mais vous laisse ecrire la correction vous-meme : les lignes du corrige
sont automatiquement masquees dans sa reponse.

![Le dialogue Demander de l'aide](captures/04-demander-aide.png)

Vous posez votre question, choisissez le **niveau d'aide** voulu (vous pouvez demander
**moins** d'aide que le maximum debloque, de « juste un indice » a une « aide directe »),
et decidez si vous **joignez votre code** et le **rendu de la console**. Par defaut ces
deux cases sont decochees : le tuteur ne voit que l'enonce et votre question.

**Le tuteur est OPTIONNEL.** Les exercices fonctionnent entierement sans lui.

Pour qu'il s'active, il faut un **outil IA en ligne de commande** installe et connecte
avec votre propre compte. Deux outils sont reconnus automatiquement :

- **Claude Code** (commande `claude`)
- **Codex** (commande `codex`)

Si l'un des deux est present sur la machine et connecte, le tuteur s'allume tout seul au
lancement (si les deux sont presents, `claude` est choisi par defaut). D'autres outils
peuvent aussi etre utilises : c'est **votre enseignant** qui les configure. La mise en
place du tuteur (choix et configuration de la commande) est decrite dans le guide de
l'enseignant, voir **02-guide-auteur.md**.

Sans aucun outil IA, l'atelier reste pleinement utilisable, simplement sans l'aide IA.

## Les soulignements rouges pendant la frappe

Des **soulignements rouges** apparaissent sous certaines parties de votre code pendant que
vous tapez : ce sont des diagnostics en direct, qui signalent une erreur probable avant
meme de compiler. Le bundle Windows embarque ce qu'il faut, vous n'avez rien a installer.
Si jamais l'outil manque, un petit message l'indique et rien n'est casse : vous compilez et
testez exactement de la meme facon.

## En cas de probleme

- **La fenetre ne s'ouvre pas** : lancez `diagnostic.bat`, il indique ce qui manque.
- **Une erreur « gcc introuvable »** : lancez toujours l'atelier par `lancer.bat` (il
  ajoute le compilateur au PATH). Verifiez aussi que le dossier `w64devkit` est bien
  reste a cote de l'application.
- **Le tuteur reste eteint** : c'est normal si aucun outil IA n'est installe ou
  connecte. L'atelier fonctionne sans.

## Pour l'enseignant

Le reglage de l'affichage progressif ou de l'ouverture de tous les exercices, le mot de
passe auteur, la configuration de la commande du tuteur, l'ajout d'un parcours et le
suivi Moodle sont reserves a l'enseignant : voir **02-guide-auteur.md**.
