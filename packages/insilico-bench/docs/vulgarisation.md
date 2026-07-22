# insilico-bench — expliqué simplement

## En une phrase

Avant de payer pour tester une protéine en laboratoire, tout le monde la
présélectionne avec un **score calculé par ordinateur**. Mais **lequel de ces
scores prédit vraiment le résultat ?** Cet outil le mesure, de façon
reproductible, campagne par campagne.

## Le problème

Concevoir une protéine par ordinateur donne plein d'indicateurs de confiance
(ipSAE, ipTM, pLDDT…). On s'en sert pour trier : on ne teste en vrai que les
mieux notées. Mais si le score choisi ne prédit pas réellement le succès, on paie
pour tester les mauvaises et on jette les bonnes. Personne ne vérifie
systématiquement quel score mérite qu'on lui fasse confiance.

## Ce que fait l'outil

Il confronte chaque score aux **vrais résultats** du laboratoire et répond à trois
questions, toujours avec une **marge d'incertitude** :

- **Sait-il distinguer** les protéines qui marchent de celles qui échouent ?
- **Suit-il la force** de l'accroche mesurée ?
- **Le plus concret** : *« si je ne paie que pour les 24 mieux notées, combien
  seront bonnes ? »* — comparé au tirage au hasard.

Le tout dans **une seule commande** qui régénère un rapport complet : on rebranche
un nouveau jeu de données, on relance, le rapport se met à jour.

## L'analogie

C'est comme tester si les notes des critiques gastronomiques prédisent vraiment
les bons restaurants : on compare les étoiles annoncées à l'expérience réelle, et
on découvre quel guide mérite qu'on le suive — et lequel ne vaut pas mieux que de
choisir au hasard.

## Ce qu'on trouve (sur données simulées, c'est indiqué)

Un score (ipSAE) distingue bien et suit l'affinité ; un autre (pLDDT) fait à peine
mieux que le hasard. Exactement le genre de résultat chiffré et honnête qu'Adaptyv
publie — et l'outil est prêt à tourner sur leurs vraies données.
