# protviz — user guide

The shared visualisation layer: one object, one function, a correct figure by
default — used across the suite (`adaptyv-kinetics` already draws through it). No CLI;
it's a library.

## How do I plot a sensorgram with its fitted model?

```python
import numpy as np
from protviz import Series, sensorgram

png_bytes = sensorgram(
    [Series(t=np.array(t), y=np.array(y), model=np.array(fit), label="50 nM")],
    title="binder_001 rep1",
)
# png_bytes is ready to embed: adaptyv_core.report.ReportBuilder.add_png(png_bytes)
```

## What else can I draw?

```python
from protviz import kinetic_map, censored_kd, reliability_curve, hit_rate_at_budget

kinetic_map(kon, koff, labels=["design_1", "design_2"])          # log-log, iso-K_D lines
censored_kd(kd_nM, censored_mask)                                  # non-binders as "> LOD", not dropped
reliability_curve(predicted_probs, observed_labels, n_bins=10)     # calibration curve
hit_rate_at_budget([24, 48, 96], values, ci_low, ci_high, base_rate=0.3)
```

Every function is **array-in, PNG-out** — pass plain numpy arrays, never a domain object
from another package, which is what lets any tool depend on protviz with no cycle.

## How do I match the house style in my own figure?

```python
from protviz.theme import new_axes, render, color

fig, ax = new_axes()               # themed, colour-blind-safe (Okabe-Ito)
ax.plot(x, y, color=color(0))      # cycles the shared palette
png_bytes = render(fig)            # tightens, rasterises, closes the figure
```

## Gotchas

- Output is raster (PNG), sized for embedding in an HTML report — not for a print
  figure. Vector/SVG output is a documented, easy extension (see `docs/limitations.md`).
- 2-D figures only; a structure viewer coloured by an experimental measurement
  (Mol*/3Dmol export) is specced but not built.

See also: [README](../../packages/protviz/README.md) ·
[technical](../../packages/protviz/docs/technical.md) ·
[limitations](../../packages/protviz/docs/limitations.md).
