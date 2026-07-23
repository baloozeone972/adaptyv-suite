# Domain-Driven Design — adaptyv-suite

A strategic-design view of the suite: the ubiquitous language, the bounded
contexts, how they relate to each other and to **Adaptyv's own domain model**,
and a line-by-line verification that the boundary between them (an
anti-corruption layer) is faithful — not just declared.

This complements [docs/TECHNICAL.md](../TECHNICAL.md) (the module map) and
[shared-components.md](../shared-components.md) (which primitives are shared)
with the *domain* view: what each part means, in whose vocabulary, and why the
boundaries are drawn where they are.

## 1. Why this document exists

Thirteen tools sit around one real external system (Adaptyv's Foundry) that
this suite does not own or control. DDD's value here is precise: it forces an
explicit answer to *"whose model wins at this boundary, and how do we know the
translation is correct?"* rather than letting API assumptions leak silently
into every tool. Section 5 is the actual compatibility check — a table, not an
assertion.

## 2. Ubiquitous language

### 2.1 Adaptyv's own terms (upstream domain — we conform to these)

Verified against `adaptyvbio/adaptyv-sdk`'s real source (2026-07), not assumed.

| Term | Meaning |
|---|---|
| **Experiment** | One assay run: a name, an `ExperimentSpec`, a lifecycle (`ExperimentStatus`). |
| **ExperimentSpec** | The immutable definition of what to run: `experiment_type`, `sequences`, `target_id`, `method`, `n_replicates`. |
| **ExperimentType** | The assay family: `affinity`, `screening`, `thermostability`, `fluorescence`, `expression`, `epitope_binning`, `enzyme_activity`. |
| **Method** | The measurement technique for binding assays: `bli` or `spr`. |
| **Quote** | A priced, time-boxed offer to run an `ExperimentSpec`; confirming it commits the spend. |
| **Result** | One output artifact of a completed/partial experiment; carries `data_package_url`, the downloadable evidence. |
| **Target** | A catalogued antigen an affinity/screening experiment binds against. |
| **Token / Attenuation** | An API credential; an attenuated token is a derived, permission-narrowed (never widened) copy of a root token. |

### 2.2 This suite's own terms (introduced where Adaptyv has no equivalent)

| Term | Meaning | Owning context |
|---|---|---|
| **Design** | A candidate protein sequence, pre-submission (Adaptyv's model starts at *Experiment*; a Design is what exists before one). | Submission Validation |
| **Liability** | A positioned, named developability risk on a sequence (e.g. `UNPAIRED_CYS`). | Developability |
| **Candidate** | A design plus a predicted bind probability and a cluster/family id, for selection. | Selection |
| **Selection** | A budget-constrained, diversity-aware pick of Candidates. | Selection |
| **Policy / Guard / Budget** | Spend rules, the enforcement engine, and a reservation-based ledger that a policy is checked against. | Governance |
| **RunState** | This suite's own persisted view of one pipeline step's progress — distinct from Adaptyv's `ExperimentStatus`, which it wraps. | Pipeline Orchestration |
| **TriageResult / Pile** | A replicate's auto-approval verdict (green/orange/red) plus the reasons. | Curve Triage |
| **Verdict** | The shared three-way outcome (`pass`/`review`/`reject`) used by both Submission Validation and Kinetics Analysis. | Shared Kernel |

## 3. Bounded contexts

| Bounded context | Package(s) | Core aggregates / entities / value objects |
|---|---|---|
| **Foundry** *(upstream, not owned)* | `adaptyv_core.foundry` (ACL only) | `Experiment`, `ExperimentSpec`, `Quote`, `Result`, `Token` — Adaptyv's model, not ours |
| **Submission Validation** | `preflight` | `ProteinDesign`, `Issue`, `Verdict` |
| **Developability** | `expression-rescue` | `Liability`, `Variant`, `SequenceReport` |
| **Kinetics Analysis** | `adaptyv-kinetics` | `Trace`, `KineticFit`, `QCFlag`, `TraceVerdict` |
| **Curve Triage** | `sensorgram-triage` | `TriageResult`, `Pile`, `DelegationCurve` (built *on* Kinetics Analysis) |
| **Predictive Benchmark** | `insilico-bench` | `DesignRecord`, `MetricReport`, `MetricScore` |
| **Campaign Economics** | `campaign-planner`, `adaptyv_core.pricing` | `Probs`, `StrategyResult`, `CostBreakdown` |
| **Governance** | `foundry-guard`, `adaptyv_core.guard` | `Policy`, `Decision`, `Budget`, `AuditJournal` — a supporting subdomain used by two core contexts |
| **Selection** | `binder-triage` | `Candidate`, `Selection` |
| **Autonomous Loop** | `dbtl-agent` | `RoundResult`, `CampaignOutcome`, `ClusterBelief` — orchestrates Selection + Governance + a Lab port |
| **Pipeline Orchestration** | `adaptyv-pipeline` | `StepConfig`, `RunState` — orchestrates the Foundry ACL as a resumable step |
| **Visualisation** *(generic subdomain)* | `protviz` | `Series` — array-in/PNG-out, no domain objects by design |
| **External-Model Feedback** | `mosaic-loop` | `DesignMeasurement`, `Calibration`, `DriftReport` — Mosaic's domain, referenced not owned |
| **Fine-tuning Research** | `boltz-tune` | `TrainingObservation`, `LearningCurve`, `TuneResult` |

**Strategic classification:** Kinetics Analysis is the **core domain** (the
flagship, the deepest and most differentiating logic). Developability,
Selection, Curve Triage, Predictive Benchmark and Campaign Economics are
**supporting subdomains** — real domain logic, but not the differentiator.
Governance, Visualisation, and the shared base (`adaptyv-core.schemas/seq/
biophysics/stats/report`) are **generic subdomains** — necessary, reusable,
not specific to protein engineering at all (a budget guard or a bootstrap CI
would look the same in any domain).

## 4. Context map

```
                         ┌─────────────────────────┐
                         │   Foundry (upstream)     │   not owned; Adaptyv's model
                         │ Experiment · Quote ·      │
                         │ Result · Target · Token   │
                         └────────────┬─────────────┘
                                      │  Anti-Corruption Layer
                                      │  (adaptyv_core.foundry)
                    ┌─────────────────┴──────────────────┐
                    │                                     │
           ┌────────▼────────┐                  ┌─────────▼─────────┐
           │ Pipeline         │                  │ Governance          │◀── Shared Kernel:
           │ Orchestration    │◀── Conformist ──▶│ (Guard/Budget/Audit) │    adaptyv-core.guard
           └────────┬────────┘                  └─────────┬─────────┘
                    │                                       │
                    │ Open Host Service (CLI)                │ Open Host Service (CLI)
                    ▼                                       ▼
          adaptyv-pipeline                          foundry-guard, dbtl-agent

  Submission Validation ──Shared Kernel (Verdict, ProteinDesign)──▶ Kinetics Analysis (core domain)
        │                                                                  │
        ▼                                                                  ▼
  Developability                                              Curve Triage ──Customer/Supplier──▶ (consumes kinetics fits)
        │                                                                  │
        ▼                                                                  ▼
  Selection ◀──Customer/Supplier── Autonomous Loop ──Shared Kernel (Guard)── Governance
        │
        ▼
  Campaign Economics (pricing shared with Selection, Pipeline)

  Predictive Benchmark, External-Model Feedback, Fine-tuning Research:
  standalone Customer/Supplier consumers of the shared base + (declared synthetic) data.

  Visualisation (protviz): Open Host Service consumed by Kinetics Analysis
  (adaptyv-kinetics already draws through it) — no dependency back.
```

**Relationship key** (standard DDD context-map patterns):
- **Anti-Corruption Layer (ACL)** — `adaptyv_core.foundry` translates Foundry's
  real model (cents, three-step lifecycle, `data_package_url`) into this
  suite's own `AssayRequest`/`CostEstimate`/`ExperimentHandle` shapes, so no
  other package touches Foundry's wire format directly.
- **Shared Kernel** — `adaptyv-core` (schemas, guard, pricing, stats, report)
  is deliberately shared, versioned, and changed rarely; every consumer accepts
  changes to it together.
- **Conformist** — `adaptyv-pipeline` and `foundry-guard` both sit directly on
  the ACL and conform to its shapes rather than wrapping them again.
- **Customer/Supplier** — `sensorgram-triage` depends on `adaptyv-kinetics`'s
  fits; `dbtl-agent` depends on `binder-triage`'s selection; both are one-way,
  versioned dependencies, not shared ownership.
- **Open Host Service** — every package's Typer CLI is the published,
  stable-surface way in; the Python API underneath is free to evolve.

## 5. Compatibility verification (the ACL, checked line-by-line)

This is the concrete answer to *"is the model compatible with Adaptyv's?"* —
not a claim, a diff. Each row was checked against `adaptyv-sdk`'s real source.

| This suite's concept | Adaptyv's real concept | Translation (in `adaptyv_core.foundry`) |
|---|---|---|
| `AssayRequest` | `ExperimentSpec` | `_experiment_spec()` maps 1:1; `method` lowercased at this boundary only (see §5.1) |
| `CostEstimate.total_usd` (float) | `CostEstimateResponse.breakdown\|incomplete.total_cents` (int) | divided by 100 once, at the client boundary |
| `FoundryClient.create_experiment(auto_confirm=True)` | `POST /experiments` with `auto_accept_quote`+`skip_draft` | identical flag pair; real API's own "fully automated" path |
| `ExperimentHandle.experiment_id` | `CreateExpResponse.experiment_id` **or** `ExpInfo.id` | both real keys exist and differ by endpoint; the client always normalises to `experiment_id` |
| `ExperimentStatus` (10 members) | `ExperimentStatus` (10 members) | verbatim, including values with no direct use yet (`draft`, `waiting_for_confirmation`, `waiting_for_materials`) |
| `download_package()` | `GET /experiments/{id}/results` → `ResultInfo.data_package_url` | client resolves the URL, then fetches it with **no** Foundry auth header (pre-signed link) |
| `AttenuationScope` | `AttenuationSpec` | field names verbatim (`allowed_actions`, `allowed_org_ids`, `allowed_resources`) |
| `adaptyv_core.schemas.AssayType` (7 members) | `ExperimentType` (7 members) | verbatim |
| `adaptyv_core.schemas.Method` (`"BLI"`/`"SPR"`) | `Method` (`"bli"`/`"spr"`) | **not** unified — see §5.1 |

### 5.1 The one place two real conventions had to be reconciled

`Method` has two legitimate, independently-verified casings: the **downloaded
data package's CSV** (`aux/replicate_info.csv`, checked against Adaptyv's live
docs) uses `"BLI"`/`"SPR"`; the **live REST API's JSON schema** (checked
against `adaptyv-sdk`) uses `"bli"`/`"spr"`. Rather than picking one and being
wrong for the other surface, `adaptyv_core.schemas.Method` keeps the CSV
convention (it's used for parsing real downloaded packages), and
`_experiment_spec()` lowercases it *only* when building a Foundry request —
documented in code and tested (`test_method_lowercased_for_the_wire`).

### 5.2 What is genuinely out of the ACL's scope

`TargetsAPI`, `SequencesAPI` (as an independent resource), `QuotesAPI.list`/
`.reject`, `FeedbackAPI`, `InfoAPI` exist in Adaptyv's real API but are called
by **none** of this suite's 13 tools — none of their domain logic needs a
target catalogue, an account-wide sequence index, quote browsing beyond the
one quote tied to a just-created experiment, feedback submission, or health
probes. This is a scoping decision, not an oversight: extending the ACL to
cover one of them is additive (one more `Transport`-protocol method + one more
Pydantic pair), never a redesign, should a future tool need one.

## 6. How to keep this honest

`adaptyv-sdk` runs its own CI job diffing its generated types against the live
OpenAPI spec weekly. This suite has no live-network CI (BYOK, no token in CI),
so the discipline here is manual: §5's table is the artifact to re-check
against `adaptyv-sdk`'s source whenever it's updated, and `HttpTransport`
(`# pragma: no cover`) is the only place a real drift would surface at runtime.
