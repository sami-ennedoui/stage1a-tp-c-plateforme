# Énoncés exacts du BE C (recopiés du PDF de slides)

Source : `[N7-FISE-1A][BE][Introduction Programmation][2023-2024].pdf`.
Recopie mot pour mot des slides d'énoncé (slides 11 à 19). La numérotation, les
noms de types, les formats et les renvois « slides X-Y » sont conservés tels quels.

Attention au mapping : les dossiers de corrigé sont nommés par thème, pas dans
l'ordre des slides. Chaque section indique le corrigé réellement associé.

---

## Exercice 1 — Découverte LANGAGE C : Les types de variables en C  (corrigé : ex01_types, slide BE #11)
**Énoncé exact :**
1 – Créez un programme principal ou vous déclarez et initialisez une variable de type `short` , une variable de type `int` , une variable de type `char`, une variable de type `float` et une variable de type `double`. `slides 8-10`
`short,int,float,char, double`

2 – Utiliser les `printf` et `scanf` associés à ces différents types de variable ( `%c`  , `%f`  ,`%i`, `%d`, `%e`). `slides 23-25`

**En plus dans le corrigé (-> approfondissement) :**
Le corrigé affiche les `sizeof` de chaque type (tailles en octets) et illustre la troncature du `char` initialisé à 320, qui donne 64 (on ne garde que les 8 bits de poids faible).

---

## Exercice 2 — Découverte LANGAGE C : Les opérateurs : slide 10-13  (corrigé : ex02_operateurs, slide BE #11)
**Énoncé exact :**
1 - Créez un programme principal ou vous déclarez et initialisez 2 variables de type `int` avec a=17 et b=21.

2 - Calculer et interprétez les résultats des opérations relationnelles suivantes : a > b , a< b , a == b , a!= b .

3 - Calculer et interprétez les résultats des opérations logiques suivantes : a&&b , a||b, !a, !b .

4 - Calculer et interprétez les résultats des opérations logiques bit à bit suivantes : a  & b , a | b , a^b . `slides 15-17`
`> , < , == , != , ||, |, & , && , ^`

**En plus dans le corrigé (-> approfondissement) :**
Rien de conceptuel en plus, mais le corrigé inverse les valeurs (a=21, b=17 au lieu de a=17, b=21 comme dans l'énoncé) et le `!a` demandé est en fait codé comme `!b`.

---

## Exercice 3 — Découverte LANGAGE C : Les structures de Contrôle  (corrigé : ex03_ n'existe pas pour cet énoncé, voir note ; slide BE #12)
**Énoncé exact :**
Réaliser un programme, mettant en œuvre un switch …case, permettant à un utilisateur, à partir d'un menu de choix, de modifier une variable parmi 3 variables a,b, et c :

Les valeurs des variables sont  : a = 1.5 - b = 0.5 - c = 0.6
Que voulez vous faire ?
1. Modifier a
2. Modifier b
3. Modifier c

Si l'utilisateur répond par un choix non proposé, afficher un message d'erreur. Après la modification, affichez les nouvelles valeurs des variables. Dans un second temps, rajouterez une boucle do … while pour demander à l'utilisateur s'il désire ou non modifier une autre variable. `slides 35-40`

**En plus dans le corrigé (-> approfondissement) :**
Pas de corrigé correspondant fourni. Le dossier `ex03_structures` contient en réalité le corrigé de l'Exercice 7 (structure `struct cercle`), pas ce menu switch…case. Voir la note du rapport final.

---

## Exercice 4 — Découverte LANGAGE C : Les structures de Contrôle  (corrigé : ex07_controle, slide BE #12)
**Énoncé exact :**
Réaliser un programme permettant de faire deviner un nombre entre 0 et 100 (on utilisera une structure de contrôle do … while et un if … else if. Comptez le nombre d'essai qui a été nécessaire pour trouver le nombre et afficher le. `slides 35-40`

**En plus dans le corrigé (-> approfondissement) :**
Rien, le corrigé colle à l'énoncé (do…while + if/else if, comptage des essais). Le nombre à trouver est fixé en dur à 56 (pas de tirage aléatoire).

---

## Exercice 5 — Découverte LANGAGE C : Les structures de Contrôle  (corrigé : aucun fourni, slide BE #12)
**Énoncé exact :**
Réaliser un programme utilisant des boucles `for` permettant de dessiner avec le caractère « - » un rectangle à partir d'un nombre de lignes et de colonnes données par l'utilisateur `slides 35-40`
(exemple sur le slide : 6 lignes / 10 colonnes -> rectangle de tirets)

**En plus dans le corrigé (-> approfondissement) :**
Pas de corrigé correspondant fourni dans le dossier `be_c`. Voir la note du rapport final.

---

## Exercice 6 — Découverte LANGAGE C : Les sous-programmes  (corrigé : aucun exact ; recoupe ex09/ex12, slide BE #13)
**Énoncé exact :**
On considère un rectangle de largeur `int Larg` et de longueur `int Long`. `slides 41-48`

Réalisez un sous programme SP_AFFICHE permettant **d'afficher** la largeur et la longueur de ce rectangle

On rajoute dans le programme principal une variable `int Aire` qui devra contenir l'aire du rectangle. Réalisez un sous programme SP_CALCUL_AIRE permettant de calculer l'air du rectangle et de renvoyer l'info vers le programme principal. Affichez cette aire depuis le programme principal

On veut réaliser un sous programme SP_MODIF_RECTANGLE permettant de **modifier** les dimensions du rectangle. Le sous-programme doit avoir un droit de modification sur ces variables **(IN/OUT)** donc il faut utiliser **un passage par adresse**.

- Afficher dans le programme principal les adresse des variables `Larg et Long`.
- Ecrire le sous-programme SP_MODIF_RECTANGLE pour qu'il puisse recevoir et manipuler les adresses de Larg et Long et vérifier par un affichage dans ce sous-programme que les adresses reçu sont les bonnes.
- Effectuer le calcul de l'aire

Utiliser votre sous-programme SP_AFFICHE dans le programme principal pour afficher les nouvelles dimensions et SP_CALCUL_AIRE pour calculer la nouvelle aire du rectangle

On rajoute dans le programme principal une variable `int Perimetre.` Réalisez un sous programme SP_CALCUL_AIR_PERIMETRE permettant de calculer à la fois l'air et le périmètre du rectangle. Affichez ces infos depuis le programme principale

**En plus dans le corrigé (-> approfondissement) :**
Pas de corrigé dédié à ce rectangle multi-sous-programmes. Le thème (sous-programmes, passage par valeur/adresse) est couvert par `ex09_sousprog` (droite y=a*x+b), `ex10_passage_valeur` et `ex11_sousprog2`. Voir la note du rapport final.

---

## Exercice 7 — Découverte LANGAGE C : Les structures de variables  (corrigé : ex03_structures, slide BE #14)
**Énoncé exact :**
1  - Construire **un nouveau type de variable** nommé `rectangle` à l'aide d'une **structure** permettant de stocker les informations relatives à la description du précédent rectangle : longueur, largeur, aire périmètre.

2 – Déclarer une nouvelle variable de **type rectangle** nommé `mon_rectangle1` dans le programme principal et initialiser les valeurs de la largeur et de la longueur.

3 - A partir de la connaissance de la largeur et de la longueur, remplir les champs aire et périmètre de votre variable `mon_rectangle1`

4 – Réaliser un sous-programme SP_AFFICHE permettant d'afficher l'ensemble des champs de la variable `mon_rectangle1`  (longueur, largeur, aire périmètre)

5 – Réaliser un sous-programme **SP_MODIF_RECTANGLE** permettant de **modifier** la largeur et la longueur du rectangle et de mettre à jour les valeurs de l'air et du périmètre. Vous utiliserez alors dans votre programme principal **SP_AFFICHE** pour vérifier que les modifications ont été effectuées. `slides 18-21`
`struct, typedef`

**En plus dans le corrigé (-> approfondissement) :**
Le corrigé `ex03_structures` porte sur un **cercle** (rayon, diamètre, aire, périmètre) et non sur le rectangle demandé, et il fait EN PLUS une saisie clavier du rayon au `scanf` puis un recalcul/affichage. La structure `typedef struct` est bien illustrée, mais sans les sous-programmes SP_AFFICHE / SP_MODIF_RECTANGLE demandés.

---

## Exercice 8 — Découverte LANGAGE C : Les tableaux  (corrigé : ex05_tableaux, slide BE #15)
**Énoncé exact :**
1- Déclarez un tableau de 5 nombres entiers et initialisez-le.
2- Afficher l'adresse à laquelle est stocké le tableau. Affichez les adresses de toutes les cases du tableau ainsi que les valeurs contenues dans les emplacements 0 à 4.
3- Essayer de remplir une case qui est en dehors de l'espace du tableau. Que se passe-t-il ? `slides 31-34`

**En plus dans le corrigé (-> approfondissement) :**
Le corrigé sur-dimensionne volontairement le tableau à 16 cases (au lieu de 5) pour pouvoir écrire hors des 5 cases utiles sans planter, et commente le fait que le C ne vérifie pas les bornes (DANGER).

---

## Exercice 9 — Découverte LANGAGE C : Les tableaux de caractère  (corrigé : ex06_tableaux2, slide BE #15)
**Énoncé exact :**
1- Déclarez un tableau de 6 char et initialisez-le avec une chaine de caractère `char chaine[6]="Salut"`. Le calculateur insert automatiquement le caractère \0 dans la case 5 ( [0]=S,[1]=a,[2]=l,[3]=u,[4]=t,[5]=\0 ) pour indiquer la fin de la chaîne de caractère. Il faut donc prévoir dans la taille du tableau une case de plus pour ce caractère spécial.
2- Afficher la chaine de caractère en utilisant `%s` dans la fonction `printf`.
3- Afficher l'adresse à laquelle est stocké le tableau.
4- Réaliser une interaction clavier pour changer la chaine de caractère stockée ( `scanf avec un %s` ) `slides 31-34`

**En plus dans le corrigé (-> approfondissement) :**
Rien de conceptuel en plus, mais le corrigé commente pourquoi on écrit `scanf("%s", chaine)` sans `&` (le nom du tableau est déjà une adresse) et signale le débordement possible si la chaîne saisie dépasse 5 caractères (DANGER).

---

## Exercice 10 — Découverte LANGAGE C : Ecriture dans un fichier en mode Texte  (corrigé : ex13_fichier, slide BE #15)
**Énoncé exact :**
1 - Réaliser un programme capable d'enregistrer dans un fichier texte (dont le nom sera demandé à l'utilisateur) le contenu d'un tableau sous la forme :

tab[0] = xx
tab[1] = xx
tab[2] = xx
tab[3] = xx

`slides 53-55`

2 – Vérifier la présence du fichier sur le disque de votre machine et ouvrer le avec un éditeur de texte pour contrôler son contenu

**En plus dans le corrigé (-> approfondissement) :**
Le corrigé ajoute un test d'erreur sur `fopen` (si le pointeur de fichier est `NULL`, message d'erreur et `return 1`) et un message de confirmation à l'écran, deux points non demandés par l'énoncé.

---

## Exercice 11 — Découverte LANGAGE C : Les sous-programmes  (corrigé : ex09_sousprog, slide BE #16)
**Énoncé exact :**
Réalisez un sous-programme permettant de calculer, à partir d'une équation du type y= a*x + b, la valeur y connaissant x. La définition complète du sous-programme est donnée ci-dessous. Illustrez son utilisation dans un programme principal.

//============================================================
// nom :  fonction calculer_y
// sémantique : calcul de la coordonnée y connaissant x
// paramètres :
// a  : IN réel – valeur du coefficient directeur
// b : IN réel – valeur du de l'ordonnée à l'origine
// x : IN réel – valeur de l'abscisse
// y : OUT réel - valeur de l'ordonnée
// pré-condition : a, b et x initialisés
// post-condition : aucune
//============================================================
// Tests : a=4, b=3, x=2, solutions y = 11
// ============================================================

FONCTION calculer_y  (a,b,x ( IN) : réel ) RETOURNE réel y

Variable y : reel

DEBUT Algorithme

y = a * x + b

Retourner y

FIN Algorithme

**En plus dans le corrigé (-> approfondissement) :**
Rien, le corrigé colle à l'énoncé et reprend les valeurs de test (a=4, b=3, x=2 -> y=11).

---

## Exercice 12 — Découverte LANGAGE C : Les sous-programmes  (corrigé : ex10_passage_valeur, slide BE #17)
**Énoncé exact :**
Réalisez une procédure en mettant en œuvre un passage par valeur afin de calculer et d'afficher le produit et la somme de deux valeurs entières val_a, val_b. La définition complète de ce sous-programme est donnée ci-dessous. Illustrez l'utilisation de cette procédure dans un programme principal.

//============================================================
// nom :  procedure calculer_produit_somme
// sémantique : calcul de la somme et du produit de 2 nombres
// paramètres :
// a : IN réel – nombre 1
// b : IN réel – nombre 2
// pré-condition : a et b initialisés
// post-condition : somme et produit affichés
//============================================================
// Tests : a=3 b=2 ; solutions produit = 6 , somme  = 5
//============================================================

PROCEDURE calculer_produit_somme  ( a,b  (IN) : réel )

Variables : produit, somme : réels

DEBUT Algorithme

produit = a * b
somme = a + b

Afficher la valeur de produit
Afficher la valeur de somme

FIN Algorithme

**En plus dans le corrigé (-> approfondissement) :**
Rien, le corrigé colle à l'énoncé (passage par valeur, calcul et affichage de somme et produit, test a=3/b=2).

---

## Exercice 13 — Découverte LANGAGE C : Les sous-programmes  (corrigé : ex11_sousprog2, slide BE #18)
**Énoncé exact :**
3- Réalisez une procédure mettant en œuvre un passage par adresse permettant de permuter circulairement trois entier val_a, val_b, val_c qui lui sont donnés en arguments. La définition de ce sous-programme est donnée ci-dessous, Illustrez l'utilisation de cette procédure dans un programme principal.

//============================================================
// nom :  permuter_valeur
// sémantique : permute circulairement les 3 valeurs qui lui sont envoyés
// paramètres :
// val_a : IN/OUT réel – valeur du nombre 1
// val_b : IN/OUT réel – valeur du nombre 2
// val_c : IN/OUT réel -  valeur du nombre 3
// pré-condition : val_a, val_b et val_c initialisés
// post-condition : aucune
//============================================================
// Tests : val_a =3 , val_b =5, val_c = 1  ; solutions :  val_a =1 , val_b =3, val_c = 5
//============================================================

PROCEDURE permuter_valeur   (val_a , b , c  (IN / OUT) : réel )

Variable temp : réel

DEBUT Algorithme

temp =  val_a ;
val_a =  val_c ;
val_c =  val_b ;
val_b =  temp ;

FIN Algorithme

**En plus dans le corrigé (-> approfondissement) :**
Rien, le corrigé colle à l'énoncé (permutation circulaire par pointeurs, test val_a=3/val_b=5/val_c=1 -> 1/3/5).

---

## Équation du second degré — Programmation : Résolution d'une équation du second ordre  (corrigé : ex_second_degre, slide BE #19)
**Énoncé exact :**
A partir des algorithmes dont vous avez la correction sous moodle , programmer en C cette application permettant de résoudre une équation du second ordre

**En plus dans le corrigé (-> approfondissement) :**
L'énoncé du slide est volontairement minimal (renvoi vers les algorithmes Moodle). Le corrigé fait tout le travail : quatre sous-programmes (saisie des coefficients avec contrôle a≠0, calcul du déterminant, calcul des racines, affichage), gestion des trois cas de discriminant (>0, =0, <0) avec racines complexes (parties réelle et imaginaire), et affichage du déterminant en `%e`.

---
