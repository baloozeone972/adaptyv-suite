# Known limitations — foundry-guard

## The MCP HTTP shell is not built

The spec frames this as an MCP proxy the agent talks to over HTTP. What is built and
tested is the **policy engine** and the **function-level proxy** (`GuardedLab` around
a `FoundryClient`). Wrapping it in a streamable-HTTP MCP server — capability
negotiation, error propagation, token attenuation via `POST /tokens/attenuate` — is
the outer shell and the riskiest lot; it is deliberately left as the next step so the
guarantees could be built and proven offline first.

## Token attenuation

The guard controls what the *proxy* forwards, but a fully hostile agent with the raw
token could bypass the proxy. The real defence is handing the agent an **attenuated**
token (scoped, capped) from `POST /tokens/attenuate`, so even direct calls are
constrained. That call is specced in `adaptyv-core.foundry` but not wired into the
guard yet.

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
