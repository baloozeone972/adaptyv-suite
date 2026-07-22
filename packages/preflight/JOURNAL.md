# Journal de bord — preflight

Logbook of what was built, with the exact commands. Newest entry on top.

---

## 2026-07-21 — Built & green (first tool of the suite)

**Goal:** ship the simplest tool end-to-end first, to prove the whole toolchain
(lint → types → tests → CI → demo) and to seed the shared validation layer.

**Built:**
- `report.py` — aggregates per-design validation into a `PreflightReport`;
  verdict logic (reject on any critical, review on any warning, else pass);
  `blocking` property drives the exit code.
- `cli.py` — Typer app: `check` (human table or `--json`, non-zero exit on
  blocking) and `fix` (dedupe + name sanitation → clean FASTA).
- Tests: `test_report.py`, `test_cli.py` (Typer `CliRunner`), plus the shared
  rules covered in `adaptyv-core/tests/test_validate.py` and a hypothesis-based
  FASTA round-trip. Demo fixture `tests/data/demo.fasta`.

**Commands used:**
```bash
uv sync --all-packages
uv run ruff check packages && uv run ruff format --check packages
uv run mypy packages/adaptyv-core/src/adaptyv_core packages/preflight/src/preflight
uv run pytest --cov=adaptyv_core --cov=preflight --cov-report=term-missing
uv run preflight check packages/preflight/tests/data/demo.fasta --assay thermostability
```

**Result of the demo:** on the 5-design demo FASTA → 0 pass, 2 review, 3 reject
(no-aromatic, too-short, non-canonical), plate-misalignment flagged, exit code 1.

**Interrupted once:** disk full (ENOSPC) mid-write of `report.py`; resumed after
space was freed, no rework needed.

**Status:** ✅ 24 tests pass, mypy --strict clean, ruff clean, 90% coverage
overall (cli.py 98%, everything else 100% except the untouched core config/logging).

**Next:** biophysical liabilities + expression risk score are deliberately out of
scope here — they belong to expression-rescue (I), which reuses this exact
validation layer as its `validate/` module.
