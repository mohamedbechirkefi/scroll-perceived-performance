# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Command-line interface: smoke, run, report, test.

  python -m scroll smoke                         tiny exploratory toolchain run (experiments/smoke.json)
  python -m scroll run --config experiments/EXP-001.json
                                                 refuses confirmatory configs while the protocol is unfrozen
  python -m scroll report --run <run dir> [--pdf]
  python -m scroll test [pytest args]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .config import ConfigError, load_config
from .freeze import NotFrozenError
from .manifest import repo_root
from .schema import SchemaError


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="scroll", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("smoke", help="run the tiny exploratory smoke config")
    s.add_argument("--out", type=Path, default=None)
    s.add_argument("--report", action="store_true", help="also build the report")
    r = sub.add_parser("run", help="run an experiment config")
    r.add_argument("--config", type=Path, required=True)
    r.add_argument("--out", type=Path, default=None)
    rp = sub.add_parser("report", help="build tables, figures and report.md from a run directory")
    rp.add_argument("--run", type=Path, required=True)
    rp.add_argument("--pdf", action="store_true")
    t = sub.add_parser("test", help="run the test suite")
    a, extra = ap.parse_known_args(argv)
    if extra and a.cmd != "test":
        ap.error(f"unrecognized arguments: {' '.join(extra)}")

    try:
        if a.cmd == "test":
            return subprocess.call([sys.executable, "-m", "pytest", *extra], cwd=repo_root())
        if a.cmd == "report":
            from .report import build_report
            print(build_report(a.run, pdf=a.pdf))
            return 0
        from .runner import run_experiment
        cfg = load_config(repo_root() / "experiments" / "smoke.json" if a.cmd == "smoke" else a.config)
        if a.cmd == "smoke" and cfg["label"] != "exploratory":
            raise ConfigError("the smoke config must be exploratory")
        out = run_experiment(cfg, out_dir=a.out)
        if a.cmd == "smoke" and a.report:
            from .report import build_report
            print(build_report(out))
        return 0
    except NotFrozenError as exc:
        print(f"REFUSED: {exc}. Freezing is the owner's decision (G-FREEZE).", file=sys.stderr)
        return 3
    except (ConfigError, SchemaError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
