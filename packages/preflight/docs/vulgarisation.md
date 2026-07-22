# preflight — expliqué simplement

## En une phrase

C'est le **correcteur d'orthographe** des commandes envoyées au laboratoire : il
repère les erreurs avant qu'elles ne coûtent de l'argent.

## Le problème

Pour tester une protéine, un client envoie sa « recette » (sa séquence) au
laboratoire d'Adaptyv. Chaque test occupe un petit puits sur une plaque, et chaque
puits est payant (environ 150 $). Si la recette est mal écrite — un caractère
interdit, trop courte, un doublon oublié — le puits est gaspillé, ou bien un
humain doit repérer le problème à la main, ce qui rajoute des jours d'attente.

## Ce que fait l'outil

Avant l'envoi, `preflight` relit chaque séquence et la classe :

- 🟢 **bon** — rien à signaler ;
- 🟠 **à revoir** — un avertissement (par exemple deux séquences identiques, donc
  payées deux fois pour rien) ;
- 🔴 **à rejeter** — une erreur bloquante (trop courte, caractère impossible,
  incompatible avec le test demandé…).

Il peut aussi corriger tout seul les problèmes sans risque (retirer les doublons,
nettoyer les noms).

## L'analogie

C'est le contrôle à l'aéroport avant l'embarquement : mieux vaut découvrir que le
billet est au mauvais nom **avant** de payer et d'attendre trois semaines, plutôt
qu'à l'arrivée. L'outil fait ce contrôle en une fraction de seconde, gratuitement.

## Pourquoi c'est utile pour Adaptyv

Moins d'allers-retours, moins de puits gaspillés, et des commandes plus propres qui
avancent plus vite. Un petit outil, un gain concret dès le premier jour.
