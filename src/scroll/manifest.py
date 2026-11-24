# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Run manifest: configuration hash, seeds, git revision, versions, platform, runtime, memory."""
from __future__ import annotations

import datetime as dt
import os
import platform
import resource
import subprocess
import sys
from importlib import metadata
from pathlib import Path
from typing import Any

from . import __version__

PACKAGES = ("playwright", "numpy", "scipy", "jsonschema", "matplotlib")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_info(root: Path | None = None) -> dict[str, Any]:
    root = root or repo_root()
    try:
        rev = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip())
        return {"revision": rev, "dirty": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"revision": None, "dirty": None}


def versions() -> dict[str, str | None]:
    out: dict[str, str | None] = {"scroll": __version__, "python": sys.version.split()[0]}
    for p in PACKAGES:
        try:
            out[p] = metadata.version(p)
        except metadata.PackageNotFoundError:
            out[p] = None
    return out


def _sysctl(name: str) -> str | None:
    try:
        return subprocess.run(["sysctl", "-n", name], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def platform_info() -> dict[str, Any]:
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "mac_ver": platform.mac_ver()[0] or None,
        "machine": platform.machine(),
        "cpu": _sysctl("machdep.cpu.brand_string") or platform.processor() or None,
        "ncpu": os.cpu_count(),
        "memsize_bytes": int(_sysctl("hw.memsize")) if _sysctl("hw.memsize") else None,
    }


def load_average() -> list[float] | None:
    try:
        return [round(x, 2) for x in os.getloadavg()]
    except OSError:
        return None


def peak_rss_bytes() -> int:
    """Peak resident set size of this Python process (the browser is not included)."""
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(r if sys.platform == "darwin" else r * 1024)


def new_manifest(run_id: str, cfg: dict[str, Any], cfg_hash: str) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "experiment_id": cfg["experiment_id"],
        "label": cfg["label"],
        "config_hash": cfg_hash,
        "seeds": list(cfg["seeds"]),
        "git": git_info(),
        "versions": versions(),
        "platform": platform_info(),
        "started_at": utc_now(),
        "finished_at": None,
        "runtime_s": None,
        "peak_rss_bytes": None,
        "load_average_start": load_average(),
        "load_average_end": None,
        "browser": {},
        "notes": "Timings measured while other agents ran on the same machine are noisy; see progress.md.",
    }
