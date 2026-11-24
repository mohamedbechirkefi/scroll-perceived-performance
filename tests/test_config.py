# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
import copy
import json
from pathlib import Path

import pytest

from scroll.config import ConfigError, arm_order, config_hash, expand_sessions, load_config, validate_config

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name", sorted(p.name for p in (ROOT / "experiments").glob("*.json")))
def test_shipped_configs_validate(name):
    cfg = load_config(ROOT / "experiments" / name)
    assert expand_sessions(cfg)


def test_matrix_sizes_match_protocol():
    # research/protocol.md section 9: EXP-001 150 + 200 interactions; EXP-002 2,400; EXP-003 3,600.
    def interactions(n):
        c = load_config(ROOT / "experiments" / n)
        return len(expand_sessions(c)) * c["interactions_per_session"]
    assert interactions("EXP-001.json") == 350
    assert interactions("EXP-002.json") == 2400
    assert interactions("EXP-003.json") == 3600


def test_hash_is_stable_and_sensitive(smoke_cfg):
    h = config_hash(smoke_cfg)
    assert h == config_hash(copy.deepcopy(smoke_cfg)) and len(h) == 64
    smoke_cfg["settle_ms"] = 201
    assert config_hash(smoke_cfg) != h


def test_arm_order_is_seeded_permutation():
    arms = ["BLANK", "SKELETON", "PREFETCH"]
    a = arm_order(20261124, 1001, 0, arms)
    assert sorted(a) == sorted(arms) and a == arm_order(20261124, 1001, 0, arms)
    orders = {tuple(arm_order(20261124, s, 0, arms)) for s in range(1001, 1041)}
    assert len(orders) > 1


def test_expansion_is_matched_across_arms(smoke_cfg):
    sessions = expand_sessions(smoke_cfg)
    cells = {}
    for s in sessions:
        cells.setdefault((s.seed, s.cell()), set()).add(s.arm)
    assert all(arms >= {"BLANK"} for arms in cells.values())
    assert len({s.session_id for s in sessions}) == len(sessions)


@pytest.mark.parametrize("mutate,msg", [
    (lambda c: c.update(seeds=[1, 2]), "confirmatory seeds"),
    (lambda c: c.update(seeds=[1001, 1001]), "unique"),
    (lambda c: c["conditions"][0].update(arms=["SKELETON", "PREFETCH"]), "baseline"),
    (lambda c: c["conditions"][0].update(arms=["BLANK", "OPTIMISTIC"]), "not defined"),
    (lambda c: c["conditions"][0].update(failure_prob=[0.1]), "read path"),
    (lambda c: c.update(jitter=1.0), "config-1.0.0"),
    (lambda c: c.update(unknown=1), "config-1.0.0"),
    (lambda c: c.pop("seeds"), "config-1.0.0"),
    (lambda c: c.update(label="confirmatory", seeds=[1, 2]), "five seeds"),
    (lambda c: c["browser"].update(channel="firefox"), "config-1.0.0"),
])
def test_invalid_configs(smoke_cfg, mutate, msg):
    mutate(smoke_cfg)
    with pytest.raises(ConfigError, match=msg):
        validate_config(smoke_cfg)


def test_load_config_errors(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "missing.json")
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    with pytest.raises(ConfigError, match="valid JSON"):
        load_config(bad)
