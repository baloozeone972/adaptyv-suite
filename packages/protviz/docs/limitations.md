# Known limitations — protviz

## 2-D figures only

The current scope is the domain's 2-D figures (sensorgram, kinetic map, censored K_D,
reliability, hit-rate@budget). **Structure viewers coloured by an experimental
measurement** (Mol* / 3Dmol.js export) are in the spec and are the natural next
addition; they need a structure/JS toolchain and are out of scope for this pure-Python,
offline library.

## Raster output

Figures are returned as PNG bytes for embedding in self-contained HTML reports. Vector
(SVG) output and interactive (Plotly/Altair) variants are easy extensions on the same
array-in API, not built here.

## Theme scope

One theme (colour-blind-safe, light-grid). Dark-mode variants and per-tool accents are
straightforward but not implemented; the palette and sizing live in `theme.py` for a
single point of change.

## Shared-layer migration

`adaptyv-kinetics` delegates its sensorgram to protviz. The other tools
(sensorgram-triage, insilico-bench) still carry their own small plotting helpers; moving
those onto protviz's `hit_rate_at_budget` / `reliability_curve` is the obvious follow-up
and would remove the remaining duplication.
