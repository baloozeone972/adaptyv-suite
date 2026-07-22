# Adaptyv tooling suite — developer entry points.
# Every package obeys the same Definition of Done: lint + types + tests green.

CORE := packages/adaptyv-core/src/adaptyv_core
PREFLIGHT := packages/preflight/src/preflight
KINETICS := packages/adaptyv-kinetics/src/adaptyv_kinetics
RESCUE := packages/expression-rescue/src/expression_rescue
PIPELINE := packages/adaptyv-pipeline/src/adaptyv_pipeline
TRIAGE := packages/sensorgram-triage/src/sensorgram_triage
BENCH := packages/insilico-bench/src/insilico_bench
PLANNER := packages/campaign-planner/src/campaign_planner
GUARD := packages/foundry-guard/src/foundry_guard
TRIAGE2 := packages/binder-triage/src/binder_triage
DBTL := packages/dbtl-agent/src/dbtl_agent
PROTVIZ := packages/protviz/src/protviz
MOSAIC := packages/mosaic-loop/src/mosaic_loop
BOLTZ := packages/boltz-tune/src/boltz_tune
MYPY_TARGETS := $(CORE) $(PREFLIGHT) $(KINETICS) $(RESCUE) $(PIPELINE) $(TRIAGE) $(BENCH) $(PLANNER) $(GUARD) $(TRIAGE2) $(DBTL) $(PROTVIZ) $(MOSAIC) $(BOLTZ)

.PHONY: install lint format typecheck test demo all clean

install:  ## Create the venv and install every workspace package (editable).
	uv sync --all-packages

lint:  ## Static lint (ruff) + format check.
	uv run ruff check packages
	uv run ruff format --check packages

format:  ## Auto-format the codebase.
	uv run ruff format packages
	uv run ruff check --fix packages

typecheck:  ## Strict type checking.
	uv run mypy $(MYPY_TARGETS)

test:  ## Run the test suite with coverage (fails under 98%).
	uv run pytest --cov=adaptyv_core --cov=preflight --cov=adaptyv_kinetics --cov=expression_rescue --cov=adaptyv_pipeline --cov=sensorgram_triage --cov=insilico_bench --cov=campaign_planner --cov=foundry_guard --cov=binder_triage --cov=dbtl_agent --cov=protviz --cov=mosaic_loop --cov=boltz_tune \
		--cov-report=term-missing --cov-fail-under=98

demo:  ## Reproduce the flagship demo: synth a package, QC it, render a report.
	uv run adaptyv-kinetics synth --out /tmp/adaptyv_demo.zip
	uv run adaptyv-kinetics qc /tmp/adaptyv_demo.zip --bootstrap 0
	uv run adaptyv-kinetics report /tmp/adaptyv_demo.zip --out /tmp/adaptyv_demo.html
	@echo "Open /tmp/adaptyv_demo.html"

demo-preflight:  ## Run the preflight linter on the demo FASTA.
	uv run preflight check packages/preflight/tests/data/demo.fasta --assay thermostability || true

all: lint typecheck test  ## Everything CI runs.

clean:
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
