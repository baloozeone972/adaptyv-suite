# The pitch

> *"Read up on what we do at Adaptyv, then build something you think would actually be
> useful to us."* — the brief.

## What I did with a no-spec brief

A no-spec brief is itself the test: it asks whether I can find a real problem, not
whether I can follow instructions. So I didn't guess one feature. I read Adaptyv's own
material — the docs, the blog posts, the data-package format, the pricing grid — and
listed the **frictions Adaptyv itself has documented**:

- you ship every binding customer a data package of raw sensorgrams and QC metrics, and
  **no tool to read it**;
- you published an "Improve Protein Expression" workflow that **nobody has implemented**;
- your 21-day delivery spends **days 16–21 on manual data review**;
- you're the **only CRO with an API**, yet the wet lab still breaks every reproducible
  pipeline at the lab door.

Then I built tools for those — not one, but a coherent **suite on a shared foundation**,
because the frictions share the same primitives (contracts, kinetics, pricing, guardrails,
reporting).

## Why this shape

- **A small finished tool beats a large unfinished one.** Every package is complete,
  tested to 100% coverage, `mypy --strict` and `ruff` clean, with a working CLI and an
  HTML report — not a prototype.
- **Your own standard of honesty.** You publish confidence intervals and negative results.
  So every number here carries a bootstrap CI; every tool documents what it deliberately
  does *not* claim; all demo data is synthetic and declared on every report. When the
  fitter can't identify a parameter, the tool says so instead of printing a confident
  number.
- **Built for your reality, not a toy.** External systems sit behind protocols with fakes,
  so the whole thing runs offline and deterministically today. For Foundry specifically,
  I didn't stop at that abstraction: I read `adaptyv-sdk`'s actual source and rewrote the
  client to be wire-compatible — real endpoint paths, the real create→confirm-quote
  lifecycle, real cost-in-cents, real result delivery via `data_package_url`. It needs a
  live token to touch your network, but the request/response shapes are no longer a guess.
  Mosaic and Proteinbase remain documented gaps (no equivalent public SDK to check against).

## The one-line version

> Instead of guessing one feature, I turned Adaptyv's own documented frictions into a
> **finished, honestly-built toolkit** — the flagship reads and independently verifies your
> binding data package in a single command; twelve more tools cover the workflow around it.

## What it says about how I'd work at Adaptyv

I ship finished, tested work; I calibrate claims to the evidence and write down the limits;
I reuse a shared base instead of duplicating; and I start from *your* documented problems,
not my assumptions. The flagship (**adaptyv-kinetics**) alone would remove a real,
repeated pain for every one of your binding customers on day one.
