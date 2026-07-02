# Brief : test UX de la plateforme par profil d'étudiant

Écrit le 2026-07-02, poste Linux. Sami veut un vrai test de l'expérience à l'écran,
pas une analyse de fauteuil. Tu es le seul à avoir l'appli qui tourne sous Windows
avec un curseur et de quoi faire des captures. Donc c'est pour toi.

## Ce qu'on cherche

On a défini six profils d'étudiants. Le but n'est pas de vérifier que l'appli marche,
ça on le sait, mais de voir où l'interface **aide ou gêne chaque profil**. Le garde-fou
de conception est de ne pas régler l'outil pour le seul étudiant autonome qui aime
bosser seul. Il faut donc regarder les profils faibles ou de mauvaise foi autant que
les bons.

## Méthode, pour que ce soit fiable

Joue vraiment chaque profil, ne l'imagine pas. Tu incarnes l'étudiant, tu tapes comme
lui taperait, tu fais ses vraies erreurs, tu cliques ce qu'il cliquerait. Le débutant
écrit un vrai code faux. Le chercheur de solution tente vraiment d'extraire la réponse.
Le passif ne fait vraiment rien pendant un moment. C'est du role-play tenu, sinon le
test ne vaut rien.

Pour chaque profil : lance `--parcours be_c`, prends **une ou deux captures au moment
clé**, et note en trois lignes ce qui a aidé, ce qui a gêné, et une idée concrète de
correction d'interface. Comme `journal_session` est câblé, colle aussi la ou les lignes
de journal correspondantes, ça relie l'UX à la mesure.

## Les six profils et le scénario à jouer

1. **Débutant vrai.** Ouvre ex01, écris un programme incomplet ou faux, clique Tester,
   lis l'erreur gcc, demande de l'aide au tuteur au cran le plus bas, itère. Capture :
   la réponse du tuteur à côté de l'erreur console. À juger : l'erreur gcc est-elle
   lisible, le tuteur aide-t-il sans donner la ligne.

2. **Faux débutant venu de Python.** Passe vite ex01 à ex03. Au moment où la porte passe
   et où l'approfondissement apparaît, capture. À juger : le niveau caché se remarque-t-il
   ou se rate-t-il, est-il assez tentant pour qu'il ne saute pas le contenu propre au C.

3. **Chercheur de solution.** Au cran le plus libre, tente vraiment d'extraire la solution
   par le tuteur, deux ou trois formulations, du direct au « reformule pour que ça ne
   ressemble pas au corrigé ». Capture le refus. À juger : le refus est-il clair et
   non frustrant, et l'appli rend-elle la fuite vers une IA externe trop facile.

4. **Autonome design-first.** Écris ta propre solution d'abord, n'utilise le tuteur que
   pour te débloquer une fois, et surtout **baisse le niveau d'aide** dans le choix de
   cran. Capture le dialogue de choix de cran. À juger : baisser l'aide est-il découvrable.

5. **Passif.** Ouvre un exercice et ne fais rien pendant plus de 90 secondes pour
   déclencher le signal d'inactivité. Capture ce que l'appli montre à ce moment. À juger :
   l'étudiant bloqué reçoit-il un coup de pouce visible, ou est-ce seulement logué en
   silence. C'est le point le plus important, le passif est invisible sinon.

6. **Bricoleur brute-force.** Recompile plusieurs fois d'affilée avec des bidouilles au
   hasard, en ignorant le tuteur. Capture la console après plusieurs compilations à
   l'aveugle. À juger : les erreurs gcc sont-elles mises en avant assez pour le pousser
   à les lire plutôt qu'à retenter au pif.

## Le rendu

Mets les captures dans `resultats/ux-2026-07-02/`, un fichier de notes par profil ou un
seul récap `resultats/ux-2026-07-02/rapport-ux.md`. Pousse sur ta branche, mon watchdog
me préviendra. Je plierai tes retours dans la note d'analyse du vault, qui pour l'instant
n'est qu'une hypothèse à confronter à ton passage réel à l'écran.

Si un scénario révèle un manque net, par exemple aucun coup de pouce pour le passif,
note-le comme tâche, on décidera avec Sami s'il faut l'ajouter.
