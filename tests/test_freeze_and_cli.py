# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""The runner refuses confirmatory configs while the protocol is unfrozen; the freeze check is read-only."""
import hashlib
from pathlib import Path

import pytest

from scroll.cli import main
from scroll.config import load_config
from scroll.freeze import NotFrozenError, protocol_status
from scroll.runner import run_experiment

ROOT = Path(__file__).resolve().parents[1]


def _fake_repo(tmp_path, parent_text, recorded):
    (tmp_path / "research" / "experiments" / "EXP-002").mkdir(parents=True)
    (tmp_path / "research" / "protocol.md").write_text(parent_text)
    proto = tmp_path / "research" / "experiments" / "EXP-002" / "protocol.md"
    proto.write_text("frozen protocol text\n")
    h = hashlib.sha256(proto.read_bytes()).hexdigest() if recorded == "correct" else recorded
    (tmp_path / "research" / "experiment_registry.csv").write_text(
        "experiment_id,protocol_path,protocol_hash\nEXP-002,research/experiments/EXP-002/protocol.md," + h + "\n")
    return tmp_path


def test_current_repository_is_not_frozen():
    for exp in ("EXP-001", "EXP-002", "EXP-003", "EXP-004"):
        ok, reason = protocol_status(exp, ROOT)
        assert ok is False and reason


@pytest.mark.parametrize("parent,recorded,frozen", [
    ("Status: DRAFT. Not frozen.", "correct", False),
    ("Status: FROZEN v1.0", "not yet recorded", False),
    ("Status: FROZEN v1.0", "0" * 64, False),
    ("Status: FROZEN v1.0", "correct", True),
])
def test_protocol_status_rules(tmp_path, parent, recorded, frozen):
    ok, _ = protocol_status("EXP-002", _fake_repo(tmp_path, parent, recorded))
    assert ok is frozen


def test_runner_refuses_confirmatory_before_any_browser(tmp_path):
    cfg = load_config(ROOT / "experiments" / "EXP-002.json")

    def boom(_):
        raise AssertionError("the harness must not start")
    with pytest.raises(NotFrozenError):
        run_experiment(cfg, out_dir=tmp_path / "out", harness_factory=boom)
    assert not (tmp_path / "out").exists()


def test_cli_run_refuses_with_exit_3(capsys):
    assert main(["run", "--config", str(ROOT / "experiments" / "EXP-003.json")]) == 3
    assert "REFUSED" in capsys.readouterr().err


def test_cli_rejects_invalid_config(tmp_path, capsys):
    p = tmp_path / "c.json"
    p.write_text("{}")
    assert main(["run", "--config", str(p)]) == 2
