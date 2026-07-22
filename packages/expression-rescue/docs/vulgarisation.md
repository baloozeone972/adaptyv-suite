# expression-rescue — expliqué simplement

## En une phrase

Entre 7 % et 19 % des protéines envoyées au laboratoire **ne se fabriquent pas** :
argent perdu, aucune donnée en retour. Cet outil prédit lesquelles sont à risque,
explique pourquoi, et propose des corrections — un mode d'emploi qu'Adaptyv avait
publié mais que personne n'avait transformé en logiciel.

## Le problème

Une protéine, c'est une longue chaîne d'acides aminés (des « perles » de 20 types).
Certaines chaînes, une fois commandées, refusent de se former correctement : elles
s'agglutinent, ne se dissolvent pas, ou sont chimiquement instables. On ne le
découvre qu'après avoir payé et attendu.

## Ce que fait l'outil

Avant de commander, il inspecte chaque protéine et signale les **défauts connus**,
en pointant l'endroit exact :

- des « perles » collantes regroupées (risque d'agglutination) ;
- une cystéine solitaire (crée de mauvaises liaisons) ;
- des motifs chimiquement fragiles ;
- une protéine globalement trop « grasse » ou mal équilibrée…

Puis il donne un **niveau de risque** (faible / moyen / élevé), chiffre l'**argent
en jeu** (« 12 protéines à risque, soit ~2 000 $ »), et propose des **corrections
minimes** — en changeant au plus 3 perles, sans toucher aux zones que l'utilisateur
a marquées comme importantes.

## L'honnêteté, encore

- Le niveau de risque est une **estimation par règles**, pas une probabilité exacte
  (le modèle calibré demanderait les données internes d'Adaptyv).
- Les corrections sont **« à considérer », pas garanties** : l'outil recalcule le
  risque après correction et vous montre l'avant/après, sans jamais promettre que
  « c'est mieux ». Seul un test en laboratoire pourrait le confirmer.

## L'analogie

C'est un correcteur qui, avant impression, repère les phrases qui ne passeront pas
et propose une reformulation prudente — en vous disant honnêtement de combien il a
réduit le risque, sans jurer que le texte est parfait.
