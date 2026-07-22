# mosaic-loop — expliqué simplement

## En une phrase

Un logiciel de conception (Mosaic) optimise des protéines d'après **trois notes
calculées** — accroche, solubilité, stabilité — sans jamais voir de vraie mesure.
Adaptyv mesure justement ces trois choses. Cet outil renvoie les mesures pour
**corriger** ces notes, et surtout dire **lesquelles correspondent vraiment à la
réalité**.

## Le problème

Mosaic ne connaît que ses propres estimations. Il optimise donc un **substitut** de la
réalité, sans jamais savoir de combien ce substitut se trompe. Si une de ses notes ne
reflète pas la vraie mesure, il « pousse » les designs dans une direction qui ne sert
à rien.

## Ce que fait l'outil

Il compare, pour chaque note, la prédiction de Mosaic et la mesure réelle d'Adaptyv, et
donne un **score de dérive** :

- 🟢 **accroche** : la prédiction suit très bien la mesure → note fiable ;
- 🟡 **solubilité** : elle suit moyennement ;
- 🔴 **stabilité** : elle ne suit **pas du tout** → Mosaic optimise ici un mauvais
  indicateur. C'est *là* qu'il faut réinjecter les mesures en priorité.

Il recale aussi les échelles (une note « 0 à 1 » et une température ne se comparent pas
directement), ce qui améliore l'accord global entre l'objectif de Mosaic et la réalité.

## L'analogie

C'est comme un GPS qui estime les temps de trajet sans jamais vérifier avec la circulation
réelle. On lui donne enfin les temps réellement mesurés : il recalibre ses estimations, et
on découvre que sur certains axes son estimation est excellente… et sur d'autres,
totalement à côté. On sait alors où le corriger en premier.

## L'honnêteté

Les données sont **simulées** (indiqué). Le vrai branchement sur Mosaic demanderait de
l'installer ; la logique de comparaison et de recalibration, elle, ne dépend pas de
Mosaic et s'appliquerait telle quelle.
