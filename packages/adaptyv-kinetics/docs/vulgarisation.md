# adaptyv-kinetics — expliqué simplement

## En une phrase

Adaptyv livre à chaque client un dossier de données brutes sur la « colle » entre
protéines — et **aucun outil pour le lire**. Ce logiciel le lit, revérifie les
calculs, repère les mesures douteuses et en fait un rapport clair, en une commande.

## De quoi parle-t-on ?

Quand on veut savoir si deux protéines « s'accrochent » (par exemple un médicament
et sa cible), le laboratoire mesure la force de cette accroche. L'appareil produit
des **courbes** : la protéine s'attache (ça monte), puis se détache (ça descend).
De ces courbes on tire un chiffre clé, le **K_D**, qui dit à quel point l'accroche
est forte.

Adaptyv envoie au client toutes ces courbes brutes dans une archive. Mais c'est du
« texte pour machine » : illisible tel quel. Chaque client réécrit donc les mêmes
programmes pour l'exploiter. Une perte de temps répétée.

## Ce que fait l'outil

En une commande, il :

1. **ouvre l'archive** et remet tout en ordre ;
2. **recalcule lui-même** le K_D à partir des courbes, de façon indépendante ;
3. **repère les courbes à problème** : signal trop faible, détachement trop court
   (le chiffre n'est alors pas fiable — et l'outil le dit au lieu d'inventer) ;
4. **produit un rapport** : chaque mesure classée bon / à revoir / à rejeter, avec
   les courbes et le modèle superposés.

## L'analogie

C'est comme recevoir les relevés bruts d'un appareil médical et avoir enfin un
logiciel qui les met en graphique, refait le calcul pour vérifier, et surligne en
rouge les examens ratés à refaire.

## L'honnêteté, au cœur

Toutes les démonstrations tournent sur des données **simulées** (fabriquées par le
logiciel lui-même), ce qui est écrit noir sur blanc sur chaque rapport. Et quand
une mesure ne permet pas de conclure, l'outil l'affiche clairement plutôt que de
donner un faux chiffre rassurant.
