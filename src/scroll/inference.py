# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Confirmatory inference and EXP-004 sensitivity tables, composed only of frozen pieces.

Written in M3 (2026-11-25) BEFORE any confirmatory output existed (DEC-011). It adds no estimand,
test, interval or tolerance of its own: it wires the frozen primitives of `analysis.py` and
`stats.py` to the frozen decision rules of `research/protocol.md` (sections 4, 6, 7) and of the
EXP-002, EXP-003 and EXP-004 protocols.

- Estimand: `analysis.trial_paired_contrasts` (amendments A1, A2), primary rows only.
- Interval: 95% percentile bootstrap over seeds (10,000 resamples, seed 20261124), unadjusted.
- Test: two-sided Wilcoxon signed-rank on the per-seed values (`stats.wilcoxon_p`), the only
  hypothesis test the protocol names; Holm over the experiment's primary family (`stats.holm`).
  H0 is rejected when the Holm-adjusted p is below 0.05. Whether the unadjusted 95% interval
  excludes 0 is reported next to it; a disagreement between the two is flagged, not resolved.
- SKELETON equivalence: TOST with margin 17 ms through the 90% bootstrap interval
  (`stats.tost_bootstrap`), unadjusted, as the protocol states.
- Failed cell (protocol section 7): more than 5% of the trials of a (cell, arm) group excluded.
  A contrast touching a failed group gets no verdict and enters the Holm family with p = 1, so the
  family size stays the frozen one.
- EXP-004: a verdict is robust only if its sign (SKELETON: its equivalence verdict; its sign is
  shown too) is the same at every factor level. S1 uses both alternative paint methods recorded by
  the frozen code (`raf1`, and Element Timing on the read path): no alternative is selected.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from . import analysis, stats
from .schema import read_result

ALPHA = 0.05
MARGIN_MS = 17.0
EXCLUSION_LIMIT = 0.05
FAMILY_SIZE = {"EXP-002": 8, "EXP-003": 15}
ALT_METHODS = {"raf1": "ttuc_raf1_ms", "element": "ttuc_element_ms"}
_CELL = re.compile(r"^(read|write) L=([0-9.]+) (h|p)=([0-9.]+)$")


def parse_cell(label: str) -> dict[str, Any]:
    m = _CELL.match(label)
    if not m:
        raise ValueError(f"unrecognised cell label {label!r}")
    path, L, kind, v = m.group(1), float(m.group(2)), m.group(3), float(m.group(4))
    return {"path": path, "L": L, "h": v if kind == "h" else None, "p": v if kind == "p" else None}


def failed_groups(result: dict[str, Any]) -> dict[tuple[str, str], float]:
    """{(cell label, arm): excluded share} for groups above the 5% rule (failed sessions count as excluded)."""
    out = {}
    for r in analysis.cell_summaries(result):
        share = (r["trials"] - r["trials_ok"]) / r["trials"] if r["trials"] else 1.0
        if share > EXCLUSION_LIMIT:
            out[(r["cell"], r["arm"])] = share
    return out


def _sign(x: float | None) -> int | None:
    return None if x is None else int(np.sign(x))


def contrast_rows(result: dict[str, Any], metric: str = "ttuc_ms", n_boot: int = 10_000) -> list[dict[str, Any]]:
    """Primary trial-paired rows with Wilcoxon p, TOST (SKELETON) and PREFETCH mechanical check; no Holm yet."""
    failed = failed_groups(result)
    rows = []
    for r in analysis.trial_paired_contrasts(result, metric=metric, n_boot=n_boot):
        if r["role"] != "primary":
            continue
        arm = r["contrast"].split(" - ")[0]
        c = parse_cell(r["cell"])
        diffs = list(r["diffs_ms"])
        row = {k: r[k] for k in ("cell", "contrast", "stratum", "metric", "pairs", "trial_pairs", "outcome_mismatches",
                                 "median_diff_ms", "ci95_low_ms", "ci95_high_ms", "sigma_d_ms")}
        row["arm"] = arm
        row["diffs_ms"] = diffs
        bad = [g for g in ((r["cell"], arm), (r["cell"], "BLANK")) if g in failed]
        row["failed_cell"] = bool(bad)
        row["failed_detail"] = "; ".join(f"{g[0]} {g[1]} excluded {failed[g]:.1%}" for g in bad)
        row["wilcoxon_p"] = stats.wilcoxon_p(diffs) if len(diffs) >= 2 else None
        row["ci95_excludes_0"] = (row["ci95_low_ms"] > 0 or row["ci95_high_ms"] < 0) if row["ci95_low_ms"] is not None else None
        row["sign"] = _sign(row["median_diff_ms"])
        if arm == "SKELETON" and len(diffs) >= 2:
            t = stats.tost_bootstrap(diffs, MARGIN_MS, n_resamples=n_boot)
            row["ci90_low_ms"], row["ci90_high_ms"], row["equivalent_17ms"] = t["ci90_low"], t["ci90_high"], t["equivalent"]
        else:
            row["ci90_low_ms"] = row["ci90_high_ms"] = row["equivalent_17ms"] = None
        if arm == "PREFETCH":
            expected = -min(c["h"], c["L"])
            row["prefetch_expected_ms"] = expected
            row["prefetch_deviation_ms"] = None if row["median_diff_ms"] is None else row["median_diff_ms"] - expected
            row["prefetch_contradiction"] = None if row["median_diff_ms"] is None else abs(row["median_diff_ms"] - expected) > MARGIN_MS
        else:
            row["prefetch_expected_ms"] = row["prefetch_deviation_ms"] = row["prefetch_contradiction"] = None
        rows.append(row)
    return rows


def primary_inference(result: dict[str, Any], n_boot: int = 10_000) -> dict[str, Any]:
    """Holm over the experiment's primary family and the frozen verdict per contrast."""
    exp = result["config"]["experiment_id"]
    rows = contrast_rows(result, n_boot=n_boot)
    expected_m = FAMILY_SIZE.get(exp)
    ps = [1.0 if (r["failed_cell"] or r["wilcoxon_p"] is None) else r["wilcoxon_p"] for r in rows]
    adj = stats.holm(ps) if ps else []
    for r, a in zip(rows, adj):
        r["holm_p"] = a
        if r["failed_cell"]:
            r["verdict"] = "failed cell (more than 5% of trials excluded); no verdict"
            r["reject_h0"] = None
            r["readings_disagree"] = None
            continue
        r["reject_h0"] = a < ALPHA
        r["readings_disagree"] = (r["ci95_excludes_0"] is not None) and (r["reject_h0"] != r["ci95_excludes_0"])
        parts = ["H0 rejected (Holm-adjusted Wilcoxon p < 0.05)" if r["reject_h0"] else "H0 not rejected (Holm-adjusted Wilcoxon p >= 0.05)"]
        if r["arm"] == "SKELETON":
            parts.append("equivalent within 17 ms (TOST, 90% bootstrap)" if r["equivalent_17ms"] else "equivalence not shown (TOST, 90% bootstrap)")
        if r["readings_disagree"]:
            parts.append("the unadjusted 95% interval " + ("excludes" if r["ci95_excludes_0"] else "includes") + " 0 (readings disagree)")
        r["verdict"] = "; ".join(parts)
    return {"experiment_id": exp, "family_size": len(rows), "family_size_frozen": expected_m,
            "family_size_matches": expected_m is None or len(rows) == expected_m, "contrasts": rows,
            "failed_groups": {f"{k[0]} {k[1]}": v for k, v in failed_groups(result).items()},
            "stop_rule": stop_rule_checks(result)}


def stop_rule_checks(result: dict[str, Any]) -> dict[str, Any]:
    """Protocol section 7 stop rule: rollback correctness below 1.0, or BLANK TTUC below the injected delay."""
    write_total = write_correct = blank_below = blank_total = 0
    defects: dict[str, int] = defaultdict(int)
    for s in result["sessions"]:
        for t in s["trials"]:
            m = t["metrics"]
            for d in m.get("defects") or []:
                defects[d] += 1
            if m["status"] != "ok":
                continue
            if s["spec"]["path"] == "write":
                write_total += 1
                write_correct += bool(m.get("final_correct"))
            if s["spec"]["arm"] == "BLANK" and m.get("ttuc_ms") is not None and m.get("delay_ms") is not None:
                blank_total += 1
                blank_below += m["ttuc_ms"] < m["delay_ms"]
    rollback = (write_correct / write_total) if write_total else None
    return {"write_trials": write_total, "rollback_correct_share": rollback, "blank_trials": blank_total,
            "blank_ttuc_below_delay": blank_below, "defect_counts": dict(defects),
            "triggered": bool((rollback is not None and rollback < 1.0) or blank_below)}


def mixed_trend(result: dict[str, Any], n_boot: int = 10_000) -> list[dict[str, Any]]:
    """EXP-003 contradiction check: the mixed (secondary) estimand must decrease in magnitude as p rises."""
    by_L: dict[float, dict[float, float | None]] = defaultdict(dict)
    for r in analysis.trial_paired_contrasts(result, n_boot=n_boot):
        c = parse_cell(r["cell"])
        if c["path"] != "write":
            continue
        if (c["p"] == 0 and r["stratum"] == "success") or r["stratum"] == "mixed":
            by_L[c["L"]][c["p"]] = r["median_diff_ms"]
    out = []
    for L in sorted(by_L):
        ps = sorted(by_L[L])
        mags = [abs(by_L[L][p]) if by_L[L][p] is not None else None for p in ps]
        dec = all(a is not None and b is not None and b < a for a, b in zip(mags, mags[1:]))
        out.append({"L": L, "p_levels": ps, "median_diff_ms": [by_L[L][p] for p in ps], "magnitude_strictly_decreasing": dec,
                    "contradiction": not dec})
    return out


def _key(r: dict[str, Any]) -> tuple:
    c = parse_cell(r["cell"])
    return (c["path"], c["L"], c["p"], r["arm"], r["stratum"])


def _level_entry(r: dict[str, Any]) -> dict[str, Any]:
    return {"median_diff_ms": r["median_diff_ms"], "ci95_low_ms": r["ci95_low_ms"], "ci95_high_ms": r["ci95_high_ms"],
            "pairs": r["pairs"], "sign": r["sign"], "equivalent_17ms": r["equivalent_17ms"], "failed_cell": r["failed_cell"]}


def sensitivity(main: dict[str, dict[str, Any]], s2: dict[str, Any] | None, s3: dict[str, Any] | None,
                s4: dict[str, Any] | None, n_boot: int = 10_000) -> list[dict[str, Any]]:
    """EXP-004 side-by-side table. `main` maps experiment id -> result (EXP-002, EXP-003)."""
    levels: dict[tuple, dict[str, dict[str, Any]]] = defaultdict(dict)
    for res in main.values():
        for r in contrast_rows(res, n_boot=n_boot):
            k = _key(r)
            levels[k]["main"] = _level_entry(r)
            levels[k]["main"]["h"] = parse_cell(r["cell"])["h"]
        for meth, metric in ALT_METHODS.items():
            for r in contrast_rows(res, metric=metric, n_boot=n_boot):
                if r["pairs"]:
                    levels[_key(r)][f"S1-{meth}"] = _level_entry(r)
    for name, res in (("S2-cpu4x", s2), ("S4-headed", s4)):
        if res is None:
            continue
        for r in contrast_rows(res, n_boot=n_boot):
            levels[_key(r)][name] = _level_entry(r)
    if s3 is not None:
        for r in contrast_rows(s3, n_boot=n_boot):
            h = parse_cell(r["cell"])["h"]
            if h is None:  # S3 varies the read-path lead only
                continue
            levels[_key(r)][f"S3-h{h:g}"] = _level_entry(r)
    out = []
    for k in sorted(levels, key=lambda t: tuple("" if x is None else x for x in t)):
        lv = levels[k]
        if "main" not in lv:
            continue
        path, L, p, arm, stratum = k
        in_reduced = L in (300.0, 1000.0) and (path == "read" or p in (0.0, 0.3))
        usable = {n: e for n, e in lv.items() if not e["failed_cell"] and e["median_diff_ms"] is not None}
        if arm == "SKELETON":
            ref = usable.get("main", {}).get("equivalent_17ms")
            changed = sorted(n for n, e in usable.items() if n != "main" and e["equivalent_17ms"] != ref)
        else:
            ref = usable.get("main", {}).get("sign")
            changed = sorted(n for n, e in usable.items() if n != "main" and e["sign"] != ref)
        sign_changed = sorted(n for n, e in usable.items() if n != "main" and e["sign"] != usable.get("main", {}).get("sign"))
        missing = sorted(n for n in lv if n not in usable)
        factors = sorted(n for n in usable if n != "main")
        if "main" not in usable:
            verdict = "main estimate unavailable (failed cell); not assessed"
        elif not changed:
            verdict = "robust" if factors else "no sensitivity level"
        else:
            kinds = []
            if any(n.startswith("S1") for n in changed):
                kinds.append("method-dependent")
            if any(not n.startswith("S1") for n in changed):
                kinds.append("condition-dependent")
            verdict = " and ".join(kinds)
        out.append({"path": path, "L": L, "p": p, "arm": arm, "stratum": stratum, "in_reduced_matrix": in_reduced,
                    "rule_basis": "equivalence verdict" if arm == "SKELETON" else "sign", "levels": lv,
                    "levels_compared": factors, "levels_changed": changed, "sign_changed": sign_changed,
                    "levels_failed": missing, "verdict": verdict})
    return out


def _flat(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{k: (";".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items() if not isinstance(v, dict)} for r in rows]


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    rows = _flat(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def sensitivity_long(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        for name, e in r["levels"].items():
            out.append({"path": r["path"], "L": r["L"], "p": r["p"], "arm": r["arm"], "stratum": r["stratum"], "level": name,
                        **{k: v for k, v in e.items()}, "verdict": r["verdict"]})
    return out


def sensitivity_figure(rows: list[dict[str, Any]], out: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = [r for r in rows if r["in_reduced_matrix"]]
    names = ["main", "S1-raf1", "S1-element", "S2-cpu4x", "S3-h0", "S3-h600", "S4-headed"]
    colors = dict(zip(names, ["#000000", "#1a5fb4", "#26a269", "#a51d2d", "#c64600", "#e5a50a", "#613583"]))
    fig, axes = plt.subplots(len(rows), 1, figsize=(8, 0.9 * len(rows) + 1.0), squeeze=False)
    for ax, r in zip(axes[:, 0], rows):
        for i, n in enumerate(names):
            e = r["levels"].get(n)
            if not e or e["median_diff_ms"] is None:
                continue
            ax.plot([e["median_diff_ms"]], [i], "o", color=colors[n], ms=4)
            if e["ci95_low_ms"] is not None:
                ax.plot([e["ci95_low_ms"], e["ci95_high_ms"]], [i, i], color=colors[n], lw=2, alpha=0.6)
        ax.axvline(0, color="#999", lw=0.8)
        ax.set_yticks(range(len(names)), names, fontsize=5)
        ax.invert_yaxis()
        lab = f"{r['path']} L={r['L']:g}" + (f" p={r['p']:g}" if r["p"] is not None else "") + f" {r['arm']}-BLANK [{r['stratum']}]: {r['verdict']}"
        ax.set_title(lab, fontsize=6, loc="left")
        ax.tick_params(axis="x", labelsize=6)
    axes[-1, 0].set_xlabel("Median over seeds of per-seed median trial-paired TTUC difference, ms (95% percentile bootstrap over seeds)", fontsize=7)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(out.with_suffix(f".{ext}"), dpi=150)
    plt.close(fig)
    return out.with_suffix(".svg")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m scroll.inference", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("primary", help="frozen inference for one run directory (EXP-002 or EXP-003)")
    p.add_argument("--run", type=Path, required=True)
    s = sub.add_parser("sensitivity", help="EXP-004 side-by-side table")
    s.add_argument("--exp002", type=Path, required=True)
    s.add_argument("--exp003", type=Path, required=True)
    s.add_argument("--s2", type=Path)
    s.add_argument("--s3", type=Path)
    s.add_argument("--s4", type=Path)
    s.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.cmd == "primary":
        res = read_result(a.run / "results.json")
        inf = primary_inference(res)
        if res["config"]["experiment_id"] == "EXP-003":
            inf["mixed_trend"] = mixed_trend(res)
        rdir = a.run / "report"
        rdir.mkdir(exist_ok=True)
        (rdir / "inference.json").write_text(json.dumps(inf, indent=1, default=str) + "\n", encoding="utf-8")
        _write_csv(inf["contrasts"], rdir / "inference.csv")
        print(rdir / "inference.json")
        return 0
    load = lambda d: read_result(d / "results.json") if d else None  # noqa: E731
    rows = sensitivity({"EXP-002": load(a.exp002), "EXP-003": load(a.exp003)}, load(a.s2), load(a.s3), load(a.s4))
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "sensitivity.json").write_text(json.dumps(rows, indent=1, default=str) + "\n", encoding="utf-8")
    _write_csv(sensitivity_long(rows), a.out / "sensitivity_long.csv")
    _write_csv([{k: v for k, v in r.items() if k != "levels"} for r in rows], a.out / "sensitivity_verdicts.csv")
    sensitivity_figure(rows, a.out / "figures" / "fig-sensitivity")
    print(a.out / "sensitivity.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
