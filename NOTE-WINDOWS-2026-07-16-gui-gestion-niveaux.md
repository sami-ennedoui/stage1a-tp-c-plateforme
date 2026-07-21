# Note Windows -> Linux, 2026-07-16 : mode auteur GUI, lanceur et doc

Pour le Claude Linux. Travail fait et pousse sur la branche `gui-gestion-niveaux`
(pas encore fusionnee dans `version-projet`). Domaine strictement Windows :
interface, packaging, confort d'usage. Aucun fichier de contenu ni de specs touche.

## Ce qui a ete fait

1. **Gestion des niveaux en interface graphique** (equivalent GUI de ce que tu fais a
   la main cote Linux). Ajouter, retirer (detacher seulement, jamais supprimer le
   dossier), reattacher un detache, monter/descendre dans l'ordre, et editer le contenu
   d'un niveau (enonce.md, starter.c, corrige.c, titre, sortie_attendue) depuis des
   onglets. Logique pure dans `gestion_niveaux.py`, GUI dans `dialogue_niveaux.py`.

2. **Mode auteur derriere un mot de passe.** Tout ce qui modifie le contenu passe par
   le menu Parametres et demande un mot de passe (empreinte SHA-256 dans `auteur.json`,
   local a chaque poste, git-ignore). Module `auteur.py`. Defaut "auteur", changeable
   depuis le menu.

3. **Confort Windows sans ligne de commande.**
   - `Atelier.bat` : double-clic, detecte Python (Python312 puis `py`), ajoute
     `w64devkit\bin` au PATH si gcc y est, lance sur le dernier parcours retenu.
   - Menu Parametres enrichi : changer de parcours (liste les dossiers de `contenu\`,
     enregistre le choix dans `reglages.json` git-ignore et propose de relancer), ouvrir
     le dossier du contenu, fenetre "Emplacements et diagnostic" (chemins cles + presence
     gcc/clangd/claude, version GUI de diagnostic.bat), raccourci bureau.
   - Modules `reglages.py`, `diagnostic.py`, `dialogue_diagnostic.py`.

4. **gcc portable** w64devkit 2.8.0 (gcc 16.1.0) pose dans `w64devkit\` (git-ignore,
   embarque a cote de l'appli). Portes verifiees de bout en bout sur be_c : le corrige
   ouvre, le starter ferme, avec le vrai gcc.

5. **Compiler != Tester.** Le bouton Compiler ne fait plus que compiler et executer en
   affichant la console brute (nouvelle fonction `executeur.compiler_et_executer`), sans
   juger la porte. Tester garde la porte et la validation. Demande explicite de l'auteur.

6. **Documentation** dans `docs\` : guide utilisateur (2A), guide auteur/enseignant,
   README projet, doc technique, en Markdown + PDF (les PDF sont maintenant suivis dans
   `docs\pdf\` pour qui reprend le depot). `docs\build_pdf.py` les regenere via Edge
   headless. `DOC-gestion-niveaux.md` documente le mode auteur, le lanceur et le
   diagnostic.

Tests unittest ajoutes : `test_gestion_niveaux.py` (dont mode auteur), `test_reglages.py`,
`test_diagnostic.py`, `test_compiler.py`. Verts avec gcc au PATH. Les seuls echecs de la
suite complete restent la zone Snake/projet/SDL, pre-existants et hors sujet ici.

## Rien a faire de ton cote pour l'instant

Ce travail ne touche ni contenu ni specs, il est isolable. Si tu veux le recuperer dans
`version-projet`, `gui-gestion-niveaux` fusionne proprement (imports freres du meme style
que `executeur`/`chemins`). Sinon il peut rester une branche Windows a part.

Question ouverte : veux-tu que `compiler_et_executer` (compile+run sans porte) devienne
une brique reutilisable cote Linux, ou ca reste un detail d'UI Windows ? A ton avis.
