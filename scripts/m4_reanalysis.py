# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""M4 exploratory re-analysis of committed confirmatory raw results (no browser, no new measurement).

EXPLORATORY. Every output of this script is post hoc and labelled exploratory. It never changes or
replaces a frozen verdict; the frozen verdicts remain those in results/raw/*/report/inference.json and
results/raw/EXP-004/sensitivity/. Inputs are the committed results.json files only.

Analyses:
  X1  Both test readings (DEC-011): Holm-adjusted Wilcoxon versus the unadjusted 95% bootstrap interval.
  X2  Frame-timing decomposition per cell and arm (first-frame latency, second-frame gap, Element Timing
      offset), and the trial-level distribution of SKELETON - BLANK at L = 50 ms.
  X3  Hover-lead (A3) exclusion sensitivity: EXP-002 primary contrasts with the excluded trials kept.
  X4  Interval-based reading of the EXP-004 robustness table (post hoc, not the frozen rule).
  X5  Arm-order check: per-seed paired differences split by whether the arm ran before BLANK.

Usage: PYTHONPATH=src .venv/bin/python scripts/m4_reanalysis.py --out results/exploratory/M4-REANALYSIS
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path

import numpy as np

from scroll import analysis, inference, stats

ROOT = Path(__file__).resolve().parents[1]
RUNS = {
    "EXP-002": "results/raw/EXP-002/EXP-002-20261125T070315Z",
    "EXP-003": "results/raw/EXP-003/EXP-003-20261125T080838Z",
    "EXP-004-S2": "results/raw/EXP-004/EXP-004-20261125T095434Z",
    "EXP-004-S3": "results/raw/EXP-004/EXP-004-20261125T103912Z",
    "EXP-004-S4": "results/raw/EXP-004/EXP-004-20261125T110537Z",
}
SENS_LONG = "results/raw/EXP-004/sensitivity/sensitivity_long.csv"
SENS_VERDICTS = "results/raw/EXP-004/sensitivity/sensitivity_verdicts.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(name: str) -> dict:
    with open(ROOT / RUNS[name] / "results.json") as f:
        return json.load(f)


def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        path.write_text("")
        return
    cols = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})


def x1_readings() -> list[dict]:
    rows = []
    for exp in ("EXP-002", "EXP-003"):
        with open(ROOT / RUNS[exp] / "report" / "inference.json") as f:
            inf = json.load(f)
        for c in inf["contrasts"]:
            rows.append({
                "experiment": exp, "cell": c["cell"], "contrast": c["contrast"], "stratum": c["stratum"],
                "median_diff_ms": c["median_diff_ms"], "ci95_low_ms": c["ci95_low_ms"], "ci95_high_ms": c["ci95_high_ms"],
                "holm_p": c["holm_p"],
                "reading_A_holm_wilcoxon_reject": c["reject_h0"],
                "reading_B_ci95_excludes_0": c["ci95_excludes_0"],
                "readings_disagree": c["readings_disagree"],
                "equivalent_17ms": c["equivalent_17ms"],
            })
    return rows


def _ok(m: dict) -> bool:
    return m["status"] == "ok"


def x2_frames(results: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    rows = []
    for exp, res in results.items():
        groups: dict[tuple, list[dict]] = defaultdict(list)
        for s in res["sessions"]:
            if s["status"] != "ok":
                continue
            ck = analysis.cell_key(s["spec"])
            for t in s["trials"]:
                if _ok(t["metrics"]):
                    groups[(ck, s["spec"]["arm"])].append(t["metrics"])
        for (ck, arm), ms in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            def med(f):
                v = [f(m) for m in ms]
                v = [x for x in v if x is not None]
                return float(np.median(v)) if v else None
            rows.append({
                "run": exp, "cell": analysis.cell_label(ck), "arm": arm, "trials": len(ms),
                "median_ttuc_ms": med(lambda m: m["ttuc_ms"]),
                "median_first_frame_excess_ms": med(lambda m: None if m.get("ttuc_raf1_ms") is None else m["ttuc_raf1_ms"] - m["ttuc_reference_ms"]),
                "median_second_frame_gap_ms": med(lambda m: None if m.get("ttuc_raf1_ms") is None else m["ttuc_ms"] - m["ttuc_raf1_ms"]),
                "median_element_minus_raf1_ms": med(lambda m: None if (m.get("ttuc_raf1_ms") is None or m.get("ttuc_element_ms") is None) else m["ttuc_element_ms"] - m["ttuc_raf1_ms"]),
                "share_first_frame_before_reference": (lambda v: float(np.mean(v)) if v else None)(
                    [m["ttuc_raf1_ms"] < m["ttuc_reference_ms"] for m in ms if m.get("ttuc_raf1_ms") is not None]),
                "share_main_ttuc_before_reference": float(np.mean([m["ttuc_ms"] < m["ttuc_reference_ms"] for m in ms])),
                "share_second_frame_gap_over_20ms": (lambda v: float(np.mean(v)) if v else None)(
                    [ (m["ttuc_ms"] - m["ttuc_raf1_ms"]) > 20 for m in ms if m.get("ttuc_raf1_ms") is not None]),
            })
    # Trial-level SKELETON - BLANK at L = 50 ms (EXP-002), paired by (seed, k)
    res = results["EXP-002"]
    data = analysis.ok_trials_by_k(res)
    ck = ("read", 50.0, 0.0, 150.0)
    dist = []
    for metric in ("ttuc_ms", "ttuc_raf1_ms", "ttuc_element_ms"):
        diffs = []
        for seed in sorted(set(data[ck]["SKELETON"]) & set(data[ck]["BLANK"])):
            ta, tb = data[ck]["SKELETON"][seed], data[ck]["BLANK"][seed]
            for k in sorted(set(ta) & set(tb)):
                if ta[k].get(metric) is not None and tb[k].get(metric) is not None:
                    diffs.append(ta[k][metric] - tb[k][metric])
        a = np.array(diffs)
        dist.append({
            "metric": metric, "trial_pairs": int(a.size), "median_ms": float(np.median(a)),
            "q25_ms": float(np.percentile(a, 25)), "q75_ms": float(np.percentile(a, 75)),
            "min_ms": float(a.min()), "max_ms": float(a.max()),
            "share_below_minus_25ms": float(np.mean(a < -25)), "share_minus_25_to_minus_8ms": float(np.mean((a >= -25) & (a < -8))),
            "share_minus_8_to_plus_8ms": float(np.mean((a >= -8) & (a <= 8))), "share_above_plus_8ms": float(np.mean(a > 8)),
        })
    return rows, dist


def x3_a3_inclusion(res: dict) -> list[dict]:
    frozen = {(c["cell"], c["contrast"]): c for c in inference.primary_inference(res)["contrasts"]}
    alt = copy.deepcopy(res)
    n_restored = 0
    for s in alt["sessions"]:
        for t in s["trials"]:
            m = t["metrics"]
            if m["status"] == "excluded" and (m.get("exclusion_reason") or "").startswith("hover lead") and m.get("ttuc_ms") is not None:
                m["status"] = "ok"
                n_restored += 1
    incl = inference.primary_inference(alt)["contrasts"]
    rows = []
    for c in incl:
        f = frozen[(c["cell"], c["contrast"])]
        rows.append({
            "cell": c["cell"], "contrast": c["contrast"],
            "frozen_trial_pairs": f["trial_pairs"], "included_trial_pairs": c["trial_pairs"],
            "frozen_median_ms": f["median_diff_ms"], "included_median_ms": c["median_diff_ms"],
            "included_ci95_low_ms": c["ci95_low_ms"], "included_ci95_high_ms": c["ci95_high_ms"],
            "frozen_holm_p": f["holm_p"], "included_holm_p": c["holm_p"],
            "frozen_reject": f["reject_h0"], "included_reject": c["reject_h0"],
            "frozen_equivalent": f["equivalent_17ms"], "included_equivalent": c["equivalent_17ms"],
            "verdict_changed": (f["reject_h0"] != c["reject_h0"]) or (f["equivalent_17ms"] != c["equivalent_17ms"]),
            "restored_trials_total": n_restored,
        })
    return rows


def x4_interval_robustness() -> list[dict]:
    lv: dict[tuple, list[dict]] = defaultdict(list)
    with open(ROOT / SENS_LONG) as f:
        for r in csv.DictReader(f):
            lv[(r["path"], r["L"], r["p"], r["arm"], r["stratum"])].append(r)
    frozen = {}
    with open(ROOT / SENS_VERDICTS) as f:
        for r in csv.DictReader(f):
            frozen[(r["path"], r["L"], r["p"], r["arm"], r["stratum"])] = r["verdict"]
    rows = []
    for k, levels in lv.items():
        if k[3] == "SKELETON":
            continue  # the frozen SKELETON rule is already interval-based (TOST)
        cls = []
        for r in levels:
            lo, hi = float(r["ci95_low_ms"]), float(r["ci95_high_ms"])
            cls.append("neg" if hi < 0 else ("pos" if lo > 0 else "zero"))
        kinds = set(cls)
        if kinds == {"zero"}:
            reading = "consistent: every level's 95% interval includes 0"
        elif len(kinds) == 1:
            reading = "consistent: every level's 95% interval excludes 0 on the same side"
        elif kinds == {"neg", "pos"} or kinds == {"neg", "pos", "zero"}:
            reading = "inconsistent: intervals exclude 0 on opposite sides"
        else:
            reading = "mixed: some levels exclude 0 and others include it"
        rows.append({"path": k[0], "L": k[1], "p": k[2], "arm": k[3], "stratum": k[4],
                     "levels": ";".join(r["level"] for r in levels), "interval_classes": ";".join(cls),
                     "exploratory_interval_reading": reading, "frozen_verdict": frozen.get(k)})
    return rows


def x5_order(results: dict[str, dict]) -> list[dict]:
    rows = []
    for exp in ("EXP-002", "EXP-003"):
        res = results[exp]
        order = {}
        for s in res["sessions"]:
            sp = s["spec"]
            order[(analysis.cell_key(sp), sp["arm"], int(sp["seed"]))] = int(sp["order_in_block"])
        for c in inference.contrast_rows(res, n_boot=1000):
            ck_label = c["cell"]
            ck = next(k for k in {kk[0] for kk in order} if analysis.cell_label(k) == ck_label)
            arm = c["arm"]
            before, after = [], []
            seeds = [s for s in range(1, 21) if (ck, arm, s) in order and (ck, "BLANK", s) in order]
            # diffs_ms are aligned with the sorted seeds that contributed; rebuild that list
            data = analysis.ok_trials_by_k(res)
            contrib = []
            for seed in sorted(set(data[ck][arm]) & set(data[ck]["BLANK"])):
                ta, tb = data[ck][arm][seed], data[ck]["BLANK"][seed]
                ok = False
                for kk in set(ta) & set(tb):
                    mb = tb[kk]
                    if c["stratum"] in ("all",) or (c["stratum"] == "success" and mb.get("request_ok") is True) or (c["stratum"] == "failure" and mb.get("request_ok") is False):
                        ok = True
                        break
                if ok:
                    contrib.append(seed)
            assert len(contrib) == len(c["diffs_ms"]), (exp, ck_label, arm, c["stratum"])
            for seed, d in zip(contrib, c["diffs_ms"]):
                (before if order[(ck, arm, seed)] < order[(ck, "BLANK", seed)] else after).append(d)
            rows.append({"experiment": exp, "cell": ck_label, "contrast": c["contrast"], "stratum": c["stratum"],
                         "seeds_arm_first": len(before), "median_arm_first_ms": float(np.median(before)) if before else None,
                         "seeds_blank_first": len(after), "median_blank_first_ms": float(np.median(after)) if after else None,
                         "difference_of_medians_ms": (float(np.median(before)) - float(np.median(after))) if before and after else None,
                         "seeds_checked": len(seeds)})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    results = {n: load(n) for n in RUNS}
    write_csv(x1_readings(), out / "x1_test_readings.csv")
    frames, dist = x2_frames(results)
    write_csv(frames, out / "x2_frame_decomposition.csv")
    write_csv(dist, out / "x2_skeleton_l50_trial_distribution.csv")
    write_csv(x3_a3_inclusion(results["EXP-002"]), out / "x3_a3_inclusion_exp002.csv")
    write_csv(x4_interval_robustness(), out / "x4_interval_robustness.csv")
    write_csv(x5_order(results), out / "x5_arm_order.csv")
    rev = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True).stdout.strip())
    inputs = {f"{RUNS[n]}/results.json": sha256(ROOT / RUNS[n] / "results.json") for n in RUNS}
    for exp in ("EXP-002", "EXP-003"):
        p = f"{RUNS[exp]}/report/inference.json"
        inputs[p] = sha256(ROOT / p)
    for p in (SENS_LONG, SENS_VERDICTS):
        inputs[p] = sha256(ROOT / p)
    manifest = {
        "label": "exploratory (M4, post hoc re-analysis of committed raw results; no browser run)",
        "never_replaces": "frozen verdicts in results/raw/*/report/inference.json and results/raw/EXP-004/sensitivity/",
        "script": "scripts/m4_reanalysis.py", "code_revision": rev, "tree_dirty_at_run": dirty,
        "command": f"PYTHONPATH=src .venv/bin/python scripts/m4_reanalysis.py --out {args.out}",
        "bootstrap": "percentile, 10,000 resamples, seed 20261124 (stats.bootstrap_ci defaults); X5 uses 1,000 only for the unused intervals",
        "inputs_sha256": inputs,
        "outputs_sha256": {p.name: sha256(p) for p in sorted(out.glob("*.csv"))},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(json.dumps({"outputs": sorted(manifest["outputs_sha256"])}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
