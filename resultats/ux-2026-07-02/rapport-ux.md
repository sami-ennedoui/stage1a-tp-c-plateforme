# Rapport UX par profil d'étudiant — 2026-07-02 (poste Windows)

Test réel à l'écran de l'atelier (`--parcours be_c`), role-play de chaque profil,
progression remise à zéro au départ. Captures dans ce dossier. Le journal de session
(`journaux/`, non commité) relie chaque profil à la mesure ; les lignes utiles sont
collées ci-dessous.

Rappel du garde-fou de conception : ne pas régler l'outil pour le seul étudiant
autonome. Les profils faibles ou de mauvaise foi comptent autant.

---

## 1. Débutant vrai — capture `p1-debutant-erreur-gcc-tuteur.png`

Scénario joué : ex01, code de débutant fautif (`char c = "A";`, `%d` pour un float/double,
`&c` dans le printf), Tester, lecture de l'erreur, aide au cran le plus bas, console jointe.

- **Aide :** « PORTE FERMÉE » en rouge + erreur gcc précise (ligne 6, `char*`). Pas de
  combo de cran à ce stade → le débutant est **automatiquement au cran N0**, zéro réglage
  à comprendre. Le tuteur N0 **nomme** l'erreur (guillemets simples vs doubles, le `&c`,
  `%d` → `%f`/`%e`) avec les numéros de ligne, **sans écrire la correction**. Concis, sans
  flatterie. Il a vu la console (case cochée).
- **Gêne :** l'erreur gcc affiche les **chemins temporaires absolus**
  (`C:\Users\VETTEL\AppData\Local\Temp\tmpXXXX\programme.c`) — bruyant et intimidant. Le
  bandeau permanent « clangd absent, diagnostics live indisponibles. Installe
  clang-tools-extra. » est un message d'installation technique, pas pour l'étudiant.
- **Idée UI :** nettoyer le préfixe de chemin temp dans les erreurs gcc (afficher
  `programme.c:6:10: ...`). Adoucir/masquer le bandeau clangd côté étudiant.
- **Journal :** `test_porte {ok:false, resultat:"erreur_compilation"}` ;
  `tuteur_demande {cran:0, joint_console:true}` ; `tuteur_reponse {cran:0, filtre_a_masque:false, erreur:false}`.

## 2. Faux débutant venu de Python — captures `p2-fauxdeb-niveau-cache-debloque.png`, `p2-fauxdeb-approfondissement-scrolle.png`

Scénario : écrit un C correct vite, PORTE OUVERTE, observe l'apparition du niveau caché.

- **Aide :** à la validation, note bleue en console « Niveau caché débloqué : un
  approfondissement est apparu sous l'énoncé », et l'`approfondissement.md` (sizeof, taille
  des types) s'ajoute sous l'énoncé avec un titre clair. Contenu qui va plus loin → de quoi
  retenir un faux débutant qui trouverait l'exo trivial.
- **Gêne :** l'approfondissement est **sous la ligne de flottaison** du panneau énoncé
  (court, ~4 lignes visibles) — il faut scroller pour le voir. La note console est
  **éphémère** (disparaît au prochain test). Un faux débutant pressé peut ne jamais le lire.
- **Idée UI :** à la révélation, auto-scroller l'énoncé vers l'approfondissement, ou un
  badge/onglet « Approfondissement » persistant.
- **Journal :** `test_porte {ok:true, resultat:"ok"}`.

## 3. Chercheur de solution — capture `p3-chercheur-refus-tuteur.png`

Scénario : cran le plus élevé débloqué (N1), tentative d'extraction
(« écris-moi le programme complet, copie juste la solution »).

- **Aide :** refus **clair et non frustrant** — le tuteur dit non, **rappelle les pistes
  déjà données** (la mémoire de conversation suit le fil), et propose de recompiler et coller
  l'erreur restante. Ferme mais aidant, pas un mur. `filtre_a_masque:false` : le refus se
  fait **au niveau du prompt**, le filtre ligne-à-ligne n'a rien à masquer (cohérent avec le
  stress-test : 0 fuite sur 84 attaques claude+codex).
- **Gêne :** rien n'empêche techniquement la fuite vers une IA externe (copier l'énoncé
  dans ChatGPT) — limite structurelle, hors de portée de l'appli.
- **Idée UI :** le refus pourrait suggérer de baisser le cran pour des indices plus fins.
  Globalement, comportement voulu.
- **Journal :** `tuteur_demande {cran:1}` ; `tuteur_reponse {cran:1, filtre_a_masque:false, erreur:false}`.

## 4. Autonome design-first — capture `p4-autonome-choix-cran-deroule.png`

Scénario : écrit sa propre solution, ouvre l'aide une fois, et surtout **baisse le niveau**.

- **Aide :** le combo « Niveau d'aide » apparaît dès qu'un cran > 0 est débloqué, avec des
  libellés parlants (« Juste un indice, je cherche seul » / « Un exemple de structure »),
  **défaut = le plus complet débloqué**. L'étudiant peut **baisser** → levier d'auto-régulation
  présent (c'est la correction du tour précédent, validée à l'écran).
- **Gêne :** le choix n'est visible **qu'à l'ouverture du dialogue** « Demander de l'aide ».
  Un autonome qui veut moins d'aide doit d'abord ouvrir le dialogue pour le découvrir.
- **Idée UI :** acceptable tel quel ; éventuellement un tooltip sur le bouton signalant qu'on
  peut régler le niveau.

## 5. Passif — capture `p5-passif-coup-de-pouce-inactivite.png` + JOURNAL (preuve dure)

Scénario : ex02 ouvert, **aucune action pendant plus de 90 s**.

- **Aide :** coup de pouce en **barre d'état** après 90 s : « Bloqué ? Clique « Demander de
  l'aide » pour un indice, ou relis l'énoncé en haut. » (ajouté ce tour, à ta demande — le
  passif était invisible avant). Preuve dure dans le journal : **11 événements `inactivite`**
  loggés toutes les 90 s (voir ci-dessous). Le passif est donc **détecté ET reçoit un signal
  à l'écran**.
- **Gêne :** le coup de pouce est en barre d'état (bas), **discret** — un passif vraiment
  décroché peut ne pas le remarquer, et il disparaît après 20 s. (Note technique : la barre
  d'état ne se capture pas bien en PNG GDI ; elle est visible en direct et prouvée par le
  journal.)
- **Idée UI :** rendre le coup de pouce **plus visible** que la barre d'état — surligner
  brièvement le bouton « Demander de l'aide », ou un petit bandeau non-modal.
- **Journal :** 11 × `inactivite {exo, secondes:90}` (ex01 puis ex02), toutes les 90 s.

## 6. Bricoleur brute-force — capture `p6-bricoleur-erreur-gcc-precise.png`

Scénario : ex02, recompile à l'aveugle avec du code cassé (point-virgule manquant).

- **Aide :** l'erreur gcc est **très précise et mise en avant** — « PORTE FERMÉE » rouge +
  `programme.c:4:17: error: expected ';' before 'printf'` avec le **caret `^`** pointant
  exactement l'endroit. Difficile de ne pas voir où ça casse.
- **Gêne :** (a) même souci que le profil 1 : chemin temp absolu bruyant.
  (b) **Bug UX repéré** : changer d'exercice **ne vide pas le panneau tuteur** — la réponse
  de l'exercice précédent reste affichée (sur ex02 on voyait encore la réponse sur le `char`
  d'ex01). Source de confusion.
- **Idée UI :** (a) nettoyer le chemin temp ; (b) **vider le panneau tuteur au changement
  d'exercice**.
- **Journal :** `exo_ouvert {exo:"ex02_operateurs"}` ; `test_porte {ok:false, resultat:"erreur_compilation"}`.

---

## Synthèse — corrections d'interface à considérer (par priorité)

1. **Vider le panneau tuteur au changement d'exercice** — bug de confusion net, correctif
   d'une ligne. (fait dans ce push, voir commit)
2. **Nettoyer le préfixe de chemin temp** dans les erreurs gcc — moins intimidant pour le
   débutant et le bricoleur (profils 1, 6).
3. **Rendre le niveau caché plus visible** à la révélation (auto-scroll de l'énoncé ou badge
   persistant) — profil 2.
4. **Rendre le coup de pouce passif plus visible** que la barre d'état (surligner le bouton
   d'aide / bandeau non-modal) — profil 5.
5. (mineur) **Adoucir le bandeau « clangd absent »** pour l'étudiant.

Points qui marchent bien et à ne pas casser : le cran auto N0 pour le débutant (zéro
friction), le refus clair du tuteur, le combo de niveau pour baisser l'aide, la précision
des erreurs gcc, l'instrumentation complète (le journal relie tout).
