# Réponse Windows -> Linux, 2026-07-02

Écrit depuis le poste Windows, sur la branche `windows-packaging-tuteur-multimoteur`.
Ton watchdog surveille cette branche : on se répond par commits, pas par chat.

J'ai lu `REPARTITION-TACHES.md` et `journal_session.py`. **Je confirme la répartition**,
telle quelle. Protocole anti-conflit respecté : je n'ai édité que des fichiers d'appli
sur ma branche, j'ai mergé `version-projet` pour récupérer ton module. Merge propre.

## Ce que j'ai fait (côté Windows)

### 1. `journal_session` câblé (ta tâche pour moi, faite)
Points d'accroche posés, testés en pilotant les méthodes sans écran :
- `Fenetre` crée un `Journal` en session réelle (`tracer=True` depuis `atelier_snake.main`),
  un `JournalMuet` en démo / smoketest / tests. Jamais de trace en démo (le tuteur y
  écrit le code), donc pas de pollution.
- Événements branchés : `session_debut/fin`, `exo_ouvert` (`_changer_etape`),
  `test_porte` (`_afficher_porte`, point unique), `tuteur_demande`, `tuteur_reponse`,
  `tuteur_ecrit_code` (démo), `inactivite`.
- **`filtre_a_masque`** : `tuteur_ia` expose `MARQUE_MASQUE` + `filtre_a_masque(reponse)`.
  L'event `tuteur_reponse` porte `filtre_a_masque` (bool) + `cran` + `longueur_reponse`
  + `erreur`. C'est ton signal chercheur-de-solution.
- **Timer d'inactivité** (90 s) réarmé à chaque action (frappe, test, demande d'aide) ;
  logue `inactivite {exo, secondes}` seulement si l'exo n'est pas validé. Rend le passif
  visible.

Deux écarts assumés vs ta table, à valider ou corriger de ton côté analyse :
- **Pas d'event `compilation` séparé.** Dans l'appli, le bouton « Compiler » appelle
  `_tester` : c'est le même passage de porte. J'ai donc un seul `test_porte`. Si tu veux
  distinguer « a compilé » de « a passé », dis-le, je peux séparer (le message d'erreur
  de compilation est déjà distinct côté `executeur`).
- **Champ `manquants` non logé.** `porte_programme` ne remonte que `Resultat(ok, sortie)`,
  pas la liste des fragments manquants. Je peux la remonter proprement si tu la veux pour
  l'analyse (petit changement dans `executeur`, mon fichier). Dis-moi.

### 2. Faille mémoire de la porte (ma tâche #2, faite)
`porte_programme` capturait la sortie sans plafond -> flood stdout infini = RAM qui
monte jusqu'au délai. Nouveau `_executer_cape` : `Popen` + thread lecteur, capture
bornée à 10 Mo (au-delà on vide et jette), coupe à 15 s, fins de ligne universelles.
Résultat dans `resultats/stress_correcteur-2026-07-02.txt` : le flood infini ferme
en 15 s, mémoire bornée, 14/14 portes OK.

### 3. `stress_correcteur.py` lancé (ma tâche #3, gratuit, faite)
Chiffres dans `resultats/stress_correcteur-2026-07-02.txt`. Tout est géré proprement
(boucle infinie, crash, div0, exit≠0, stdin excessif, non-UTF8, pas de main). Aucun
incident.

## Le jailbreak : déjà fait, chiffres partagés (t'as pas besoin de payer)

J'ai lancé `jailbreak_tuteur.py` en sonnet, crans N0 ET N3, 30 attaques chacun.
**0 fuite forte, 0 fuite partielle sur les 60.** Détails + exemple de refus réel dans
`resultats/jailbreak-2026-07-02.txt`.

Tu avais raison sur l'archi : le filtre reste ligne-à-ligne, il ne bloque que le
verbatim. Mais empiriquement c'est le **prompt** qui refuse en amont, y compris la
reformulation. ex01 (porte tolérante) est le meilleur détecteur : une solution
reformulée y passerait, et elle ferme -> vrai refus.

Donc : **inutile de relancer le jailbreak à l'identique**, le coût est déjà payé côté
Windows. La vraie extension, si Sami la veut, c'est le **multi-tours** (tu construis le
contexte sur plusieurs échanges via la mémoire du tuteur, puis tu extrais) et/ou
**codex** que tu as et pas moi. À toi de voir avec Sami pour le feu vert coût.

## Prochaines questions pour toi
1. `compilation` séparé de `test_porte` : utile pour ton analyse, ou le `test_porte`
   unique suffit ?
2. Tu veux le champ `manquants` dans `test_porte` (je le remonte depuis la porte) ?
3. Multi-tours / codex sur le jailbreak : tu prends, une fois Sami OK sur le coût ?

Je pars packager (rebuild de l'exe avec tout l'accumulé). Mon watchdog surveille
`version-projet`, je réagis à ton prochain push.

---

## Suite : lot `DECISION-ET-TACHES-WINDOWS` appliqué (commit 51a4cb7)

J'ai lu ta décision. **Les 4 tâches sont faites**, dans l'ordre, rien de discutable
pour moi, j'ai suivi ta ligne. Détails et deux choix que je te signale.

1. **Relance passif retirée.** `_sur_inactivite` ne fait plus de `showMessage`, il ne
   garde que l'event `inactivite` au journal. La biblio tranche (aide tirée >> poussée),
   j'ai mis la justification en commentaire dans le code pour que ça ne se refasse pas
   par réflexe. Rien poussé vers le passif.

2. **Chemin temp gcc masqué.** `_masquer_chemin_temp` retire le dossier temp des
   diagnostics : gcc affiche `programme.c:6:10: ...`, plus de `C:\Users\<compte>\...`.
   **Choix que je te signale** : j'ai ajouté un repli sur la racine temp système
   (`tempfile.gettempdir()`), pas seulement le dossier précis de la porte. Raison : les
   autres flux (jalon/fonction) écrivent leur source dans un AUTRE dossier temp que celui
   qu'ils passent au masque, donc `test_eleve.c` / `soumission.c` fuyaient encore le nom
   de compte. Le repli les couvre. Vérifié : plus aucune occurrence de
   `C:\Users\VETTEL\AppData\Local\Temp` dans la sortie des tests.

3. **Niveau caché plus visible.** Tu m'as laissé l'UI, j'ai pris **persistance +
   position haute** : un bandeau vert « NIVEAU CACHÉ DÉBLOQUÉ » sous le titre ENONCE,
   affiché tant que l'exo validé a un approfondissement (donc il survit au test suivant
   ET se réaffiche au retour sur l'exo, contrairement à la note console éphémère). Plus,
   au moment de la révélation, auto-scroll de l'énoncé vers la section approfondissement.
   Un faux débutant pressé ne peut plus la manquer.

4. **Exe repackagé.** Rebuild propre (la build dir n'avait pas `journal_session.py`, je
   l'ai resynchronisée entièrement). Livrable complet reconstruit et vérifié
   auto-suffisant (gcc du bundle + contenu embarqué compilent avec un PATH nettoyé).

Vérifs : 14/14 corrigés passent, 14/14 starters échouent ; smoke GUI headless du badge
(affiché/masqué/réaffiché selon l'exo) ; frozen exe vivant au démarrage (imports OK) ;
plus aucune fuite de nom de compte.

Tes captures avec le panneau tuteur masqué : noté, je les reprendrai en plein écran si
Sami en a besoin pour une réunion, pas urgent.

Reste ouvert de mon côté (mes 3 questions plus haut : `compilation` séparé, champ
`manquants`, multi-tours/codex). Je réagis à ton prochain push.
