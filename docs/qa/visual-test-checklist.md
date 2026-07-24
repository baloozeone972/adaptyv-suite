# Checklist de test visuel — avant soumission / avant Loom

Un test **visuel** par appli (13), à faire dans cet ordre, sur une install propre.
Pas juste `make all` (ça vérifie que le code est correct) — ici on vérifie que
**ce qu'un humain regarde** (rapport HTML, sortie terminal, figure) a l'air juste,
lisible, et sans artefact moche (texte tronqué, graphique vide, HTML cassé).

Prévoir ~25 min. Cocher au fur et à mesure. Nettoyer avec `rm -f /tmp/adaptyv-qa/*`
à la fin (dossier de sortie suggéré ci-dessous, pour ne rien laisser traîner dans le repo).

```bash
mkdir -p /tmp/adaptyv-qa && cd adaptyv-suite && make install
```

---

## 1. preflight (texte terminal)

```bash
uv run preflight check packages/preflight/tests/data/demo.fasta --assay thermostability
```
- [ ] Les symboles `✗` (reject) et `!` (review) sont visibles et alignés avec le nom du design.
- [ ] La dernière ligne récapitulative (`N designs — X pass, Y review, Z reject`) est cohérente
      avec le compte de lignes au-dessus.
- [ ] Code de sortie non nul si au moins un `reject` (`echo $?` après coup).

## 2. adaptyv-kinetics (HTML — le rapport phare)

```bash
uv run adaptyv-kinetics synth --out /tmp/adaptyv-qa/package.zip
uv run adaptyv-kinetics report /tmp/adaptyv-qa/package.zip -o /tmp/adaptyv-qa/kinetics.html
open /tmp/adaptyv-qa/kinetics.html
```
- [ ] Bandeau **"Synthetic data"** visible en haut du rapport.
- [ ] Tableau des verdicts (pass/review/reject) par réplicat, lisible.
- [ ] Au moins un sensorgramme s'affiche correctement : courbe brute + fit en pointillés,
      légende lisible, pas de graphique vide ou de `NaN` affiché.
- [ ] Le rapport s'ouvre et se scroll sans erreur JS dans la console du navigateur.

## 3. expression-rescue (HTML)

```bash
printf '>risky_design\nMKCAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKAAAAAAAAAAAAAAA\n' > /tmp/adaptyv-qa/designs.fasta
uv run expression-rescue check /tmp/adaptyv-qa/designs.fasta --report /tmp/adaptyv-qa/risk.html
open /tmp/adaptyv-qa/risk.html
```
- [ ] Chaque liability listée porte bien une **position** (résidu) et une sévérité colorée.
- [ ] Le score de risque et le tier (low/medium/high) sont visibles par design.

## 4. sensorgram-triage (HTML — courbe de délégation)

```bash
uv run sensorgram-triage calibrate --max-fnr 0.02 --report /tmp/adaptyv-qa/delegation.html
open /tmp/adaptyv-qa/delegation.html
```
- [ ] La courbe (fraction auto-approuvée vs taux de faux négatifs) se dessine avec des axes
      lisibles et une légende.
- [ ] Le point opérationnel choisi (au seuil `--max-fnr`) est visuellement marqué sur la courbe.

## 5. insilico-bench (HTML)

```bash
uv run insilico-bench synth --out /tmp/adaptyv-qa/designs.csv
uv run insilico-bench run /tmp/adaptyv-qa/designs.csv --out /tmp/adaptyv-qa/bench.html
open /tmp/adaptyv-qa/bench.html
```
- [ ] Le graphique hit-rate@budget affiche bien les barres d'erreur (CI) par score.
- [ ] Le tableau AUC-ROC / average precision / Spearman est complet, sans cellule vide.
- [ ] `ipsae` ressort visuellement au-dessus de `plddt` (le point de tout ce harnais).

## 6. campaign-planner (texte terminal — tableau)

```bash
uv run campaign-planner plan --n 96 --p-express 0.3 --p-bind 0.15 --budget 20000
```
- [ ] Le tableau des deux stratégies est aligné en colonnes (coût, binders attendus + CI, coût/binder).
- [ ] La ligne de crossover en bas est présente et lisible.

## 7. foundry-guard (texte terminal — trace d'audit)

```bash
uv run foundry-guard demo --budget 3000
```
- [ ] `ALLOW`/`DENY` bien alignés à gauche, montant et raison lisibles sur chaque ligne.
- [ ] Dernière ligne : `Audit chain valid: True` — visuellement distincte (pas noyée dans le reste).

## 8. binder-triage (texte terminal — comparaison)

```bash
uv run binder-triage select --k 24 --diversity 0.8
```
- [ ] Les deux lignes (`top_n` vs `diverse_greedy`) sont comparables visuellement : mêmes colonnes,
      la colonne `identity` baisse bien et `families` monte bien pour `diverse_greedy`.

## 9. dbtl-agent (texte terminal — boucle multi-rounds)

```bash
uv run dbtl-agent run --budget 24000 --batch 24 --rounds 6 --diversity 0.3 --seed 3
```
- [ ] Une ligne par round, lisible, pas de chevauchement de texte.
- [ ] Les deux dernières lignes (`Budget respected: True`, `audit valid: True`) ressortent.

## 10. adaptyv-pipeline (texte terminal — état de run)

```bash
printf '>d1\nMKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKR\n' > /tmp/adaptyv-qa/designs.fasta
uv run adaptyv-pipeline run /tmp/adaptyv-qa/designs.fasta --assay affinity --budget 15000 --execute
```
- [ ] Un `run_id` hexadécimal est imprimé et le statut final est `done: package fetched`.
- [ ] `.adaptyv-runs/<run_id>.state.json` existe et contient un JSON valide (`cat` rapide).

## 11. protviz (PNG — pas de CLI, script à la volée)

```bash
uv run python -c "
import numpy as np
from protviz import Series, sensorgram
png = sensorgram([Series(t=np.linspace(0,300,50), y=np.sin(np.linspace(0,3,50))+2, model=np.linspace(0,2,50), label='50 nM')], title='QA check')
open('/tmp/adaptyv-qa/protviz.png','wb').write(png)
"
open /tmp/adaptyv-qa/protviz.png
```
- [ ] Le PNG s'ouvre, palette Okabe-Ito (pas de rouge/vert par défaut matplotlib),
      pas de figure coupée ou de légende qui déborde du cadre.

## 12. mosaic-loop (HTML)

```bash
uv run mosaic-loop analyze --report /tmp/adaptyv-qa/drift.html
open /tmp/adaptyv-qa/drift.html
```
- [ ] Le tableau de drift par terme (affinity/solubility/stability) est présent, avec le terme
      `stability` visuellement signalé comme mauvais proxy (drift élevé).

## 13. boltz-tune (texte terminal — verdict)

```bash
uv run boltz-tune evaluate --target-lift 0.05
uv run boltz-tune evaluate --target-lift 0.02
uv run boltz-tune evaluate --target-lift 0.10
```
- [ ] Les trois appels donnent bien trois verdicts **différents** (needs-more-data /
      already-helps / unreachable) — c'est ce qui prouve que les 4 branches marchent.

---

## Nettoyage

```bash
rm -rf /tmp/adaptyv-qa .adaptyv-runs
```

## Si un test visuel échoue

Ce n'est **pas** la même chose qu'un test `pytest` qui échoue : `make all` peut être
100% vert et un rapport HTML avoir un CSS cassé sur un cas limite non testé côté rendu
(les tests vérifient que le PNG/HTML est généré et bien formé, pas son rendu visuel
pixel par pixel). Si quelque chose ne s'affiche pas correctement ici, c'est un vrai bug
à corriger avant l'enregistrement du Loom — ne pas l'ignorer sous prétexte que la CI
est verte.
