# binder-triage — expliqué simplement

## En une phrase

Quand on doit choisir quelles protéines tester (la plaque est limitée et payante),
la méthode habituelle — « prendre les N mieux notées » — remplit la plaque de
protéines quasi identiques. Cet outil choisit **plus malin** : de bonnes candidates,
mais **variées**.

## Le problème : la monoculture

Un modèle prédit une note pour chaque protéine. Si on prend simplement les 24
meilleures notes, on se retrouve souvent avec 24 variantes de la **même** protéine
(la « famille » que le modèle préfère). Or si le modèle se **trompe** sur cette
famille — ce qui arrive — on a tout misé sur le mauvais cheval, et la plaque ne
donne presque rien.

C'est exactement ce qu'on a observé lors d'un hackathon (TREM2) : les IA
convergeaient toutes vers des designs très ressemblants.

## Ce que fait l'outil

Il sélectionne les candidates en récompensant à la fois **une bonne note** et **la
différence** par rapport à celles déjà choisies. Résultat : une plaque tout aussi
prometteuse, mais **étalée sur plusieurs familles** plutôt que concentrée sur une
seule.

Sur nos données de test, à budget égal :

- méthode « top-N » : 1 seule famille, protéines à 72 % identiques, et parfois un
  effondrement du résultat (mauvais pari) ;
- méthode « diversifiée » : ~4-5 familles, protéines à 48 % identiques, et un **pire
  cas nettement meilleur**.

## L'analogie

C'est la différence entre parier tout son argent sur un seul cheval (le favori) et
répartir sur plusieurs. On gagne peut-être un peu moins quand le favori l'emporte,
mais on évite la catastrophe quand il perd. La diversité, c'est une **assurance**.

## L'honnêteté

Les données sont **simulées** (indiqué), avec une « vérité » connue pour pouvoir
mesurer. Sur de vraies données, il faut aussi rappeler un biais important : les
designs déjà publiés ont souvent passé un premier filtre informatique, ce qui rend
les modèles trop optimistes — l'outil le documente clairement.
