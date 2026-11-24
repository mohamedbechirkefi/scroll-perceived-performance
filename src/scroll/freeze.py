# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Read-only freeze check. This module never freezes anything (gate G-FREEZE belongs to the owner).

A confirmatory run is accepted only when all of the following hold:

1. `research/protocol.md` exists and no longer declares itself "Not frozen";
2. the freeze record `research/freeze.json` exists and its SHA-256 for `research/protocol.md`
   matches the file;
3. the experiment is listed in the freeze record, and the SHA-256 of its protocol file matches
   both the freeze record and the `protocol_hash` column of `research/experiment_registry.csv`;
4. when a configuration is given, its canonical hash (`config.config_hash`) is one of the
   configuration hashes frozen for that experiment.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .manifest import repo_root

HEX64 = re.compile(r"^[0-9a-f]{64}$")
FREEZE_RECORD = Path("research") / "freeze.json"


class NotFrozenError(RuntimeError):
    """A confirmatory run was requested while its protocol or configuration is not frozen."""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_freeze_record(root: Path | None = None) -> dict[str, Any] | None:
    p = (root or repo_root()) / FREEZE_RECORD
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def protocol_status(experiment_id: str, root: Path | None = None, cfg: dict[str, Any] | None = None) -> tuple[bool, str]:
    """(frozen, reason). See the module docstring for the rules."""
    root = root or repo_root()
    parent = root / "research" / "protocol.md"
    if not parent.is_file():
        return False, "research/protocol.md not found"
    if "Not frozen" in parent.read_text(encoding="utf-8"):
        return False, "research/protocol.md declares itself not frozen"
    try:
        record = load_freeze_record(root)
    except json.JSONDecodeError as exc:
        return False, f"freeze record is not valid JSON: {exc}"
    if record is None:
        return False, f"freeze record {FREEZE_RECORD.as_posix()} not found"
    parent_hash = (record.get("protocol") or {}).get("sha256", "")
    if not HEX64.match(str(parent_hash)):
        return False, "freeze record has no SHA-256 for research/protocol.md"
    actual_parent = sha256_file(parent)
    if actual_parent != parent_hash:
        return False, f"research/protocol.md changed since the freeze (recorded {parent_hash[:12]}, file {actual_parent[:12]})"
    entry = (record.get("experiments") or {}).get(experiment_id)
    if entry is None:
        return False, f"{experiment_id} is not frozen in the freeze record"

    reg = root / "research" / "experiment_registry.csv"
    if not reg.is_file():
        return False, "experiment registry not found"
    with reg.open(newline="", encoding="utf-8") as fh:
        rows = {r["experiment_id"]: r for r in csv.DictReader(fh)}
    row = rows.get(experiment_id)
    if row is None:
        return False, f"{experiment_id} is not registered"
    recorded = (row.get("protocol_hash") or "").strip()
    if not HEX64.match(recorded):
        return False, f"{experiment_id} has no recorded protocol hash ({recorded!r})"
    if recorded != entry.get("protocol_sha256"):
        return False, f"{experiment_id} registry hash and freeze record disagree"
    proto = root / row["protocol_path"]
    if not proto.is_file():
        return False, f"protocol file missing: {row['protocol_path']}"
    actual = sha256_file(proto)
    if actual != recorded:
        return False, f"{experiment_id} protocol hash mismatch (recorded {recorded[:12]}, file {actual[:12]})"

    if cfg is not None:
        from .config import config_hash

        allowed = {c.get("config_hash") for c in entry.get("configs", [])}
        h = config_hash(cfg)
        if h not in allowed:
            return False, f"{experiment_id} configuration {h[:12]} is not one of the frozen configurations"
    return True, "frozen"


def require_frozen(experiment_id: str, root: Path | None = None, cfg: dict[str, Any] | None = None) -> None:
    ok, reason = protocol_status(experiment_id, root, cfg)
    if not ok:
        raise NotFrozenError(f"refusing confirmatory run of {experiment_id}: {reason}")
