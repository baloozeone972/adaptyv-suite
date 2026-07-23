# Known limitations — foundry-guard

## `adaptyv_core.foundry` is now wire-compatible (was a simplified guess)

`GuardedLab.submit` uses `FoundryClient.create_experiment(..., auto_confirm=True)`
— the real API's one-shot `auto_accept_quote` + `skip_draft` path — so the whole
spend still happens at one call the guard gates atomically (estimate → authorize
→ reserve → create-and-confirm → commit), matching this file's original design
intent. The request/response shapes underneath are now the real, verified ones
(see `adaptyv-core/docs/limitations.md` for the full comparison against
`adaptyvbio/adaptyv-sdk`'s source) rather than an assumed REST shape.

Not implemented here (deliberately, matching `adaptyv-core`'s stated scope):
the manual multi-step flow (`create(auto_confirm=False)` → `submit_experiment`
→ `confirm_quote`, all present on `FoundryClient` for parity) is not wired into
`GuardedLab`, which only ever uses the one-shot path — a human-in-the-loop
manual-quote-review flow would use those methods directly against the guard's
`authorize`, without needing `GuardedLab` at all.

## Token attenuation exists on the client; not yet wired into the guard

`FoundryClient.attenuate_token` is implemented and wire-compatible (real,
cryptographically append-only narrowing — `allowed_actions`, `allowed_org_ids`,
`allowed_resources` — that can only shrink access, never expand it). It is not
yet called anywhere in `GuardedLab`: handing the agent a narrowed token instead
of the root one (belt and suspenders — the token can't overreach even if the
proxy is bypassed) is a natural, small addition (mint once at `GuardedLab`
construction, or per-session) but isn't wired in yet.

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
