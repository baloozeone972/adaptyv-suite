# adaptyv-suite — expliqué simplement

Une vue d'ensemble grand public de toute la suite. Chaque outil a aussi sa propre
fiche `docs/vulgarisation.md` ; ce document est la carte.

## De quoi s'agit-il ?

Adaptyv est un laboratoire qui teste des protéines pour ses clients : on lui envoie
des « recettes » de protéines, il les fabrique, mesure si elles fonctionnent
(accroche, solubilité, stabilité), et renvoie les résultats. C'est puissant, mais
tout autour de ce labo, il y a des **frictions** répétées — et cette suite est une
**boîte à outils** qui s'y attaque, une friction à la fois.

Principe directeur : **un petit outil fini vaut mieux qu'un gros inachevé.**

## Les outils, en une phrase chacun

| Outil | Ce qu'il fait, simplement |
|---|---|
| **preflight** | Le correcteur d'orthographe des commandes envoyées au labo. |
| **adaptyv-kinetics** | Lit le dossier de résultats bruts et le rend enfin lisible + vérifie les calculs. |
| **expression-rescue** | Prédit les protéines qui ne se fabriqueront pas et propose des corrections. |
| **sensorgram-triage** | Trie les courbes bon/à revoir/à refaire et chiffre le temps humain économisé. |
| **insilico-bench** | Dit quels scores calculés par ordinateur prédisent vraiment le résultat réel. |
| **campaign-planner** | Choisit la meilleure façon de dépenser un budget d'expériences. |
| **foundry-guard** | Le garde du corps d'une IA qui dépense : plafond, périmètre, journal infalsifiable. |
| **binder-triage** | Choisit des protéines à tester **variées**, pas 24 fois la même. |
| **dbtl-agent** | Une IA qui mène toute seule des manches d'expériences, mais sous surveillance stricte. |
| **adaptyv-pipeline** | Transforme « envoyer au labo » en une étape automatique de chaîne de travail. |
| **protviz** | La charte graphique commune : de belles figures correctes par défaut. |
| **mosaic-loop** | Renvoie les mesures réelles pour corriger un logiciel de conception. |
| **boltz-tune** | Mesure honnêtement si spécialiser un modèle d'IA vaut le coup, et à quel prix en données. |

## Le fil rouge : l'honnêteté

Trois idées reviennent partout, parce qu'elles comptent pour une équipe qui publie
elle-même ses résultats — y compris négatifs :

1. **Jamais un chiffre tout seul.** Toujours avec sa marge d'incertitude, comme un
   sondage « à 2 % près ».
2. **On dit ce qu'on ne sait pas.** Chaque outil liste noir sur blanc ce qu'il ne
   prétend **pas** faire.
3. **Données simulées, et c'est écrit.** Comme un candidat n'a pas les vraies données
   d'Adaptyv, toutes les démonstrations tournent sur des données fabriquées — indiqué
   sur chaque rapport.

## Comment c'est fait (sans jargon)

Tout est écrit dans un même style, testé automatiquement (chaque ligne de code est
vérifiée par un test), et vérifié à chaque modification. Deux vrais défauts de sécurité
ont d'ailleurs été trouvés **par les tests** et corrigés avant même d'être un problème.

Pour voir tourner l'outil phare en une commande :

```bash
make demo
```

…et un rapport HTML lisible s'ouvre, avec les courbes, les verdicts, et le rappel que
les données sont simulées.
