# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Experiment configuration: loading, validation, hashing and matrix expansion.

Units: all durations in milliseconds; probabilities in [0, 1].
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .schema import validate_instance

CONFIG_SCHEMA = "config-1.0.0.json"
ARMS = {"read": ("BLANK", "SKELETON", "PREFETCH"), "write": ("BLANK", "OPTIMISTIC")}
BASELINE = "BLANK"
CONFIRMATORY_SEEDS = range(1, 21)  # research/protocol.md, section 5 (20 seeds, amendment A6)
CONFIRMATORY_CHANNEL = "chrome"  # installed Google Chrome, version recorded per run (amendment A5, DEC-005 option b)


class ConfigError(ValueError):
    """Raised for a configuration that is malformed or violates a protocol rule."""


@dataclass(frozen=True)
class SessionSpec:
    session_id: str
    seed: int
    condition_index: int
    path: str
    arm: str
    latency_ms: float
    failure_prob: float
    hover_lead_ms: float
    order_in_block: int

    def cell(self) -> tuple[str, float, float, float]:
        """Condition cell without the arm (arms are compared within a cell)."""
        return (self.path, self.latency_ms, self.failure_prob, self.hover_lead_ms)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def config_hash(cfg: dict[str, Any]) -> str:
    """SHA-256 of the canonical JSON encoding of the configuration."""
    return hashlib.sha256(canonical_json(cfg).encode("ascii")).hexdigest()


def validate_config(cfg: dict[str, Any]) -> dict[str, Any]:
    """Schema plus semantic validation. Returns the config unchanged or raises ConfigError."""
    try:
        validate_instance(cfg, CONFIG_SCHEMA)
    except Exception as exc:  # SchemaError carries the detail
        raise ConfigError(str(exc)) from exc
    seeds = cfg["seeds"]
    if len(set(seeds)) != len(seeds):
        raise ConfigError("seeds must be unique")
    if cfg["label"] == "exploratory":
        overlap = sorted(set(seeds) & set(CONFIRMATORY_SEEDS))
        if overlap:
            raise ConfigError(f"exploratory configs must not use confirmatory seeds 1-20 (found {overlap})")
    if cfg["label"] == "confirmatory" and len(seeds) < 5:
        raise ConfigError("confirmatory configs need at least five seeds per stochastic arm")
    if cfg["label"] == "confirmatory" and cfg["browser"]["channel"] != CONFIRMATORY_CHANNEL:
        raise ConfigError(f"confirmatory configs must use the installed Google Chrome (channel {CONFIRMATORY_CHANNEL!r}, amendment A5)")
    for i, cond in enumerate(cfg["conditions"]):
        path = cond["path"]
        arms = cond["arms"]
        if len(set(arms)) != len(arms):
            raise ConfigError(f"condition {i}: duplicate arms")
        bad = [a for a in arms if a not in ARMS[path]]
        if bad:
            raise ConfigError(f"condition {i}: arms {bad} are not defined for path {path}")
        if BASELINE not in arms:
            raise ConfigError(f"condition {i}: the baseline {BASELINE} must be present")
        if path == "read" and any(p != 0 for p in cond.get("failure_prob", [0])):
            raise ConfigError(f"condition {i}: failure_prob must be 0 on the read path")
    return cfg


def load_config(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    try:
        cfg = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"config not found: {p}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config is not valid JSON: {p}: {exc}") from exc
    return validate_config(cfg)


def arm_order(meta_seed: int, seed: int, condition_index: int, arms: list[str]) -> list[str]:
    """Seeded permutation of arms within one seed block and condition."""
    rng = np.random.default_rng([meta_seed, seed, condition_index])
    idx = rng.permutation(len(arms))
    return [arms[i] for i in idx]


def expand_sessions(cfg: dict[str, Any]) -> list[SessionSpec]:
    """Full list of sessions in execution order: seed-major, then condition, then permuted arms."""
    validate_config(cfg)
    out: list[SessionSpec] = []
    n = 0
    default_h = cfg["hover_lead_ms"]
    for seed in cfg["seeds"]:
        ci = 0
        for cond in cfg["conditions"]:
            for L in cond["latency_ms"]:
                for p in cond.get("failure_prob", [0]):
                    for h in cond.get("hover_lead_ms", [default_h]):
                        for j, arm in enumerate(arm_order(cfg["meta_seed"], seed, ci, list(cond["arms"]))):
                            n += 1
                            out.append(SessionSpec(f"S{n:04d}", seed, ci, cond["path"], arm, float(L), float(p), float(h), j))
                        ci += 1
    return out
