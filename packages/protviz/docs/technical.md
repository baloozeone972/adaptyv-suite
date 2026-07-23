# protviz — technical documentation

Visualisation primitives for experimentally-validated protein design.

## Module map

```
theme.py     PALETTE (Okabe-Ito), color(), new_axes(), render() -> PNG bytes
figures.py   Series; sensorgram, kinetic_map, censored_kd, reliability_curve, hit_rate_at_budget
```

## The no-cycle contract

Every figure takes **plain arrays** (and a small `Series` dataclass of arrays), never a
`Trace`/`KineticFit`/`DesignRecord`. So `adaptyv-kinetics` can depend on `protviz`
(kinetics → protviz) without protviz depending back on kinetics. The tool adapts its
objects to arrays at the call site — e.g. `adaptyv_kinetics.report.plots.plot_replicate`
builds `Series` from its traces and fit, then calls `protviz.sensorgram`.

## Figures

- **sensorgram(series, title)** — raw response vs time, fitted model dashed in the same
  colour per series.
- **kinetic_map(kon, koff, labels?)** — log-log scatter with iso-K_D diagonals
  (`k_on = k_off / K_D`) annotated at 1/10/100 nM.
- **censored_kd(kd_nM, censored)** — measured K_D on a log axis; non-binders drawn as
  right-censored markers at "> LOD" rather than dropped (the statistically honest view).
- **reliability_curve(probs, labels, n_bins)** — mean predicted vs observed frequency per
  bin, against the diagonal.
- **hit_rate_at_budget(ks, values, ci_low, ci_high, base_rate)** — errorbars vs budget k
  with the random baseline.

## Theme

`theme.render(fig)` tightens, rasterises at 110 dpi to PNG bytes, and closes the figure
(no leaked figures). The palette is colour-blind-safe; `color(i)` cycles it. `new_axes()`
returns a themed (Figure, Axes) with a light grid below the data.

## Testing

100% coverage: every figure returns a valid PNG, and each branch is exercised
(sensorgram with/without a model, kinetic_map with/without labels, censored_kd with
measured-only / censored-only / both). The `adaptyv-kinetics` sensorgram test still
passes unchanged after delegating here — the refactor is behaviour-preserving.

## Not built (documented)

Structure viewers coloured by an experimental measurement (Mol*/3Dmol export) are in the
spec; they need a JS/structure toolchain and are the natural next addition. The current
scope is the 2-D domain figures, which cover G/A/H/I/D today.

## Domain model

Bounded context: **Visualisation** — a **generic subdomain** by design: `Series`
is an array-in/PNG-out value object, deliberately carrying no domain concepts
(no `Trace`, no `KineticFit`). Exposed to `adaptyv-kinetics` as an **Open Host
Service** — kinetics depends on protviz, never the reverse (the no-cycle
contract above). See
[the DDD doc](../../../docs/architecture/domain-driven-design.md).
