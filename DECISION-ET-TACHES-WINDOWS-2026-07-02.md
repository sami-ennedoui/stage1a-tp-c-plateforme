# Décision de conception + lot de travail pour le Claude Windows

Écrit le 2026-07-02, poste Linux. Deux choses : une décision qui annule un de tes
correctifs, et un lot de travail clair pour la suite.

## 1. Décision : on retire la relance automatique du passif

Sami a confronté le design à notre biblio et il **refuse le coup de pouce
automatique à l'écran pour le passif**. Concrètement, le `showMessage` que tu as
ajouté dans `_sur_inactivite` (ton correctif 132bc1a, le message « Bloqué ? Clique
Demander de l'aide... » après 90 s) est à **retirer**.

Ce n'est pas un caprice, c'est fondé. Deux résultats de notre corpus visent
exactement ce profil.
- Prather 2024 « widening gap » : l'IA aggrave les difficultés métacognitives de
  l'étudiant qui peine, c'est-à-dire le passif, avec illusion de compétence chez les
  plus faibles.
- Shen-Tamkin (Anthropic) : l'aide **poussée** ou déléguée détruit l'apprentissage,
  24 à 39 % au quiz, là où la question **tirée** par l'étudiant le préserve, 65 à
  86 %. La ligne qui décide, c'est pull contre push.

Pousser de l'aide vers le passif, c'est appliquer l'IA au profil et dans le mode où
elle nuit le plus. Donc on l'écarte.

**Ce qu'on garde**, en revanche, c'est la **mesure** : l'événement d'inactivité au
journal. Il rend le passif visible pour qu'un enseignant le récupère, ce qui est
l'axe « instrumenter le processus » de notre synthèse. Garde donc l'`event`
d'inactivité au journal, ne retire que la relance visuelle. Et ne muscle pas ce
nudge, c'était la piste opposée.

## 2. Lot de travail, dans l'ordre

1. **Retirer la relance passif à l'écran.** Enlève le `showMessage` de
   `_sur_inactivite`, garde l'`event` d'inactivité au journal. C'est tout pour le
   passif.

2. **Nettoyer le chemin temporaire dans les erreurs gcc.** Aujourd'hui l'erreur de
   compilation affiche le chemin absolu du fichier temp, du genre
   `C:\Users\<compte>\AppData\Local\Temp\...\programme.c`. Deux problèmes : c'est long
   et intimidant pour le débutant, et surtout **ça fait fuiter le nom de compte
   Windows** dans chaque message. Remplace ce chemin par un nom neutre, par exemple
   `programme.c`, dans la sortie montrée à l'étudiant. C'est le point le plus rentable,
   il touche le débutant vrai et le bricoleur, et il règle un souci de confidentialité.

3. **Rendre le niveau caché plus visible à la révélation.** Le faux débutant rate
   l'approfondissement parce qu'il apparaît sous la ligne de flottaison de l'énoncé et
   que le message de révélation est éphémère. C'est le point de conception le plus
   important pour ce profil. Rends la révélation plus persistante ou plus haute, à toi
   de voir l'UI, l'idée est qu'un faux débutant pressé ne puisse pas la manquer.

4. **Empaquetage exe.** Une fois 1 à 3 faits, tu peux enchaîner sur le packaging.

## 3. Captures

Deux de tes captures ont le panneau tuteur masqué par ta propre fenêtre d'éditeur.
Si elles doivent servir en réunion, reprends-les en plein écran. Sans urgence.

Pousse sur ta branche quand c'est fait, mon watchdog me préviendra. Si un point te
paraît discutable, écris-le en réponse plutôt que de le trancher seul, on validera
avec Sami.
