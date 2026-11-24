# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""The freeze guard: confirmatory runs need a frozen parent protocol, a freeze record whose hashes match
the protocol files and the registry, and a configuration whose hash was frozen. The check is read-only."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from scroll.cli import main
from scroll.config import config_hash, load_config
from scroll.freeze import NotFrozenError, protocol_status, require_frozen
from scroll.runner import run_experiment

ROOT = Path(__file__).resolve().parents[1]
CFG = {"experiment_id": "EXP-002", "label": "confirmatory", "x": 1}


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _fake_repo(tmp_path, parent_text="Status: FROZEN v1.0", registry="correct", record="correct", cfg=CFG):
    (tmp_path / "research" / "experiments" / "EXP-002").mkdir(parents=True)
    parent = tmp_path / "research" / "protocol.md"
    parent.write_text(parent_text)
    proto = tmp_path / "research" / "experiments" / "EXP-002" / "protocol.md"
    proto.write_text("frozen protocol text\n")
    h = _sha(proto)
    reg_h = h if registry == "correct" else registry
    (tmp_path / "research" / "experiment_registry.csv").write_text(
        "experiment_id,protocol_path,protocol_hash\nEXP-002,research/experiments/EXP-002/protocol.md," + reg_h + "\n")
    if record is not None:
        rec = {"protocol": {"path": "research/protocol.md", "sha256": _sha(parent)},
               "experiments": {"EXP-002": {"protocol_path": "research/experiments/EXP-002/protocol.md", "protocol_sha256": h,
                                           "configs": [{"path": "experiments/EXP-002.json", "config_hash": config_hash(cfg)}]}}}
        if record == "stale_parent":
            rec["protocol"]["sha256"] = "1" * 64
        (tmp_path / "research" / "freeze.json").write_text(json.dumps(rec))
    return tmp_path


def test_exploratory_experiment_is_never_frozen():
    ok, reason = protocol_status("EXP-001", ROOT)
    assert ok is False and reason


@pytest.mark.parametrize("kwargs,frozen", [
    ({"parent_text": "Status: DRAFT. Not frozen."}, False),
    ({"registry": "not yet recorded"}, False),
    ({"registry": "0" * 64}, False),
    ({"record": None}, False),
    ({"record": "stale_parent"}, False),
    ({}, True),
])
def test_protocol_status_rules(tmp_path, kwargs, frozen):
    ok, _ = protocol_status("EXP-002", _fake_repo(tmp_path, **kwargs))
    assert ok is frozen


def test_changed_protocol_file_is_refused(tmp_path):
    root = _fake_repo(tmp_path)
    (root / "research" / "experiments" / "EXP-002" / "protocol.md").write_text("edited after the freeze\n")
    ok, reason = protocol_status("EXP-002", root)
    assert ok is False and "mismatch" in reason


def test_changed_parent_protocol_is_refused(tmp_path):
    root = _fake_repo(tmp_path)
    (root / "research" / "protocol.md").write_text("Status: FROZEN v1.0, edited")
    ok, reason = protocol_status("EXP-002", root)
    assert ok is False and "changed since the freeze" in reason


def test_config_hash_must_be_frozen(tmp_path):
    root = _fake_repo(tmp_path)
    assert protocol_status("EXP-002", root, CFG) == (True, "frozen")
    changed = copy.deepcopy(CFG)
    changed["x"] = 2
    ok, reason = protocol_status("EXP-002", root, changed)
    assert ok is False and "not one of the frozen configurations" in reason
    with pytest.raises(NotFrozenError):
        require_frozen("EXP-002", root, changed)


def test_unlisted_experiment_is_refused(tmp_path):
    ok, reason = protocol_status("EXP-003", _fake_repo(tmp_path))
    assert ok is False and "not frozen in the freeze record" in reason


def test_runner_refuses_changed_confirmatory_config_before_any_browser(tmp_path):
    cfg = load_config(ROOT / "experiments" / "EXP-002.json")
    cfg["description"] = cfg["description"] + " (edited)"

    def boom(_):
        raise AssertionError("the harness must not start")
    with pytest.raises(NotFrozenError):
        run_experiment(cfg, out_dir=tmp_path / "out", harness_factory=boom)
    assert not (tmp_path / "out").exists()


def test_cli_run_refuses_changed_config_with_exit_3(tmp_path, capsys):
    cfg = json.loads((ROOT / "experiments" / "EXP-003.json").read_text())
    cfg["seeds"] = cfg["seeds"][:10]
    p = tmp_path / "EXP-003-edited.json"
    p.write_text(json.dumps(cfg))
    assert main(["run", "--config", str(p)]) == 3
    assert "REFUSED" in capsys.readouterr().err


def test_cli_rejects_invalid_config(tmp_path, capsys):
    p = tmp_path / "c.json"
    p.write_text("{}")
    assert main(["run", "--config", str(p)]) == 2
