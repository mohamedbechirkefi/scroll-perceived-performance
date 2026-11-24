# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Descriptive analysis of a validated result: cell summaries, paired seed-level contrasts,
degenerate-case detection and runtime projection. Pure functions over the result dict."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

from . import stats
from .config import BASELINE, expand_sessions

PAIRED_METRICS = {"double_raf": "ttuc_ms", "raf1": "ttuc_raf1_ms", "element": "ttuc_element_ms"}


def cell_key(spec: dict[str, Any]) -> tuple[str, float, float, float]:
    return (spec["path"], float(spec["latency_ms"]), float(spec["failure_prob"]), float(spec["hover_lead_ms"]))


def cell_label(key: tuple[str, float, float, float]) -> str:
    path, L, p, h = key
    s = f"{path} L={L:g}"
    if path == "write":
        s += f" p={p:g}"
    else:
        s += f" h={h:g}"
    return s


def _ok_trials(session: dict[str, Any]) -> list[dict[str, Any]]:
    if session["status"] != "ok":
        return []
    return [t["metrics"] for t in session["trials"] if t["metrics"]["status"] == "ok"]


def _vals(ms: list[dict[str, Any]], key: str) -> list[float]:
    return [float(m[key]) for m in ms if m.get(key) is not None]


def _med(v: list[float]) -> float | None:
    return float(np.median(v)) if v else None


def seed_medians(result: dict[str, Any], metric: str = "ttuc_ms") -> dict[tuple, dict[str, dict[int, float]]]:
    """{cell: {arm: {seed: median metric over that session's ok trials}}}."""
    out: dict[tuple, dict[str, dict[int, float]]] = defaultdict(lambda: defaultdict(dict))
    for s in result["sessions"]:
        v = _vals(_ok_trials(s), metric)
        if v:
            out[cell_key(s["spec"])][s["spec"]["arm"]][int(s["spec"]["seed"])] = float(np.median(v))
    return out


def cell_summaries(result: dict[str, Any]) -> list[dict[str, Any]]:
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for s in result["sessions"]:
        groups[(cell_key(s["spec"]), s["spec"]["arm"])].append(s)
    sm = seed_medians(result)
    rows = []
    for (ck, arm), sessions in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        ms = [m for s in sessions for m in _ok_trials(s)]
        all_trials = [t for s in sessions for t in s["trials"]]
        ttuc = _vals(ms, "ttuc_ms")
        per_seed = list(sm.get(ck, {}).get(arm, {}).values())
        q = stats.iqr(ttuc) if ttuc else (None, None)
        excess = _vals(ms, "ttuc_excess_ms")
        el = [m["ttuc_element_ms"] - m["ttuc_ms"] for m in ms if m.get("ttuc_element_ms") is not None]
        ev = [m for m in ms if m.get("event_below_threshold") is not None]
        rows.append({
            "cell": cell_label(ck), "arm": arm, "sessions": len(sessions),
            "sessions_failed": sum(1 for s in sessions if s["status"] != "ok"),
            "trials": len(all_trials), "trials_ok": len(ms), "trials_excluded": len(all_trials) - len(ms),
            "seeds": len(per_seed),
            "ttuc_median_ms": _med(ttuc), "ttuc_q1_ms": q[0], "ttuc_q3_ms": q[1],
            "seed_median_min_ms": min(per_seed) if per_seed else None, "seed_median_max_ms": max(per_seed) if per_seed else None,
            "seed_median_sd_ms": stats.sd(per_seed) if len(per_seed) >= 2 else None,
            "ttff_median_ms": _med(_vals(ms, "ttff_ms")),
            "excess_min_ms": min(excess) if excess else None, "excess_median_ms": _med(excess),
            "element_minus_raf2_median_ms": _med(el), "element_available": len(el),
            "event_below_threshold_share": (sum(1 for m in ev if m["event_below_threshold"]) / len(ev)) if ev else None,
            "input_to_handler_median_ms": _med(_vals(ms, "input_to_handler_ms")),
            "hover_lead_excluded": sum(1 for t in all_trials if (t["metrics"].get("exclusion_reason") or "").startswith("hover lead")),
            "layout_shift_all_median": _med(_vals(ms, "layout_shift_all")),
            "layout_shift_cls_median": _med(_vals(ms, "layout_shift_cls")),
            "wrong_state_median_ms": _med(_vals(ms, "wrong_state_ms")),
            "false_state_median_ms": _med(_vals(ms, "false_state_ms")),
            "failures_injected": sum(1 for m in ms if m.get("request_ok") is False),
            "final_correct_share": (sum(1 for m in ms if m.get("final_correct")) / len(ms)) if ms else None,
            "prefetch_hit_share": (sum(1 for m in ms if m.get("prefetch_hit")) / len(ms)) if arm == "PREFETCH" and ms else None,
            "defects": sum(len(m["defects"]) for m in ms),
            "session_wall_median_s": _med([s["wall_s"] for s in sessions]),
        })
    return rows


def _interval_fields(row: dict[str, Any], diffs: list[float], delta: float, n_boot: int) -> None:
    row["median_diff_ms"] = float(np.median(diffs)) if diffs else None
    if len(diffs) >= 2:
        row["ci95_low_ms"], row["ci95_high_ms"] = stats.bootstrap_ci(diffs, n_resamples=n_boot)
        row["sigma_d_ms"] = stats.sd(diffs)
        row["sigma_d_ci95_low_ms"], row["sigma_d_ci95_high_ms"] = stats.bootstrap_ci(
            diffs, stat=lambda a: float(np.std(a, ddof=1)), n_resamples=n_boot)
        row["required_n"] = stats.required_n(row["sigma_d_ms"], delta)
        row["required_n_at_sigma_upper"] = stats.required_n(row["sigma_d_ci95_high_ms"], delta)
    else:
        for k in ("ci95_low_ms", "ci95_high_ms", "sigma_d_ms", "sigma_d_ci95_low_ms", "sigma_d_ci95_high_ms", "required_n", "required_n_at_sigma_upper"):
            row[k] = None


def ok_trials_by_k(result: dict[str, Any]) -> dict[tuple, dict[str, dict[int, dict[int, dict[str, Any]]]]]:
    """{cell: {arm: {seed: {k: metrics of an ok trial}}}}; failed sessions contribute nothing."""
    out: dict[tuple, dict[str, dict[int, dict[int, dict[str, Any]]]]] = defaultdict(lambda: defaultdict(dict))
    for s in result["sessions"]:
        if s["status"] != "ok":
            continue
        by_k = {int(t["k"]): t["metrics"] for t in s["trials"] if t["metrics"]["status"] == "ok"}
        out[cell_key(s["spec"])][s["spec"]["arm"]][int(s["spec"]["seed"])] = by_k
    return out


def strata_for(ck: tuple[str, float, float, float]) -> list[tuple[str, str]]:
    """(stratum, role) pairs for a cell. Amendment A2: write cells with p > 0 are split by outcome;
    the mixed stratum is secondary. At p = 0 every trial succeeds, so the success stratum is the cell."""
    path, _, p, _ = ck
    if path == "read":
        return [("all", "primary")]
    if p == 0:
        return [("success", "primary")]
    return [("success", "primary"), ("failure", "primary"), ("mixed", "secondary")]


def _in_stratum(stratum: str, m: dict[str, Any]) -> bool:
    if stratum in ("all", "mixed"):
        return True
    return (m.get("request_ok") is True) if stratum == "success" else (m.get("request_ok") is False)


def trial_paired_contrasts(result: dict[str, Any], metric: str = "ttuc_ms", delta: float = 17.0,
                           n_boot: int = 10_000) -> list[dict[str, Any]]:
    """Primary estimand (amendment A1): within each seed, trial k of an arm is paired with trial k of
    BLANK (same scheduled delay and outcome); the seed contributes the median of its trial-level
    differences; the estimate is the median over seeds, with a percentile bootstrap over seeds.
    The seed stays the independent unit. Pairs whose scheduled outcome differs between arms (impossible
    by construction) are dropped and counted in `outcome_mismatches`."""
    rows = []
    data = ok_trials_by_k(result)
    for ck in sorted(data):
        arms = data[ck]
        if BASELINE not in arms:
            continue
        for arm in sorted(a for a in arms if a != BASELINE):
            for stratum, role in strata_for(ck):
                per_seed: dict[int, float] = {}
                n_pairs = 0
                mismatches = 0
                for seed in sorted(set(arms[arm]) & set(arms[BASELINE])):
                    ta, tb = arms[arm][seed], arms[BASELINE][seed]
                    diffs = []
                    for k in sorted(set(ta) & set(tb)):
                        ma, mb = ta[k], tb[k]
                        if ma.get(metric) is None or mb.get(metric) is None:
                            continue
                        if ck[0] == "write" and ma.get("request_ok") != mb.get("request_ok"):
                            mismatches += 1
                            continue
                        if not _in_stratum(stratum, mb):
                            continue
                        diffs.append(float(ma[metric]) - float(mb[metric]))
                    if diffs:
                        per_seed[seed] = float(np.median(diffs))
                        n_pairs += len(diffs)
                row: dict[str, Any] = {"cell": cell_label(ck), "contrast": f"{arm} - {BASELINE}", "stratum": stratum, "role": role,
                                       "metric": metric, "pairs": len(per_seed), "trial_pairs": n_pairs,
                                       "outcome_mismatches": mismatches, "seeds": sorted(per_seed),
                                       "diffs_ms": [round(per_seed[s], 3) for s in sorted(per_seed)]}
                _interval_fields(row, [per_seed[s] for s in sorted(per_seed)], delta, n_boot)
                rows.append(row)
    return rows


def paired_contrasts(result: dict[str, Any], delta: float = 17.0, n_boot: int = 10_000) -> list[dict[str, Any]]:
    """Draft estimand, kept as a secondary descriptive analysis after amendment A1: per-seed differences
    of session medians (arm minus BLANK) within each cell, for each paint-time method."""
    rows = []
    per_method = {meth: seed_medians(result, key) for meth, key in PAIRED_METRICS.items()}
    main = per_method["double_raf"]
    for ck in sorted(main):
        arms = main[ck]
        if BASELINE not in arms:
            continue
        for arm in sorted(a for a in arms if a != BASELINE):
            d = stats.paired_differences(arms[arm], arms[BASELINE])
            diffs = list(d.values())
            row: dict[str, Any] = {"cell": cell_label(ck), "contrast": f"{arm} - {BASELINE}", "pairs": len(diffs),
                                   "diffs_ms": [round(x, 3) for x in diffs]}
            _interval_fields(row, diffs, delta, n_boot)
            for meth in ("raf1", "element"):
                a2 = per_method[meth].get(ck, {})
                if arm in a2 and BASELINE in a2:
                    try:
                        row[f"median_diff_{meth}_ms"] = float(np.median(list(stats.paired_differences(a2[arm], a2[BASELINE]).values())))
                    except stats.StatsError:
                        row[f"median_diff_{meth}_ms"] = None
                else:
                    row[f"median_diff_{meth}_ms"] = None
            rows.append(row)
    return rows


def degenerate_cases(result: dict[str, Any], contrasts: list[dict[str, Any]], cells: list[dict[str, Any]]) -> list[str]:
    notes = []
    for c in contrasts:
        tag = f"{c['cell']} {c['contrast']}" + (f" [{c['stratum']}]" if c.get("stratum") else "")
        if c.get("outcome_mismatches"):
            notes.append(f"{tag}: {c['outcome_mismatches']} trial pair(s) with different scheduled outcomes (defect: common random numbers broken).")
        if c["pairs"] < 2:
            notes.append(f"{tag}: fewer than two matched seeds; no interval.")
        elif c["sigma_d_ms"] == 0:
            notes.append(f"{tag}: zero spread between seeds.")
    for r in cells:
        if r["trials_excluded"]:
            notes.append(f"{r['cell']} {r['arm']}: {r['trials_excluded']} excluded trial(s).")
        if r["sessions_failed"]:
            notes.append(f"{r['cell']} {r['arm']}: {r['sessions_failed']} failed session(s).")
        if r["event_below_threshold_share"] is not None and r["event_below_threshold_share"] >= 0.5:
            notes.append(f"{r['cell']} {r['arm']}: Event Timing duration below the 16 ms threshold in {r['event_below_threshold_share']:.0%} of trials (metric mostly unobservable; descriptive only, amendment A4).")
        if r["element_available"] == 0 and r["cell"].startswith("read"):
            notes.append(f"{r['cell']} {r['arm']}: no Element Timing entries.")
        if r["defects"]:
            notes.append(f"{r['cell']} {r['arm']}: {r['defects']} defect flag(s) (stop-rule checks).")
    # write cells with p > 0: seeds whose sessions saw no failure (per-seed median then ignores failures)
    by_seed: dict[tuple, list[int]] = defaultdict(list)
    for s in result["sessions"]:
        sp = s["spec"]
        if sp["path"] == "write" and sp["failure_prob"] > 0:
            n_fail = sum(1 for m in _ok_trials(s) if m.get("request_ok") is False)
            by_seed[(cell_key(sp), sp["arm"])].append(n_fail)
    for (ck, arm), fails in sorted(by_seed.items()):
        K = result["config"]["interactions_per_session"]
        zero = sum(1 for f in fails if f == 0)
        major = sum(1 for f in fails if f > K / 2)
        if zero or major:
            notes.append(f"{cell_label(ck)} {arm}: failures per session {fails} of K={K}; the per-seed median TTUC reflects "
                         f"{'only successes' if zero else ''}{' and ' if zero and major else ''}{'mostly failures' if major else ''} in some seeds.")
    for s in result["sessions"]:
        sp = s["spec"]
        if sp["path"] == "read" and sp["arm"] == "PREFETCH" and sp["hover_lead_ms"] >= sp["latency_ms"] * (1 + result["config"]["jitter"]):
            notes.append(f"{cell_label(cell_key(sp))} PREFETCH: lead time h >= maximum delay, so the residual wait is always 0 (TTUC independent of L by construction).")
            break
    return notes


def runtime_model(result: dict[str, Any]) -> dict[str, float]:
    """Fit wall(session) = a + sum_k [c + (d_k + settle + pre_input + h) / 1000] from ok trials."""
    cfg = result["config"]
    fixed = (cfg["settle_ms"] + cfg["pre_input_ms"]) / 1000
    over_trial, over_session = [], []
    for s in result["sessions"]:
        if s["status"] != "ok":
            continue
        h = s["spec"]["hover_lead_ms"] / 1000
        for t in s["trials"]:
            m = t["metrics"]
            if m["status"] == "ok":
                over_trial.append(t["wall_s"] - (m["delay_ms"] / 1000 + fixed + h))
        over_session.append(s["wall_s"] - sum(t["wall_s"] for t in s["trials"]))
    if not over_trial or not over_session:
        raise stats.StatsError("no ok trials to fit the runtime model")
    return {"trial_overhead_s": float(np.median(over_trial)), "session_overhead_s": float(np.median(over_session)),
            "trial_overhead_p90_s": float(np.percentile(over_trial, 90)),
            "session_wall_median_s": float(np.median([s["wall_s"] for s in result["sessions"]])),
            "trial_wall_median_s": float(np.median([t["wall_s"] for s in result["sessions"] for t in s["trials"] if t["metrics"]["status"] == "ok"]))}


def project_runtime(model: dict[str, float], cfg: dict[str, Any]) -> dict[str, Any]:
    """Projected wall-clock for a config (uses the nominal latency L as the expected delay)."""
    sessions = expand_sessions(cfg)
    K = cfg["interactions_per_session"]
    fixed = (cfg["settle_ms"] + cfg["pre_input_ms"]) / 1000
    total = 0.0
    for sp in sessions:
        total += model["session_overhead_s"] + K * (model["trial_overhead_s"] + sp.latency_ms / 1000 + fixed + sp.hover_lead_ms / 1000)
    return {"experiment_id": cfg["experiment_id"], "description": cfg["description"], "sessions": len(sessions),
            "interactions": len(sessions) * K, "projected_s": total,
            "cpu_throttle": cfg["browser"]["cpu_throttle"], "headless": cfg["browser"]["headless"]}
