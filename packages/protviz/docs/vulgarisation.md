# protviz — expliqué simplement

## En une phrase

C'est la **boîte à figures** commune de toute la suite : les six graphiques du
domaine, dessinés correctement une fois pour toutes, plutôt que réinventés (mal)
dans chaque notebook.

## Le problème

Pour ce métier — des protéines conçues puis testées en vrai — il manque un outil de
visualisation adapté :

- les logiciels de **structures 3D** (PyMOL, Mol\*) savent afficher une molécule, mais
  pas la colorer selon une **mesure expérimentale** ;
- les outils de **graphiques** (matplotlib…) savent tout tracer, mais n'ont rien de
  prêt pour les courbes d'accroche ou les « non-lieurs » ;
- les logiciels des **instruments** font tout ça, mais sont propriétaires et
  impossibles à intégrer dans un pipeline.

Résultat : chaque équipe redessine les mêmes six figures, chacune à sa façon, dans un
carnet jetable.

## Ce que fait l'outil

Une fonction = une figure correcte par défaut, avec :

- une **charte visuelle unique** (couleurs lisibles même pour les daltoniens) ;
- les objets propres au domaine : courbes d'accroche avec leur ajustement, cartes de
  cinétique, et surtout une façon **honnête** de montrer les protéines qui n'accrochent
  pas (on les indique « au-delà du seuil de détection » au lieu de les faire disparaître).

Et ce n'est pas un brouillon : c'est **testé et réutilisé**. L'outil d'analyse des
courbes (adaptyv-kinetics) l'utilise déjà pour tous ses graphiques.

## L'analogie

C'est la charte graphique d'une entreprise : au lieu que chacun bricole ses slides
dans son coin, tout le monde utilise les mêmes gabarits propres et cohérents. On gagne
du temps, et tout se ressemble — dans le bon sens.
