# protviz

The visualisation layer for experimentally-validated protein design. One object, one
function, a correct figure by default — so every tool in the suite draws the same six
figures the same way, instead of each notebook re-inventing them badly.

This is the **visible layer of G/A/H/I/D**. `adaptyv-kinetics` already delegates its
sensorgram plot to `protviz.sensorgram` — the shared layer, demonstrated.

## Use

```python
import numpy as np
from protviz import sensorgram, Series, kinetic_map, censored_kd, reliability_curve, hit_rate_at_budget

png = sensorgram([Series(t, y, model, "50 nM")], title="binder_001")   # PNG bytes
png = kinetic_map(kon, koff, labels)                                    # iso-K_D map
png = censored_kd(kd_nM, censored_mask)                                 # non-binders censored
png = reliability_curve(probs, labels)                                 # calibration
png = hit_rate_at_budget([24, 48, 96], values, ci_low, ci_high, base_rate)
```

Every function returns **PNG bytes**, ready to embed via `adaptyv-core.report`.

## Design

- **Array in, PNG out.** Functions take plain numpy arrays, not domain objects, so any
  tool can call them with **no dependency cycle** (protviz depends only on
  matplotlib/numpy).
- **One theme.** A colour-blind-safe (Okabe-Ito) palette, restrained grid, consistent
  sizing — set once in `theme.py`, applied everywhere.
- **The domain's own objects.** Sensorgrams with fits, kinetic maps with iso-K_D lines,
  K_D distributions that treat non-binders as **right-censored** (not dropped),
  calibration curves, and the hit-rate@budget selection figure.

## Why it exists

Mol*/PyMOL draw structures but can't colour by a measurement; matplotlib draws data but
has nothing for sensorgrams or censored K_D; instrument software does kinetics but is
proprietary and non-scriptable. protviz covers the intersection — and, unlike a
notebook, it is tested (100% coverage) and reused. See `docs/limitations.md`.
