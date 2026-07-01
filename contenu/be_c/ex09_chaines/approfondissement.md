# Approfondissement (débloqué une fois l'exercice validé)

L'énoncé te demande de relire une chaîne au clavier avec `scanf` et le format `%s`. Le corrigé insiste sur un détail qui surprend souvent les débutants.

Pour un entier, tu écris `scanf("%d", &n)` avec l'esperluette `&` devant la variable, car `scanf` a besoin de l'adresse de la case où ranger la valeur lue. Pour une chaîne, tu écris `scanf("%s", chaine)` sans `&`. Ce n'est pas un oubli. Le nom d'un tableau, ici `chaine`, vaut déjà l'adresse de sa première case. Écrire `&chaine` donnerait bien une adresse, mais d'un autre type, et ce n'est pas ce que `%s` attend. La bonne forme est donc `chaine` tout court.

Il y a un piège qui accompagne cette lecture. `%s` lit un mot et le range dans le tableau sans jamais vérifier qu'il y tient. Ton tableau réserve 6 cases, donc 5 lettres utiles plus le `\0` final. Si l'utilisateur tape un mot plus long, par exemple 10 lettres, `scanf` écrit quand même par-dessus, au-delà du tableau, dans une zone mémoire non prévue. C'est le même débordement de tableau que dans l'exercice précédent, un piège classique en C. DANGER.

Pour aller plus loin : on limite la casse en bornant la lecture, par exemple `scanf("%5s", chaine)` qui lit au plus 5 caractères. C'est une bonne habitude dès qu'une saisie vient de l'extérieur.
