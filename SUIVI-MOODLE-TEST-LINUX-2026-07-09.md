# Remontée de progression vers Moodle, test sur Linux du 9 juillet 2026

Ce document rend compte du test de bout en bout de la remontée automatique de
progression du TP C vers le carnet de notes Moodle, réalisé sur Linux. Il sert
aussi de mode d'emploi pour refaire la vérification.

## Le principe

L'atelier de bureau garde un bouton « Connecter à Moodle ». L'étudiant lance
l'activité LTI depuis le cours, Moodle affiche un code court, l'étudiant colle ce
code dans l'atelier. À partir de là, chaque exercice validé remonte tout seul.
Un petit service en ligne, le compagnon, reçoit ces validations, calcule un score
et l'écrit dans le carnet par le protocole AGS de LTI 1.3.

Côté serveur, le compagnon tourne sur Render à l'adresse
`https://compagnon-tp-c.onrender.com`. Côté cours, l'outil est déclaré dans le
bac à sable « BAS stage QCM et IA », identifiant de cours 4665, avec l'activité
« Test » et la ligne de note 16842.

## Ce qu'on a testé

Le test appelle exactement les fonctions que déclenchent le bouton et la
validation d'un exercice dans l'atelier :

- `moodle_sync.appairer(code)` pour le bouton « Connecter à Moodle »,
- `moodle_sync.signaler_porte(id_etape)` après la validation d'une étape.

Le parcours visé est `be_c`, celui qui part aux étudiants, et l'étape de test est
`ex01_types`, le premier exercice du BE. Le code d'appairage a été obtenu en
lançant l'activité « Test » dans Moodle, il est valable dix minutes et ne sert
qu'une fois.

## Le résultat, la chaîne fonctionne

Chaque maillon a répondu comme prévu.

- L'appairage a réussi. Le compagnon a rendu un jeton permanent et l'atelier l'a
  rangé dans son fichier de synchronisation.
- La validation de l'étape a été acceptée. La file locale s'est vidée, signe que
  le compagnon a répondu 200.
- Le score a été calculé correctement. Pour une étape sur quatorze, le compagnon
  a renvoyé `{"recu": 1, "score": 7.1}`, soit 100 × 1 / 14.
- La poussée AGS a bien atteint Moodle. Le compagnon a obtenu le jeton OAuth du
  service de notes, puis a envoyé le score à la bonne ligne de note.

La preuve de la poussée se lit dans les journaux du serveur :

```
POST https://moodle.inp-toulouse.fr/mod/lti/services.php/4665/lineitems/16842/lineitem/scores?type_id=4
→ 400 - []
ERROR:compagnon:poussée AGS échouée pour 5375
```

L'échec 400 survient au moment de l'écriture de la note, pas avant. Le jeton du
service AGS a donc été obtenu et accepté, et la requête a atteint la bonne ligne
de note. Tout le circuit technique est prouvé.

## La case du carnet et le compte enseignant

La case du carnet reste vide dans ce test, et c'est normal. Le sub 5375 est le
compte enseignant de Sami. Moodle refuse d'écrire une note pour un compte qui
n'est pas notable dans le cours, ce que vérifie sa règle
`is_user_gradable_in_course`. Un enseignant n'a pas de ligne dans le carnet, donc
la note n'a nulle part où se poser et Moodle répond 400 avec un corps vide.

Ce n'est pas un défaut du code. Un vrai étudiant est notable, sa note s'écrira
sans rien changer. La confirmation visuelle du chiffre dans le carnet se fera
au premier étudiant de la promotion. Prendre le rôle « Étudiant » depuis le
compte enseignant ne suffit pas, c'est un aperçu de session qui ne rend pas le
compte notable. On ne teste pas avec un autre compte, le compte Moodle est
strictement personnel.

## Le correctif appliqué avant le test

En préparant le test, on a trouvé une erreur de configuration. Le dénominateur
du score, la variable `TOTAL_ETAPES` du serveur, valait 6 alors que le parcours
`be_c` compte quatorze étapes. Avec 6, un étudiant aurait affiché 100 % dès sa
sixième étape sur quatorze, une note fausse et gonflée. La valeur a été corrigée
à 14 sur Render, le service a redéployé, et le score de 7,1 % pour une étape
confirme que la correction est bien prise en compte.

## Refaire la vérification

Le déroulé réel côté étudiant est le suivant.

1. Ouvrir l'activité « Test » dans le cours Moodle. La page du compagnon affiche
   un code de sept caractères du style `72W-HWD`.
2. Lancer l'atelier, cliquer sur « Connecter à Moodle », coller le code.
3. Faire et valider un exercice. La progression remonte toute seule.

Pour une vérification technique, on lit les journaux du serveur avec l'API Render
et on cherche la ligne de poussée AGS. Une écriture réussie ne laisse pas de
trace d'erreur, une écriture refusée laisse la ligne `poussée AGS échouée`.

## Ce qui reste

- La confirmation visuelle du score dans le carnet, au premier vrai étudiant.
- Les tests et la documentation sur Windows, sur un poste avec droits
  administrateur, à faire ensuite.
