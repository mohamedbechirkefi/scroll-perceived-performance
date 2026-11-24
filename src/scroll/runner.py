# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Experiment runner: config -> sessions -> validated result file and run manifest."""
from __future__ import annotations

import csv
import datetime as dt
import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .config import config_hash, expand_sessions, validate_config
from .freeze import require_frozen
from .manifest import load_average, new_manifest, peak_rss_bytes, repo_root, utc_now
from .metrics import METRIC_KEYS
from .schema import RESULT_SCHEMA_VERSION, write_result


def default_out_dir(cfg: dict[str, Any], run_id: str) -> Path:
    base = "exploratory" if cfg["label"] == "exploratory" else "raw"
    return repo_root() / "results" / base / cfg["experiment_id"] / run_id


def flatten_trials(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for s in result["sessions"]:
        sp = s["spec"]
        for t in s["trials"]:
            row = {"session_id": sp["session_id"], "seed": sp["seed"], "path": sp["path"], "arm": sp["arm"],
                   "latency_ms": sp["latency_ms"], "failure_prob": sp["failure_prob"], "hover_lead_ms": sp["hover_lead_ms"],
                   "order_in_block": sp["order_in_block"], "session_status": s["status"], "k": t["k"], "trial_wall_s": t["wall_s"]}
            for key in METRIC_KEYS:
                v = t["metrics"][key]
                row[key] = ";".join(v) if isinstance(v, list) else v
            rows.append(row)
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def run_experiment(cfg: dict[str, Any], out_dir: Path | None = None, log: Callable[[str], None] = print,
                   harness_factory: Callable[[dict[str, Any]], Any] | None = None) -> Path:
    validate_config(cfg)
    if cfg["label"] == "confirmatory":
        require_frozen(cfg["experiment_id"])  # raises NotFrozenError; this code never freezes
    sessions = expand_sessions(cfg)
    run_id = f"{cfg['experiment_id']}-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    out = Path(out_dir) if out_dir else default_out_dir(cfg, run_id)
    out.mkdir(parents=True, exist_ok=True)
    h = config_hash(cfg)
    manifest = new_manifest(run_id, cfg, h)
    t0 = time.perf_counter()
    if harness_factory is None:
        from .harness import Harness
        harness_factory = Harness
    records = []
    log(f"[{cfg['label'].upper()}] {run_id}: {len(sessions)} sessions -> {out}")
    with harness_factory(cfg["browser"]) as hz:
        manifest["browser"] = hz.info()
        for i, spec in enumerate(sessions, 1):
            r = hz.run_session(spec, cfg)
            records.append(r)
            ok = sum(1 for t in r["trials"] if t["metrics"]["status"] == "ok")
            log(f"  {i}/{len(sessions)} {spec.session_id} seed={spec.seed} {spec.path}/{spec.arm} L={spec.latency_ms:g} p={spec.failure_prob:g} "
                f"h={spec.hover_lead_ms:g}: {r['status']}, {ok}/{len(r['trials'])} ok, {r['wall_s']:.1f} s")
    manifest["finished_at"] = utc_now()
    manifest["runtime_s"] = time.perf_counter() - t0
    manifest["peak_rss_bytes"] = peak_rss_bytes()
    manifest["load_average_end"] = load_average()
    result = {"schema_version": RESULT_SCHEMA_VERSION, "kind": "scroll.result", "label": cfg["label"],
              "manifest": manifest, "config": cfg, "sessions": records}
    write_result(result, out / "results.json")
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (out / "config.json").write_text(json.dumps(cfg, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(flatten_trials(result), out / "trials.csv")
    log(f"done in {manifest['runtime_s']:.1f} s; results at {out / 'results.json'}")
    return out
