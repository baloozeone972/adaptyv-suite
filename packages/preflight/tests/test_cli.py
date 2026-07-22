"""Tests for the preflight CLI, including exit codes and the fix command."""

from __future__ import annotations

from pathlib import Path

from adaptyv_core.seq.io import read_fasta
from preflight.cli import app
from typer.testing import CliRunner

runner = CliRunner()
_DEMO = Path(__file__).parent / "data" / "demo.fasta"


def test_check_demo_blocks() -> None:
    result = runner.invoke(app, ["check", str(_DEMO), "--assay", "thermostability"])
    assert result.exit_code == 1  # demo contains rejectable designs
    assert "REJECT" in result.stdout


def test_check_json_output() -> None:
    result = runner.invoke(app, ["check", str(_DEMO), "--json"])
    assert result.exit_code == 1
    assert '"n_designs": 5' in result.stdout


def test_check_clean_file_passes(tmp_path: Path) -> None:
    good = tmp_path / "good.fasta"
    good.write_text(">d1\n" + "A" * 59 + "W\n")
    result = runner.invoke(app, ["check", str(good)])
    assert result.exit_code == 0


def test_fix_removes_duplicates(tmp_path: Path) -> None:
    out = tmp_path / "clean.fasta"
    result = runner.invoke(app, ["fix", str(_DEMO), "--out", str(out)])
    assert result.exit_code == 0
    names = {d.name for d in read_fasta(out)}
    assert "dup_of_ok" not in names or len(read_fasta(out)) < 5
