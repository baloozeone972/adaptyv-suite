# Journal de bord — adaptyv-core

Logbook of what was built in this package, with the exact commands, so the
generation can be followed and reproduced. Newest entry on top.

---

## 2026-07-21 — Foundation laid (seq I/O + validation)

**Goal:** stand up the shared base so the first tool (preflight) has something to
build on, and freeze the cross-project contracts first (per the ground rules).

**Built:**
- `schemas.py` — frozen contracts written before any logic: `AssayType`,
  `Method`, `PlateTier`, `Severity`, `DataSource`, `Verdict`, `ProteinDesign`
  (with `.chains` / `.residues`), `Issue`.
- `config.py` — env-only settings, BYOK token via `ADAPTYVBIO_API_TOKEN`,
  `require_token()` never used in a logging path.
- `logging.py` — structlog JSON; libraries never `print`.
- `seq/io.py` — tolerant FASTA reader/writer, dependency-free, points at the
  offending line on malformed input.
- `seq/validate.py` — submission rules from the public docs: canonical alphabet,
  length 50–700, multichain `:`, name sanity, thermostability aromatics, target
  requirement, duplicate sequence/name, plate-tier alignment. All named
  constants, all functions < 50 lines.

**Commands used:**
```bash
uv sync --all-packages
uv run ruff format packages && uv run ruff check --fix packages
uv run mypy packages/adaptyv-core/src/adaptyv_core
uv run pytest --cov=adaptyv_core --cov-report=term-missing
```

**Decisions & fixes:**
- FASTA parser kept pure-Python (no Biopython) so the simplest tools stay light;
  Biopython is reserved for `biophysics`.
- mypy "source found twice" under the src layout → fixed by setting
  `mypy_path = ["packages/*/src"]` in the root config (see ADR 0001).
- `structlog.get_logger` returns `Any` → bound to a typed local before return.

**Status:** ✅ green. Coverage: `schemas` 100%, `seq.io` 100%, `seq.validate`
100%. `config`/`logging` at 0% (foundation for later tools, not yet consumed).

**Next:** add `stats` (bootstrap CI) and `report` (HTML base) when building
adaptyv-kinetics (G); add `biophysics` + `plm` when building expression-rescue (I).

---

## 2026-07-21 (later) — stats, report, and test hardening

- Added `stats.py` (bootstrap CI with `Estimate`) and `report.py` (self-contained
  HTML builder with a data-source banner), both consumed first by adaptyv-kinetics.
- **Security:** `Settings._token` is now `field(repr=False)` — a test asserts the
  token value never appears in `repr(settings)`.
- New tests: config (incl. token-safety), logging, schemas, FASTA edge cases
  (CRLF/casing/whitespace/multichain), validation boundaries (49/50/700/701) and
  two hypothesis property tests. Core modules at 100% coverage.

---

## 2026-07-22 — biophysics + foundry

- `biophysics.py` (GRAVY, hydrophobic patches, net charge, pI by bisection,
  fraction) — for expression-rescue (I), also A and H.
- `foundry.py` — the shared Foundry client: `Transport` protocol so it's testable
  offline, `FoundryClient` (cost-estimate/submit/status/download), `verify_webhook`
  (HMAC-SHA256 on the raw body), `HttpTransport` (urllib, `# pragma: no cover`).
  For pipeline (L), triage (A), DBTL (B), guard (K).

