# S2, deux pointeurs pour un échange

Tu as déjà vu qu'un sous-programme peut changer la variable de l'appelant s'il reçoit son adresse. On va un cran plus loin, échanger deux variables d'un coup. C'est un geste qui revient partout, par exemple pour trier ou pour permuter deux cases.

Tu dois écrire `echanger`, qui reçoit les adresses de deux entiers et troque leurs valeurs. Après l'appel, la première variable de l'appelant contient ce qu'avait la seconde, et inversement.

Le piège : si tu écris `*a = *b` en premier, tu écrases la valeur de a avant de l'avoir mise de côté. Il te faut une variable temporaire.

La porte : quand `echanger` troque bien les valeurs pour plusieurs cas, y compris deux valeurs égales, le test sort en succès.
