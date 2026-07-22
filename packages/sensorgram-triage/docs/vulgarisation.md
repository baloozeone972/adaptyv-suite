# sensorgram-triage — expliqué simplement

## En une phrase

Sur les 21 jours que met Adaptyv à livrer un résultat, **6 sont consacrés à
relire des courbes à la main**. Cet outil trie ces courbes automatiquement en
trois piles et, surtout, **chiffre combien de cette relecture peut être supprimée
sans risque**.

## Le problème

Quand le laboratoire mesure l'accroche entre protéines, il produit des courbes. Un
scientifique qualifié doit ensuite toutes les regarder pour décider lesquelles sont
bonnes, lesquelles sont douteuses, lesquelles sont à refaire. C'est long, coûteux,
et c'est un frein à la croissance : on ne l'automatise pas en achetant une machine
de plus.

## Ce que fait l'outil

Il regarde chaque courbe et la range dans une pile :

- 🟢 **verte** — nickel, publiable sans intervention ;
- 🟠 **orange** — quelque chose cloche, à faire relire par un humain ;
- 🔴 **rouge** — inexploitable, à refaire.

Mais le vrai livrable, c'est un **graphique de décision** qui répond à la question
du responsable : *« si j'accepte de me tromper au plus 2 fois sur 100, quelle
proportion des courbes puis-je approuver toute seule ? »* — par exemple 60 %. Soit
autant d'heures de scientifique récupérées à chaque manche.

## L'analogie

C'est comme un tri automatique du courrier : la machine met de côté ce qui est
clairement bon et ce qui est clairement à jeter, et ne laisse à l'humain que la
petite pile des cas ambigus. Et elle vous dit exactement quel réglage garantit de
ne jamais jeter une lettre importante.

## L'honnêteté

Le modèle a été entraîné sur des courbes **simulées** (fabriquées par le logiciel,
c'est écrit sur le rapport). C'est un **harnais prêt à calibrer** : le jour où
Adaptyv branche ses vraies décisions de relecture, le même graphique dit
précisément combien de relecture peut être retirée en toute sécurité — et combien
d'exemples il faudrait pour y arriver.
