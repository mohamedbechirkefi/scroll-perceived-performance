# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""The repository's own freeze (owner-approved 2026-11-24): the frozen confirmatory configs are accepted,
changed ones are refused, and no browser is started by these checks."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from scroll.config import load_config
from scroll.freeze import NotFrozenError, load_freeze_record, protocol_status
from scroll.runner import run_experiment

ROOT = Path(__file__).resolve().parents[1]
FROZEN = {"EXP-002": ["EXP-002.json"], "EXP-003": ["EXP-003.json"], "EXP-004": ["EXP-004-S2.json", "EXP-004-S3.json", "EXP-004-S4.json"]}


def test_freeze_record_matches_files():
    rec = load_freeze_record(ROOT)
    assert rec["protocol"]["sha256"] == hashlib.sha256((ROOT / "research" / "protocol.md").read_bytes()).hexdigest()
    assert set(rec["experiments"]) == set(FROZEN)
    for exp, entry in rec["experiments"].items():
        assert entry["protocol_sha256"] == hashlib.sha256((ROOT / entry["protocol_path"]).read_bytes()).hexdigest()
        assert sorted(Path(c["path"]).name for c in entry["configs"]) == sorted(FROZEN[exp])
        for c in entry["configs"]:
            assert c["file_sha256"] == hashlib.sha256((ROOT / c["path"]).read_bytes()).hexdigest()


@pytest.mark.parametrize("exp,name", [(e, n) for e, ns in FROZEN.items() for n in ns])
def test_frozen_configs_are_accepted(exp, name):
    assert protocol_status(exp, ROOT, load_config(ROOT / "experiments" / name)) == (True, "frozen")


@pytest.mark.parametrize("exp,name", [(e, n) for e, ns in FROZEN.items() for n in ns])
def test_changed_configs_are_refused_before_any_browser(tmp_path, exp, name):
    cfg = copy.deepcopy(load_config(ROOT / "experiments" / name))
    cfg["settle_ms"] = cfg["settle_ms"] + 1

    def boom(_):
        raise AssertionError("the harness must not start")
    with pytest.raises(NotFrozenError, match="not one of the frozen configurations"):
        run_experiment(cfg, out_dir=tmp_path / "out", harness_factory=boom)
    assert not (tmp_path / "out").exists()


def test_config_of_another_experiment_is_refused():
    cfg = load_config(ROOT / "experiments" / "EXP-002.json")
    cfg = json.loads(json.dumps(cfg))
    cfg["experiment_id"] = "EXP-003"
    ok, _ = protocol_status("EXP-003", ROOT, cfg)
    assert ok is False


class _GuardPassed(Exception):
    pass


@pytest.mark.parametrize("exp,name", [(e, n) for e, ns in FROZEN.items() for n in ns])
def test_runner_accepts_frozen_configs(tmp_path, exp, name):
    """The runner gets past the freeze guard to the harness; the stub stops it there (no browser, no run)."""
    def stop(_):
        raise _GuardPassed
    with pytest.raises(_GuardPassed):
        run_experiment(load_config(ROOT / "experiments" / name), out_dir=tmp_path / "out", harness_factory=stop, log=lambda s: None)
