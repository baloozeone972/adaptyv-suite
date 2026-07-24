# Presentation speech

A spoken script to present the submission (≈ 4 minutes), to accompany or replace the
Loom. Timings are guides. Say it in your own voice — the point is the story, not the
words. `[ ]` are stage directions.

---

**[0:00 — Open on the problem, not the code]**

"Hi, I'm Laurent. The brief said: read up on Adaptyv, then build something actually
useful. So I want to start with a problem you already describe in your own docs.

Every binding customer gets a data package — raw sensorgrams, fitted curves, QC
metrics — and there's no tool to read it. Each customer re-writes the same parsing and
plotting code, badly, in a throwaway notebook. That's a repeated, documented friction.
So I built the tool for it — and twelve more around it."

**[0:35 — The flagship, live]**

"This is **adaptyv-kinetics**. `unzip` a package and it's illegible machine text.
`adaptyv-kinetics report package.zip` — one command — and I get this.
[show the HTML report]

Verdicts per replicate: pass, review, reject. The raw curves with an **independent**
re-fit overlaid — I don't trust the package's numbers, I re-derive them and compare.
Where they agree, that's confidence; where they diverge, that's information.

And here's the part I care about most: when a curve doesn't dissociate enough to pin down
the off-rate, the tool doesn't print a confident K_D. It flags it as unidentifiable. It
tells you what it *can't* know."

**[1:40 — The honesty thread]**

"That's the thread through everything. You publish confidence intervals and negative
results, so I held myself to that. Every performance number has a bootstrap interval and a
sample size. Every tool has a limitations file saying what it deliberately does not claim.
And because I don't have your real data, every demo runs on synthetic data — declared, in
big letters, on every report. I'd rather show you an honest synthetic result than a
dishonest real-looking one."

**[2:20 — The breadth, briefly]**

"Around the flagship there's a whole workflow. Before the lab: a submission linter, an
expression-risk diagnoser, a diversity-aware selector that avoids betting a whole plate on
one design family. Spending: a budget planner, and a guardrail proxy that makes it
*mathematically impossible* for an autonomous agent to overspend — property-tested. After
the lab: a curve-triage tool that quantifies how much human review you can safely remove,
and a benchmark that measures which in-silico score actually predicts your wet-lab outcome.

They're not sketches. Thirteen tools, one shared foundation, 302 tests, 100% coverage,
strict type-checking — all green in CI."

**[3:15 — The one that's arguably bigger than the flagship]**

"One I'll flag: **adaptyv-pipeline**. You're the only CRO with an API. That means the wet
lab can become a normal, reproducible step in a Nextflow pipeline — cost estimated up
front, resumable across the three-week turnaround, with the model version linked to the
physical result. No competitor can offer that, because none has your API. That's a
differentiator only Adaptyv can ship."

**[3:45 — Close]**

"So — I didn't guess one feature. I turned your own documented frictions into finished,
honestly-built software. The repo's there, everything runs with `make demo`, and I'd love
to talk about which of these would move the needle most for you. Thanks for the brief — it
was a genuinely good way to spend the time."

---

### If you only have 60 seconds

"The brief was open, so I read your docs and built for the frictions you describe: your
binding customers get a data package with no reader — so the flagship reads it, re-fits the
kinetics independently, and flags what it can't identify rather than faking a number.
Around it, twelve more tools cover the workflow — all finished, 100% test coverage, every
claim carrying its confidence interval, all demo data declared synthetic. One command,
`make demo`, shows it running."
