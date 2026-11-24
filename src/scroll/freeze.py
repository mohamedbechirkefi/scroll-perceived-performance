# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Read-only freeze check. This module never freezes anything (gate G-FREEZE belongs to the owner)."""
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

from .manifest import repo_root

HEX64 = re.compile(r"^[0-9a-f]{64}$")


class NotFrozenError(RuntimeError):
    """A confirmatory run was requested while its protocol is not frozen."""


def protocol_status(experiment_id: str, root: Path | None = None) -> tuple[bool, str]:
    """(frozen, reason). Frozen only if the registry records a SHA-256 that matches the protocol file
    and the parent protocol no longer declares itself unfrozen."""
    root = root or repo_root()
    parent = root / "research" / "protocol.md"
    if not parent.is_file():
        return False, "research/protocol.md not found"
    if "Not frozen" in parent.read_text(encoding="utf-8"):
        return False, "research/protocol.md declares itself not frozen"
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
    proto = root / row["protocol_path"]
    if not proto.is_file():
        return False, f"protocol file missing: {row['protocol_path']}"
    actual = hashlib.sha256(proto.read_bytes()).hexdigest()
    if actual != recorded:
        return False, f"{experiment_id} protocol hash mismatch (recorded {recorded[:12]}, file {actual[:12]})"
    return True, "frozen"


def require_frozen(experiment_id: str, root: Path | None = None) -> None:
    ok, reason = protocol_status(experiment_id, root)
    if not ok:
        raise NotFrozenError(f"refusing confirmatory run of {experiment_id}: {reason}")
