# adaptyv-pipeline — expliqué simplement

## En une phrase

Aujourd'hui, un chercheur automatise tout son travail informatique… puis **s'arrête
à la porte du laboratoire** : il exporte un fichier, va sur un site web, colle ses
protéines à la main, attend trois semaines, télécharge un ZIP, et recolle les
résultats à la main. Cet outil supprime cette rupture : le laboratoire devient une
**étape automatique** de la chaîne, comme n'importe quelle autre.

## Le problème, avec une image

Imaginez une usine entièrement robotisée… sauf une étape au milieu où un ouvrier
doit sortir une pièce, l'apporter à pied dans un autre bâtiment, attendre, puis la
rapporter. Toute la fluidité est cassée à cet endroit précis. Le « laboratoire »
d'Adaptyv, c'est cette étape manuelle au milieu d'un processus sinon automatique.

## Ce que fait l'outil

Il transforme « envoyer des protéines au labo » en une seule commande intégrable
dans un pipeline (Nextflow, Snakemake — les outils standards des chercheurs) :

- **devis à blanc** : il calcule le coût *avant* toute dépense ;
- **sécurité d'abord** : par défaut il **ne commande rien** ; il faut le dire
  explicitement, et il refuse de dépasser le budget fixé ;
- **reprise** : comme une vraie manche dure trois semaines, si le processus est
  interrompu, il **reprend exactement où il en était** ;
- **traçabilité** : il note quelle **version du modèle** a produit quel **résultat
  réel** — le chaînon manquant entre « ce que l'IA a prédit » et « ce que la
  biologie a répondu ».

## Pourquoi c'est un atout unique pour Adaptyv

Aucun autre laboratoire concurrent ne peut proposer ça, tout simplement parce
qu'aucun autre n'a d'interface programmable. Adaptyv, si. Cet outil tient la
promesse qu'ils écrivent eux-mêmes : commander une expérience aussi simplement
qu'un appel de programme.

## L'honnêteté

Les démonstrations tournent sur un **laboratoire simulé** (intégré au logiciel),
pour que tout fonctionne sans dépenser un centime et de façon reproductible. Le
branchement sur le vrai laboratoire existe, mais nécessite une clé d'accès.
