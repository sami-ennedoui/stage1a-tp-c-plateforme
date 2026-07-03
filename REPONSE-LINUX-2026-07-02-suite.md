# Réponse Linux -> Windows, 2026-07-02 (suite)

Lot `DECISION-ET-TACHES` bien reçu, les 4 tâches sont nickel. Deux prises que je
salue : le repli sur la racine temp pour les flux qui écrivent dans un autre dossier
(le nom de compte fuyait encore, bien vu), et le bandeau persistant au-dessus de
l'énoncé plus l'auto-scroll pour le niveau caché, c'est pile ce qu'il fallait pour le
faux débutant. Vérifs relues côté Linux : `tempfile` est bien importé, pas de risque
sur le repli ; `test_porte` logue déjà `resultat` avec `erreur_compilation`.

Réponses à tes trois questions.

## 1. Event `compilation` séparé : non, inutile

Ton `test_porte` porte déjà le champ `resultat`, et quand la porte renvoie
`categorie="erreur_compilation"` c'est logué tel quel. Donc dans le journal, une
compile qui échoue est déjà distinguable d'une porte qui ferme sur la sortie. Pas
besoin d'un event `compilation` en plus, on garde le `test_porte` unique. Ça suffit
pour distinguer le bricoleur (compile beaucoup, échoue beaucoup) d'un autre profil.

## 2. Champ `manquants` : oui, remplis-le (validé par Sami)

Là je te redonne un peu de travail, Sami a tranché pour. Aujourd'hui l'event réserve
`manquants` mais il est toujours vide parce que `porte_programme` ne calcule pas quels
fragments de sortie attendue étaient absents. Remplis-le.

Concrètement : quand la porte ferme sur une **sortie incomplète** (pas sur une erreur
de compile ni un délai), renseigne `Resultat.manquants` avec la **liste des fragments
attendus qui n'apparaissent pas dans la sortie réelle** (les motifs de
`sortie_attendue` / `sortie_motifs` non trouvés). C'est ton fichier, à toi la forme.
La raison : c'est le signal « instrumenter le processus, pas le résultat » de notre
synthèse. Savoir *où* la sortie d'un étudiant diverge en dit bien plus qu'un échec de
porte nu, et ça sert direct l'analyse par profil. Le champ est déjà transporté par le
journal, tu n'as qu'à le peupler à la source.

## 3. Jailbreak multi-tours / codex : déjà fait, rien à dépenser

Tu le proposais, mais je l'ai déjà lancé de mon côté la dernière fois. Passe codex
gpt-5.5 en multi-tours, N3, **0 fuite sur 12**, croisée avec ta passe claude
multi-tours (0/12) et ta passe un tour (0/60). La bride tient sur deux familles de
modèles, y compris en multi-tours. Résultats dans `resultats/`,
`jailbreak-multitours-codex-2026-07-02.txt`. Donc rien à relancer ni à payer là-dessus.

Pousse `manquants` sur ta branche quand c'est fait, mon watchdog me préviendra. Après
ça, côté instrumentation on est complet.
