# Loom — scripts finalisés (Mix A+C et B)

Deux scripts prêts à lire, mot-à-mot, avec le timing, ce que tu **dis** (en anglais,
l'équipe est internationale) et ce que tu **fais** à l'écran. Choisis-en un le jour J.

---

## Pré-vol (hors caméra, avant d'enregistrer)

```bash
cd adaptyv-suite
make install
adaptyv-kinetics synth --out package.zip     # le package de démo
```

- Terminal en police ≥ 16 pt, fenêtre propre, notifications coupées.
- Navigateur prêt à ouvrir `report.html`.
- Répète la séquence de commandes une fois à blanc.
- Règle d'or : **ouvre sur le problème chiffré**, et **dis « simulé » au moins une fois**.

---

# SCRIPT FINAL 1 — Mix A+C (« l'outil fini + l'ingénieur honnête », ~3 min 45)

Le récit produit de A, avec le beat honnêteté / tests / sécurité à la fin.

| Temps | Ce que tu dis (lire tel quel) | Ce que tu fais |
|---|---|---|
| **0:00** | "Adaptyv ships every binding customer a data package — raw sensorgrams, fitted curves, QC metrics. Your own docs say it's machine-readable and works with automated pipelines. But there's no tool to actually read it — so every customer re-writes the same parser, the same re-fit, the same figures. I built that tool." | Caméra sur toi ~5 s, puis partage d'écran (terminal). |
| **0:30** | "Here's exactly what a customer receives." | `unzip -l package.zip \| head -20` — laisse voir l'arborescence brute. |
| **0:50** | "One command parses the package, re-fits the kinetics independently, runs QC on every curve, and writes a single self-contained HTML report." | `adaptyv-kinetics report package.zip -o report.html` puis `open report.html`. |
| **1:10** | "Every replicate gets a verdict — pass, review, or reject. Here are the raw sensorgrams with my independent fit overlaid. This one is flagged INCOMPLETE_DISSOCIATION: the dissociation is too short, so k_off — and therefore K_D — simply isn't identifiable. The tool says so, instead of printing a confident, wrong number." | Scroll : bandeau → tableau verdicts → un sensorgramme *reject*. |
| **1:50** | "It's an independent verifier, not a competitor to your fitting pipeline. Where my re-fit agrees with your package's values, that's evidence of quality. Where it diverges — here, R_max — it's because these concentrations don't saturate binding, so R_max isn't well determined. The tool surfaces that rather than hiding it." | `adaptyv-kinetics compare package.zip` — pointe la colonne `rmax_pct_diff`. |
| **2:20** | "Everything you just saw runs on synthetic data I generate in the repo — and it's declared on every single report — because I don't have one of your real packages. That same generator is my validation harness: the true parameters are known, so I can measure the fitter's recovery error." | Pointe le bandeau « Synthetic data » du rapport. |
| **2:40** | "I let the tests drive the hardening, and they found two real issues: a path-traversal in the package loader — a malicious zip could have escaped the temp folder — and the Foundry token leaking into a debug repr. Both fixed, both regression-tested. A hundred-and-two tests, full coverage, gated in CI, strict types throughout." | `make all` — laisse défiler jusqu'au vert « 100% ». |
| **3:20** | "And I wrote the limits down: R_max needs saturation, drift detection needs your known association/dissociation split, and the QC thresholds need your labelled curves to be calibrated. That's exactly what I'd do with access to your internal data — and it's the honesty your own blog posts already practise." | Retour caméra. |
| **3:35** | "A small, finished tool your support team could recommend tomorrow — and the starting point for the rest." | Caméra, sourire, fin. |

---

# SCRIPT FINAL 2 — B (« la suite », ~5 min)

Pour montrer l'ampleur : une base commune, plusieurs outils, une roadmap.

| Temps | Ce que tu dis (lire tel quel) | Ce que tu fais |
|---|---|---|
| **0:00** | "Adaptyv ships every binding customer a data package with no tool to read it, publishes a protein-expression workflow nobody has implemented, and spends a quarter of its delivery time on manual data review. Each of those is a friction I found in your own material — so I didn't build one script. I built a suite." | Caméra ~5 s, puis écran. |
| **0:30** | "It's a monorepo on one shared foundation. Every tool depends on a single package, adaptyv-core: the data contracts, sequence I/O, validation, statistics, reporting. Write it once, reuse it everywhere. The contracts are frozen first, so the tools can be built and tested independently." | Montre l'arbo `packages/`, puis `docs/shared-components.md`. |
| **1:15** | "The simplest tool is a pre-submission linter. It catches format and platform errors before they cost a paid well — wrong length, non-canonical residues, a thermostability assay with no aromatic residue for the nanoDSF readout." | `preflight check packages/preflight/tests/data/demo.fasta --assay thermostability` |
| **1:45** | "The flagship is adaptyv-kinetics. Here's what a binding customer receives — and one command turns it into a report." | `unzip -l package.zip \| head -15` puis `adaptyv-kinetics report package.zip -o report.html` ; `open report.html`. |
| **2:20** | "Every replicate gets a verdict. Raw sensorgrams with my independent fit on top. This one is flagged INCOMPLETE_DISSOCIATION — k_off isn't identifiable, and the tool says so rather than inventing a number." | Scroll : verdicts → un sensorgramme *reject*. |
| **2:50** | "And it's an independent verifier: where my re-fit agrees with your reported values it's evidence of quality; where R_max diverges, it's because the concentrations don't saturate — surfaced, not hidden." | `adaptyv-kinetics compare package.zip` |
| **3:20** | "All of it is finished where it counts: a hundred-and-two tests, full coverage gated in CI, strict types — and the tests caught two real security bugs, a zip path-traversal and a token leak, both fixed. Everything runs on synthetic data I generate and declare." | `make all` — jusqu'au vert. |
| **3:55** | "And it's planned where it grows. Eleven more tools are specced and prioritised against frictions in your material. Two stand out: adaptyv-pipeline — making your lab a reproducible Nextflow step, which no other CRO can offer because no other CRO has your API — and protviz, a visualisation layer these tools already share." | Montre `docs/action-plans/00-roadmap.md`. |
| **4:40** | "Finished where it counts, planned where it grows. With access to your internal data, the first thing I'd do is calibrate the QC thresholds and close the pipeline loop." | Retour caméra, fin. |

---

## Annexe — séquence de commandes (copier-coller)

```bash
# Pré-vol (hors caméra)
cd adaptyv-suite && make install
adaptyv-kinetics synth --out package.zip

# À l'écran
unzip -l package.zip | head -20
preflight check packages/preflight/tests/data/demo.fasta --assay thermostability   # (script B)
adaptyv-kinetics report package.zip -o report.html
open report.html                       # macOS ; sinon xdg-open
adaptyv-kinetics compare package.zip
make all
```

Nettoyage après coup : `rm -f package.zip report.html`.

---

## À faire / à éviter

**À faire** : dire « simulated » au moins une fois ; montrer un intervalle de confiance ;
finir sur « voici ce que je ferais avec vos données internes ».

**À éviter** : ouvrir sur l'architecture ; survendre un chiffre sur petit n ; laisser
entendre que le re-fit « corrige » Adaptyv — c'est un vérificateur, pas un juge.

**Détail qui parle** (à glisser à l'oral, pas à l'écran) : leur API expose
`POST /feedback` avec la mention « or have your agents do it ». Le mentionner en une
phrase montre qu'on a lu la doc jusqu'au bout.

---

## Références internes citées à l'écran

- `docs/shared-components.md` — la base commune
- `docs/action-plans/00-roadmap.md` — les 13 outils priorisés
- `packages/adaptyv-kinetics/docs/limitations.md` — les limites déclarées
