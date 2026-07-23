# Known limitations — adaptyv-core

## `foundry.py` is wire-compatible with the real API — within a stated scope

Rewritten and verified against `adaptyvbio/adaptyv-sdk`'s actual source
(`client/foundry.py` + its generated types, 2026-07), not assumed:

- Real endpoint paths (`POST /experiments/cost-estimate`, `POST /experiments`,
  `POST /experiments/{id}/submit`, `POST /experiments/{id}/quote/confirm`,
  `GET /experiments/{id}`, `GET /experiments/{id}/results`,
  `POST /tokens/attenuate`) and the real `Authorization: Bearer` /
  `Content-Type: application/json` headers.
- The real two/three-step experiment lifecycle (`create` → `submit` →
  `confirm_quote`), plus the real API's one-shot `auto_accept_quote` +
  `skip_draft` combination on `create()` — the path this suite's
  `foundry-guard` and `adaptyv-pipeline` use, so the entire spend happens at
  one call the guard can gate atomically.
- Real response shapes: cost in integer `total_cents` (converted to USD once,
  at the client boundary), `ExpInfo.id`/`.status` vs `CreateExpResponse
  .experiment_id` (different key names for the same concept — a real API
  quirk, not a bug here), results as a paginated `{"items": [...]}` envelope,
  and the package delivered via `ResultInfo.data_package_url` (a pre-signed
  link, fetched with no Foundry auth header) rather than a direct
  `/experiments/{id}/package` endpoint.
- The real `ExperimentStatus` enum (10 values, lowercase snake_case) and
  `AssayType` (7 values, matching `ExperimentType` exactly).
- Real, cryptographically append-only token attenuation
  (`FoundryClient.attenuate_token`, matching `TokensAPI.attenuate` — narrows
  access, never expands it).
- Env var names and the default API base already matched (`ADAPTYV_API_KEY`,
  `ADAPTYV_API_URL`).

**What this client deliberately does not cover** — none of this suite's 13
tools need them: managing targets (`TargetsAPI`), sequences as their own
resource (`SequencesAPI`), quotes as a listable/rejectable resource beyond
`confirm_quote` (`QuotesAPI.list`/`.reject`), feedback submission
(`FeedbackAPI`), and service health checks (`InfoAPI`). Adding any of these is
a small, additive extension of the same `Transport`-protocol pattern, not a
redesign.

**Still not exercised against the live network** (by construction — no token,
no live calls in CI): `HttpTransport` is `# pragma: no cover`. Every other
line — payload assembly, response parsing, the lifecycle, cost conversion,
attenuation — is tested through a fake `Transport` shaped exactly like the
real API's documented responses.

## `pricing` covers 4 of the 7 real assay types

`pricing.UNIT_PRICE_USD` / `DURATION_DAYS` have data for `expression`,
`screening`, `affinity`, `thermostability` — the assays this suite's tools
actually price. Calling `pricing.price()` with `fluorescence`,
`epitope_binning` or `enzyme_activity` raises `ValueError` rather than
guessing a number; adding real prices for them is a two-line change once
pricing data is available.

## Biophysics, stats, guard

No known integration gaps — these are self-contained (no external API
surface) and are exercised by the packages that use them (see their own
`docs/limitations.md`).
