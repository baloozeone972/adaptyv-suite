# boltz-tune — expliqué simplement

## En une phrase

Adaptyv utilise un grand modèle d'IA (Boltz-2) « tel quel ». Elle produit pourtant
exactement les données qui pourraient le **spécialiser**. La question honnête : **est-ce
que le spécialiser aide vraiment — et combien de données faudrait-il pour un gain réel ?**
Cet outil y répond.

## Le problème

Spécialiser (« affiner ») un modèle sur ses propres données coûte du temps et du calcul,
et ne marche pas toujours : le volume de données d'Adaptyv est modeste, et le domaine
(protéine-protéine) diffère de celui sur lequel Boltz-2 a surtout appris. On ne sait pas,
à l'avance, si le jeu en vaut la chandelle.

## Ce que fait l'outil

Il trace une **courbe d'apprentissage** : la qualité du modèle en fonction de la quantité
de données d'entraînement. À partir de quelques points, il ajuste la courbe et
**extrapole** : « avec les données actuelles, on gagne +X ; pour gagner +Y, il faudrait
environ **Z fois plus** de données ». Et il tranche honnêtement selon quatre cas :

- ça aide déjà,
- il faut ~N fois plus de données,
- l'objectif est hors de portée (au-dessus du plafond),
- affiner ne battra jamais le modèle de base.

Sur l'exemple simulé : viser +0,05 demanderait **~6× plus de données** que le volume
actuel.

## L'analogie

C'est comme estimer combien d'heures de révision supplémentaires il faudrait pour gagner
deux points de moyenne : on regarde la progression déjà obtenue, on prolonge la courbe, et
on répond « pour +2, il faudrait à peu près tripler le temps de révision » — ou
« au-delà, ça ne bouge plus ».

## L'honnêteté (au cœur de ce projet)

C'est cadré comme un **projet de recherche**, pas un produit. La courbe est **simulée**
(indiqué), car affiner réellement Boltz-2 demande les données internes d'Adaptyv et de la
puissance de calcul. Le livrable, c'est le **harnais reproductible + une réponse chiffrée
honnête** — y compris quand la réponse est « pas encore, il faudrait tant de données en
plus ». Ce chiffre-là a de la valeur.
