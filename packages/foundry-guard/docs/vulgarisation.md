# foundry-guard — expliqué simplement

## En une phrase

Quand une IA autonome peut commander des expériences (donc dépenser de l'argent)
toute seule, cet outil se place **entre l'IA et le laboratoire** comme un garde du
corps : il applique des limites que l'IA **ne peut pas contourner**.

## Le problème

On confie de plus en plus à des agents IA le soin d'enchaîner les expériences sans
humain à chaque étape. Mais un agent peut se tromper, boucler, ou être manipulé —
et chaque commande coûte de l'argent réel. Comment lui laisser de l'autonomie sans
risquer qu'il vide le budget ou lance n'importe quoi ?

## Ce que fait l'outil

Toute commande de l'agent passe d'abord par le garde, qui vérifie :

- **le budget** — il *réserve* le montant avant de commander, jamais après. Du
  coup, aucune suite de commandes ne peut dépasser l'enveloppe. C'est prouvé par un
  test qui bombarde le système de milliers de scénarios aléatoires.
- **le périmètre** — seuls les types d'expériences autorisés passent ; le reste est
  refusé.
- **l'escalade humaine** — au-dessus d'un certain montant, il faut l'accord explicite
  d'un humain ; par défaut, c'est non.
- **la traçabilité** — chaque décision est inscrite dans un registre **infalsifiable**
  (chaîné par empreintes cryptographiques) : la moindre modification a posteriori se
  détecte immédiatement.

En cas de doute ou de panne, la règle est simple : **on refuse** (jamais « dans le
doute, on laisse passer »).

## L'analogie

C'est la carte bancaire d'entreprise avec un plafond strict, une liste de magasins
autorisés, une validation du manager au-dessus d'un montant, et un relevé que
personne ne peut trafiquer. L'employé (l'agent) garde son autonomie, mais dans un
cadre qu'il ne peut pas forcer.

## Pourquoi c'est utile pour Adaptyv

C'est exactement la brique de sécurité qui manque pour laisser tourner un agent
autonome sur leur laboratoire en confiance — la couche qui rend l'automatisation
totale acceptable.
