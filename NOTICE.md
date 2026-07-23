# Notice

This project is original work, licensed under [MIT](LICENSE). This file records
one specific, deliberate act of reuse, for transparency.

## Wire-format knowledge derived from `adaptyvbio/adaptyv-sdk`

To make `adaptyv_core.foundry` genuinely compatible with Adaptyv's real Foundry
API — rather than guessing at a plausible-looking REST shape — its endpoint
paths, request/response field names, enum values, and pagination envelope were
read from the public source of
[`adaptyvbio/adaptyv-sdk`](https://github.com/adaptyvbio/adaptyv-sdk)
(MIT-licensed, copyright Adaptyv Bio), specifically `src/adaptyv/client/foundry.py`
and `src/adaptyv/types/{generated,lists}.py`, as they stood in 2026-07.

**What was and wasn't done with that reading:**
- API contract facts — endpoint paths, field names, enum members, status codes —
  are not copyrightable expression; they were used freely to write fresh,
  independent code (`packages/adaptyv-core/src/adaptyv_core/foundry.py`) that
  speaks the same wire protocol.
- No source code from `adaptyv-sdk` was copied into this repository. Every
  Pydantic model, method, and docstring in `foundry.py` was written from
  scratch for this project's own architecture (a `Transport` protocol enabling
  offline testing, USD-denominated costs at the client boundary, this suite's
  own `AssayRequest`/`ExperimentHandle` shapes).
- Every place this project's code was shaped by that reading is called out
  explicitly in the relevant `docs/limitations.md` and in code comments
  (e.g. `adaptyv-core/docs/limitations.md`), rather than left as an
  unattributed coincidence.

This note exists so that, should this project ever be assigned to or merged
with Adaptyv's own codebase, the provenance of this specific design decision is
already on the record.
