# Known limitations — foundry-guard

## `adaptyv_core.foundry` is a simplified shape, not the real Foundry contract

Verified against `adaptyvbio/adaptyv-sdk`'s source (its `client/foundry.py` and
generated types, 2026-07) — not guessed. The real client exposes seven typed
resources (`ExperimentsAPI`, `TargetsAPI`, `ResultsAPI`, `QuotesAPI`, `TokensAPI`,
`SequencesAPI`, `FeedbackAPI`) with a **two-step** experiment lifecycle
(`create()` → a quote → `confirm_quote()` / `submit()`), not the single
`submit()` this repo models. Concretely, `GuardedLab.submit` would need to
become `estimate → guard.authorize → create (unconfirmed) → confirm_quote`,
still gated the same way. This is a genuine adapter, not a config change — see
"Real integration path" below.

## Token attenuation is real and richer than assumed

`AttenuateTokenRequest`/`AttenuationSpec` exist in the real SDK with
cryptographically enforced, **append-only** narrowing (`allowed_actions`,
`allowed_org_ids`, `allowed_resources` — attenuation can only narrow access,
never expand it). That's a stronger guarantee than this repo's guard alone
provides today; wiring `TokensAPI.attenuate()` so the agent only ever holds a
narrowed token is the natural pairing with `Guard` (belt and suspenders: the
token can't do it even if the proxy is bypassed).

## Real integration path

Two options, in order of preference:
1. **Wrap their `Lab`/`FoundryClient`** behind this repo's `Transport` protocol —
   reuse their maintained, spec-drift-tested client (`adaptyv-sdk` runs a weekly
   CI job diffing its generated types against the live OpenAPI spec) instead of
   re-implementing REST calls here.
2. Re-implement `HttpTransport` directly against their OpenAPI spec — more
   control, but duplicates what their SDK already solves and can drift from it.

## The MCP HTTP shell is not built

The spec frames this as an MCP proxy the agent talks to over HTTP. What is built and
tested is the **policy engine** and the **function-level proxy** (`GuardedLab` around
a `FoundryClient`). Wrapping it in a streamable-HTTP MCP server — capability
negotiation, error propagation, token attenuation via `POST /tokens/attenuate` — is
the outer shell and the riskiest lot; it is deliberately left as the next step so the
guarantees could be built and proven offline first.

## Cost model

The budget reserves the **cost estimate** returned by Foundry and treats it as
authoritative (Adaptyv bills the quote). If actual charges could exceed the quote,
reservation would need a safety margin; the current model assumes estimate == charge.

## Scope

- Approval is a synchronous gate (a callback). A real deployment would escalate via
  webhook/Slack and block until a decision; the interface is the same.
- Rate limiting per unit time is specced but not implemented; the per-call and total
  caps are.
- The audit journal is in-memory; persisting it (append-only file / DB) is a small
  extension on the same hash chain.
