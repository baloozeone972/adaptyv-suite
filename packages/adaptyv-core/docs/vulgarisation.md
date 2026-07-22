# adaptyv-core — expliqué simplement

## En une phrase

C'est la **boîte à outils commune** que tous les autres logiciels de la suite
utilisent, pour ne pas réécrire dix fois les mêmes briques de base.

## L'idée

Imaginez une cuisine de restaurant. Avant de préparer des plats différents, on a
besoin des mêmes ustensiles fiables : des couteaux qui coupent bien, une balance
juste, des recettes de base. `adaptyv-core`, c'est ce tiroir d'ustensiles partagés.

Chaque outil de la suite (analyser des courbes, vérifier des protéines, piloter le
laboratoire…) pioche dedans au lieu de fabriquer ses propres couteaux. Résultat :
tout le monde utilise **exactement les mêmes** définitions et calculs, donc les
outils se comprennent entre eux et ne se contredisent pas.

## Ce qu'il contient, sans jargon

- **Un langage commun** : la façon standard de décrire une protéine, un type
  d'expérience, un verdict (« bon / à revoir / à rejeter »).
- **La lecture des séquences** de protéines et leur vérification (est-ce bien écrit ?
  la bonne longueur ?).
- **Des mesures de chimie** : à quel point une protéine est « grasse » (et donc
  risque de mal se dissoudre), son acidité, etc.
- **Des statistiques honnêtes** : jamais un chiffre tout seul, toujours avec sa
  marge d'incertitude — comme un sondage donné « à 2 % près ».
- **La fabrication de rapports** lisibles (une seule page web autonome).
- **La connexion sécurisée** au laboratoire d'Adaptyv, avec la clé d'accès qui
  n'est **jamais** écrite ni affichée quelque part.

## Pourquoi c'est important

En mettant ces fondations en commun, on gagne du temps, on évite les erreurs de
recopie, et on garantit que « une protéine trop grasse » veut dire la même chose
partout. C'est la partie invisible mais qui tient tout l'édifice.
