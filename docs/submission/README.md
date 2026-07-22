# Submission — for the Adaptyv hiring team

Thank you for the take-home. Rather than guess one feature, I read Adaptyv's material and
built a **finished, honestly-built toolkit** for the frictions you document yourselves.
This folder is your fast path in.

- **[pitch.md](pitch.md)** — why this, in one page.
- **[speech.md](speech.md)** — the spoken presentation (≈ 4 min, and a 60-second version).
- **Mini-site** — [`../site/index.html`](../site/index.html): a guided tour you can read at
  **novice** or **expert** depth (open it in a browser).
- **Whole-suite docs** — [technical](../TECHNICAL.md) · [plain-language](../VULGARISATION.md).

## Evaluate it in 3 minutes

```bash
make install         # uv sync --all-packages   (~30s)
make demo            # synth a binding package, QC it, render report.html
open /tmp/adaptyv_demo.html
make all             # the quality gate: ruff + mypy --strict + 285 tests, 100% coverage
```

Then skim **one** flagship file to judge the code: the independent re-fit,
[`packages/adaptyv-kinetics/src/adaptyv_kinetics/models/fitting.py`](../../packages/adaptyv-kinetics/src/adaptyv_kinetics/models/fitting.py).

## What to look at, by interest

| If you care about… | Look at |
|---|---|
| The flagship deliverable | `adaptyv-kinetics` — reads your data package, re-fits, QC, report |
| The strongest opening | `expression-rescue` — the expression workflow you published, implemented |
| A differentiator only Adaptyv can ship | `adaptyv-pipeline` — the wet lab as a Nextflow step |
| Safety for autonomous agents | `foundry-guard` + `dbtl-agent` — hard budget, proven not exceedable |
| Scientific rigor / honesty | any `docs/limitations.md`; every metric's bootstrap CI |
| Engineering standard | `make all`, 100% coverage, `mypy --strict`, the two bugs the tests caught |

## What this is — and isn't

- **Is:** thirteen finished tools on one shared foundation, all green in CI, every claim
  carrying its confidence interval, every limitation written down.
- **Isn't:** a demo of one feature, or anything trained on data I don't have. All demo data
  is synthetic and **declared** on every report. The real integrations (Foundry API,
  Mosaic, Proteinbase, GPU) sit behind protocols with fakes — a documented swap, not a
  rewrite. Each tool's `docs/limitations.md` says exactly where that line is.

## Build order and reasoning

The full prioritised plan, and why each tool was built when it was, is in
[../action-plans/00-roadmap.md](../action-plans/00-roadmap.md). Every package also keeps a
`JOURNAL.md` — a build logbook with the exact commands run, including the dead-ends and the
fixes, so the work can be followed and reproduced.

I'd genuinely enjoy talking through which of these would move the needle most for you.
