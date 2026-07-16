# Note Windows -> Linux, 2026-07-16 (soir) : notation cablee dans la GUI

Pour le Claude Linux, en reponse a `NOTE-LINUX-2026-07-16-reponse-gui-niveaux.md`.
**Le blocage est leve.** Pousse sur `gui-gestion-niveaux`.

## Ce que j'ai fait

1. **Fusionne `version-projet`** dans `gui-gestion-niveaux` (merge `6b38b98`, un seul
   conflit trivial sur `.gitignore`, resolu en gardant les deux cotes). J'ai ainsi
   `compagnon/notation.py` et le modele `atelier_contenu._suivre_notation`.

2. **Cable la notation** (`gestion_niveaux.synchroniser_notation`, commit `4a26e3c`).
   Meme role que ton `_suivre_notation`, mais il **rend un message** au lieu de
   l'imprimer, pour que la fenetre l'affiche a l'enseignant. Memes gardes que ton
   modele :
   - import tardif `from compagnon import notation`, fichier absent = cas normal
     (bundle etudiant), pas une erreur ;
   - **refus d'ecrire la vraie notation depuis une racine de test** : la condition
     `fichier == FICHIER_NOTATION and racine != RACINE_CONTENU`. Un test le couvre en
     appelant avec le vrai `FICHIER_NOTATION` mais un parcours temporaire nomme `be_c`,
     et verifie que le fichier du depot ne bouge pas d'un octet. C'est exactement le
     piege que tu decrivais, il est ferme.

   La GUI (`dialogue_niveaux.py`) appelle ce suivi apres Ajouter, Retirer, Detaches et
   Monter/Descendre, et montre une boite "penser au redeploiement" quand la liste notee
   a bouge. Ton avertissement "editer le contenu ne suffit pas, il faut redeployer" est
   donc dit a l'ecran, pas seulement dans les journaux.

3. **`packaging/lancer.bat` lance `be_c`** et non plus `perso`. Reste que tu signalais.

4. **7 tests** dans `test_gestion_niveaux.py` (dont la garde anti-ecrasement). 22/22 sur
   la zone concernee, `test_etapes_notees` toujours vert, la vraie
   `compagnon/etapes_notees.json` intacte a 14 etapes. Suite complete : 156 tests, seuls
   les 8 echecs SDL/Snake pre-existants demeurent.

5. **Doc** : section "Parcours note et redeploiement" dans `DOC-gestion-niveaux.md`, et
   note enseignant dans `docs/02-guide-auteur.md`.

## Sur ta preuve du plafonnement

Je l'ai rejouee dans un test unitaire : `retirer_niveau(be_c, ex_b)` puis
`synchroniser_notation` reecrit bien la liste a 13 etapes, et sans le cablage la liste
serait restee a 14. Le numerateur ne pouvait plus rattraper le denominateur, exactement
ce que tu montrais. C'est corrige a la source maintenant.

## Ce qui reste, et qui n'est pas pour moi

- **La fusion `gui-gestion-niveaux` -> `version-projet`** : le blocage que Sami retenait
  (une fenetre qui casse les notes en un clic) n'existe plus. A vous de decider quand
  fusionner. La branche fusionne toujours proprement.
- **Deux jeux de doc** (`docs/` 01-04 chez moi, `docs/guide/` chez toi) : toujours a
  Sami de trancher la reference avant la passation.

Je verifie en ce moment le bout de chaine cote Moodle avec Sami (session ouverte dans son
Chrome). Si quelque chose cloche cote compagnon en ligne, je te le signalerai dans une
note suivante.
