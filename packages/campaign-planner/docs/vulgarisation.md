# campaign-planner — expliqué simplement

## En une phrase

Avec un budget et un objectif, il liste les façons **valides** de mener une
expérience et les classe — y compris une stratégie **en deux temps** que le
formulaire du site ne sait pas proposer.

## Le problème

Tester des protéines coûte cher, et on paie par **plaque entière** : si vous avez
70 protéines, vous réservez une plaque de 96 et payez les 96 emplacements, même
les 26 vides. Comment dépenser au mieux un budget donné pour obtenir le plus de
protéines qui « fonctionnent » ? Le configurateur en ligne ne répond pas à ça.

## L'idée maligne : tester en deux temps

Plutôt que de lancer directement le test d'accroche (cher) sur toutes les
protéines, on peut d'abord faire un test d'expression (bon marché) pour écarter
celles qui ne se fabriquent même pas, puis ne payer le test cher que sur les
survivantes.

- Si beaucoup de protéines échouent à se fabriquer → **le deux-temps fait
  économiser** (on ne gaspille pas le test cher sur des ratées).
- Si presque toutes se fabriquent → **le deux-temps coûte plus cher** (on a payé
  un test en plus pour rien) et prend plus de temps (les deux étapes s'enchaînent).

## Ce que fait l'outil

Il **simule** des milliers de campagnes pour estimer, avec une marge d'incertitude,
combien de protéines fonctionnelles chaque stratégie rapporte et pour quel coût.
Puis il classe : d'abord ce qui tient dans le budget, ensuite le meilleur rendement,
enfin le moins cher. Et il donne le **seuil décisif** : *« tester en deux temps est
rentable tant que moins de 50 % des protéines se fabriquent »*.

## L'analogie

C'est comme organiser un casting : soit vous faites passer l'audition finale
(coûteuse) à tout le monde, soit vous faites d'abord un tri rapide et n'invitez à
la finale que les présélectionnés. Le bon choix dépend de combien de candidats
passent le premier filtre — et l'outil calcule précisément où est la bascule.
