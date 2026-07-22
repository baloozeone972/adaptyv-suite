# adaptyv-core

The shared foundation for the Adaptyv tooling suite. Stable primitives, not
orchestration. Every tool depends on this package.

## Modules

| Module | Status | What it provides |
|---|---|---|
| `schemas` | ✅ | Frozen contracts: `AssayType`, `Method`, `PlateTier`, `Severity`, `DataSource`, `Verdict`, `ProteinDesign`, `Issue` |
| `config` | ✅ | Env-sourced settings, BYOK token (never logged) |
| `logging` | ✅ | structlog JSON configuration |
| `seq.io` | ✅ | Tolerant FASTA read/write |
| `seq.validate` | ✅ | Submission validation rules (shared by preflight & expression-rescue) |
| `biophysics` | ⏳ | pI, GRAVY, hydrophobic patches, liabilities |
| `stats` | ✅ | bootstrap CI (Fisher, Mann-Whitney, grouped CV, calibration planned) |
| `report` | ✅ | self-contained HTML reporting with data-source banner |
| `foundry` | ⏳ | Foundry client: cost-estimate, token attenuation, webhook HMAC |
| `pricing` | ⏳ | plate tiers, price grid, discounts |
| `guard` | ⏳ | budget policy, hash-chained audit journal |
| `plm` | ⏳ | ESM embeddings / log-likelihood, disk-cached |
| `proteinbase` | ⏳ | download, cache, harmonize campaigns |

⏳ modules are added when the first consuming tool is built (see
`docs/shared-components.md`).

## Usage

```python
from adaptyv_core import ProteinDesign, AssayType
from adaptyv_core.seq import validate_design

design = ProteinDesign(name="d1", sequence="MK...W")
issues = validate_design(design, assay=AssayType.THERMOSTABILITY)
```
