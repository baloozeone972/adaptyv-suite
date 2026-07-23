# Known limitations — adaptyv-core

## `foundry.py` models a simplified REST shape, not the real Foundry contract

Checked against `adaptyvbio/adaptyv-sdk`'s actual source (2026-07), not assumed.
The real client is seven typed resources (`ExperimentsAPI`, `TargetsAPI`,
`ResultsAPI`, `QuotesAPI`, `TokensAPI`, `SequencesAPI`, `FeedbackAPI`) with a
two-step experiment lifecycle and results delivered via a `data_package_url`
field, not this module's single `submit()` + direct `/package` download. See
[foundry-guard/docs/limitations.md](../../foundry-guard/docs/limitations.md#adaptyv_corefoundry-is-a-simplified-shape-not-the-real-foundry-contract)
for the full comparison and the recommended adapter path (wrap the real SDK
client behind this module's `Transport` protocol). Env var names and the
default API base (`ADAPTYV_API_KEY`, `ADAPTYV_API_URL`) do match the real SDK.

## `AssayType` now matches the real enum; `pricing` does not fully cover it

`AssayType` mirrors `adaptyv-sdk`'s generated `ExperimentType` exactly (7
values). `pricing.UNIT_PRICE_USD` / `DURATION_DAYS` only have data for the 4
assays this suite's tools actually price (`expression`, `screening`,
`affinity`, `thermostability`); calling `pricing.price()` with `fluorescence`,
`epitope_binning` or `enzyme_activity` raises `ValueError` rather than
guessing a number.

## Biophysics, stats, guard

No known integration gaps — these are self-contained (no external API surface)
and are exercised by the packages that use them (see their own
`docs/limitations.md`).
