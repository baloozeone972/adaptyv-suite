# adaptyv-core — technical documentation

The shared foundation every tool in the suite depends on. It holds **stable
primitives**, not orchestration: contracts, sequence handling, biophysics,
statistics, reporting, the Foundry client, config and logging.

## Design principle

Pydantic contracts are frozen first (`schemas.py`) and changed rarely. Each module
exposes a narrow public surface; everything else is private (`_`). This is what
lets the tools be built and tested in isolation against synthetic fixtures.

## Modules

| Module | Public surface | Notes |
|---|---|---|
| `schemas` | `AssayType`, `Method`, `PlateTier`, `Severity`, `DataSource`, `Verdict`, `ProteinDesign`, `Issue` | `ProteinDesign.chains`/`.residues` split on `:` |
| `config` | `Settings.from_env`, `has_token`, `require_token` | BYOK; token `repr=False` so it never leaks |
| `logging` | `configure`, `get_logger` | structlog JSON; libraries never `print` |
| `seq.io` | `parse_fasta`, `read_fasta`, `write_fasta` | tolerant, dependency-free; points at the offending line |
| `seq.validate` | `validate_design`, `validate_campaign`, `check_plate_alignment`, `CANONICAL_AA` | submission rules from the public docs |
| `biophysics` | `gravy`, `hydrophobic_patches`, `net_charge`, `isoelectric_point`, `fraction` | Kyte-Doolittle; EMBOSS pKa; pI by bisection |
| `stats` | `bootstrap_ci`, `Estimate` | percentile bootstrap; house rule "never a bare number" |
| `report` | `ReportBuilder` | self-contained HTML; embeds images as data URIs; data-source banner |
| `foundry` | `FoundryClient`, `Transport`, `verify_webhook`, `AssayRequest`, `CostEstimate`, `ExperimentStatus` | transport protocol so it's testable offline; HMAC-SHA256 |

## Key algorithms

- **Isoelectric point** — bisection on net charge over pH ∈ [0, 14] to a tolerance;
  net charge via Henderson-Hasselbalch over EMBOSS pKa. Absolute pI is approximate
  (±0.5 across pKa sets), so consumers use windows, not hard cutoffs.
- **Hydrophobic patches** — sliding window (default 7) of mean Kyte-Doolittle above
  a threshold (default 2.0), overlapping windows merged into maximal runs.
- **Bootstrap CI** — resample with replacement `n` times, percentile interval;
  returns an `Estimate(value, ci_low, ci_high, n)`.

## Security posture

- Foundry token read from the environment only, `repr=False`, never logged.
- `foundry.verify_webhook` uses `hmac.compare_digest` on the raw body (constant-time).
- The real HTTP transport is the only network code and is excluded from coverage;
  all client logic is tested through a fake transport.

## Testing

100% line coverage. Property-based tests (`hypothesis`) on the FASTA round-trip and
the validation alphabet. See `tests/`.
