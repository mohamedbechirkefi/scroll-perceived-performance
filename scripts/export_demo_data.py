# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Export the published results for the M5 demo page (demo/public/data/results.json).

Reads committed files only: the frozen inference outputs of EXP-002 and EXP-003, the EXP-004
sensitivity outputs, the committed cell summaries, the committed exploratory re-analysis tables X6
and X7, the experiment registry, the claims register, the artifact manifest and
research/limitations.md. Nothing is recomputed: every value is copied, and every display string is
formatted exactly as the manuscript prints it (tests/test_demo_export.py checks this).

Output schema: lab-demo-results 1.0.0 (the shared demo template), with these project keys, each
validated fail-closed by demo/src/results.ts:
  traces            per-arm cell medians for the side-by-side trace visual (documented exception:
                    these medians are copied from committed cell_summary.csv and X7 files, and the
                    manuscript prints only their ranges);
  robustness        the EXP-004 verdict of each of the 23 primary contrasts under both S1 readings;
  pending_decisions owner decisions that are still open, each shown with every reading;
  placeholders      owner-only facts that stay placeholders.
Estimates carry optional project fields (group, seeds, holm_p_display, reading_a, reading_b,
tost_display, claim_id). Deterministic: no timestamps; sources are listed with their SHA-256.

Usage: .venv/bin/python scripts/export_demo_data.py [--check]
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo" / "public" / "data" / "results.json"

EXP002 = "results/raw/EXP-002/EXP-002-20261125T070315Z/report/inference.json"
EXP003 = "results/raw/EXP-003/EXP-003-20261125T080838Z/report/inference.json"
CELLS002 = "results/raw/EXP-002/EXP-002-20261125T070315Z/report/cell_summary.csv"
CELLS003 = "results/raw/EXP-003/EXP-003-20261125T080838Z/report/cell_summary.csv"
SENS = "results/raw/EXP-004/sensitivity/sensitivity.json"
X6 = "results/exploratory/M4-REANALYSIS/x6_narrow_s1_reading.csv"
X7 = "results/exploratory/M4-REANALYSIS/x7_exp003_failure_exposure.csv"
REGISTRY = "research/experiment_registry.csv"
CLAIMS = "research/claims_register.csv"
MANIFEST = "research/publication/artifact_manifest.json"
LIMITATIONS = "research/limitations.md"

QUESTION = (
    "How do loading strategies (blank, skeleton, optimistic update, prefetch) affect measurable "
    "interface responsiveness under controlled, injected delays?"
)
STATUS_LABEL = (
    "Measured benchmark results, one mock page in one browser on one machine. EXP-002 to EXP-004 are "
    "confirmatory under protocol v1.0, frozen by the owner on 2026-11-24; EXP-001 is exploratory. "
    "Objective timing only: no claim about perceived speed. The manuscript is a preprint draft, not "
    "peer-reviewed; the owner's full-text review is pending (M6). DEC-011 is a pending owner decision "
    "and is shown both ways."
)

# Verdict texts: each piece is printed verbatim in manuscript Table 4 (checked by the test).
VERDICTS: dict[str, list[str]] = {
    "EXP-001": ["Instrumentation validated (exploratory)"],
    "EXP-002": [
        "No contradiction; H0 rejected at all 4 delays",
        "Equivalence shown at 3 of 4 delays; not shown at 50 ms",
    ],
    "EXP-003": [
        "H0 rejected in all 9 success strata",
        "No contradiction",
        "H0 not rejected in all 6; no equivalence claim",
    ],
    "EXP-004": [
        "Literal contradiction criterion met for 4 contrasts; main interpretation qualified at 50 ms (see Section 6)",
    ],
}

# Notes: each is a verbatim sentence of research/paper/manuscript.md (checked by the test).
NOTES: dict[str, list[str]] = {
    "EXP-001": [
        "Both runs had 70 of 70 sessions and 350 interactions.",
        "The second run had one hover-lead exclusion.",
        "The pre-freeze run motivated amendments A1 to A3 and A6; its values are not evidence.",
        "The protocol said EXP-001 would choose the alternative paint method for S1; no choice was recorded (DEC-012).",
    ],
    "EXP-002": [
        "EXP-002 (`EXP-002-20261125T070315Z`) completed 240 of 240 sessions in 3,887.4 s; 2,387 of 2,400 trials were analysed after 13 hover-lead exclusions (at most 2 of 200 in any cell and arm), and no cell failed.",
        "Prefetching reduced TTUC at every delay.",
        "The skeleton reached usable content 16.7 ms earlier than BLANK under the main paint method, H0 was rejected, and equivalence was not shown because the lower 90% bound, -17.05 ms, lies just beyond the margin.",
        "The two test readings disagree at L = 300 ms: the unadjusted interval [-1.1, -0.4] ms excludes 0, the Holm-adjusted Wilcoxon test does not reject.",
    ],
    "EXP-003": [
        "EXP-003 (`EXP-003-20261125T080838Z`) completed 360 of 360 sessions in 6,318.7 s, with 3,600 of 3,600 trials analysed, no exclusion and rollback correctness 1.0; the stop rule was not triggered.",
        "On failure, no stratum rejected H0, with estimates from -1.6 to 2.7 ms; no equivalence test was registered for these strata, so they are not equivalence claims.",
        "In failure trials (83 per delay and arm over both p levels), OPTIMISTIC displayed a false state for a median of 83.4, 283.9 and 999.1 ms at L = 100, 300 and 1000 ms, and BLANK displayed none.",
    ],
    "EXP-004": [
        "EXP-004 ran S2 (CPU 4x, 140 sessions), S3 (h = 0 and 600 ms, 80 sessions, 4 hover-lead exclusions) and S4 (headed, 140 sessions) in full, 3,596 of 3,600 trials analysed, with no failed cell; S1 recomputed every EXP-002 and EXP-003 contrast with the alternative paint methods.",
        "We therefore do not report a skeleton benefit at 50 ms.",
        "The frozen verdicts stand as reported.",
        "TTFF sensitivity could not be computed, because the frozen code records alternative paint times only for the usable-content frame.",
    ],
}

STATUS = {
    "EXP-001": "exploratory (not frozen), two runs",
    "EXP-002": "confirmatory, complete",
    "EXP-003": "confirmatory, complete",
    "EXP-004": "confirmatory, complete",
}

# Pending owner decisions: every reading is a verbatim manuscript sentence or phrase.
PENDING = [
    {
        "id": "DEC-011",
        "title": "Which test decides H0, and which alternative paint methods form sensitivity level S1",
        "state": "pending owner decision",
        "readings": [
            {
                "label": "Test reading A (DEC-011 item 1)",
                "text": "H0 is rejected when the Holm-adjusted Wilcoxon p is below 0.05",
            },
            {
                "label": "Test reading B (shown beside it)",
                "text": "the unadjusted 95% interval excludes 0",
            },
            {
                "label": "Where the test readings differ",
                "text": "Tabulating both readings over the 23 primary contrasts confirms that they disagree only for EXP-002 SKELETON at L = 300 ms",
            },
            {
                "label": "S1 reading of DEC-011 (rAF1 and Element Timing)",
                "text": "Under the frozen rule, 19 of 23 primary contrasts were robust, including every PREFETCH and every OPTIMISTIC success contrast and the SKELETON equivalence at L of 100 ms and more.",
            },
            {
                "label": "Narrow S1 reading (Element Timing only)",
                "text": "The count becomes 11 robust, 1 method-dependent (the 50 ms skeleton), 2 condition-dependent (write L = 300 and 1000 ms, p = 0.3, failure) and 9 not assessed.",
            },
        ],
    }
]

PLACEHOLDERS = [
    "Repository URL: placeholder, not yet published (the owner's decision).",
    "Demo URL: placeholder, the page is not hosted anywhere.",
    "Funding statement: placeholder for the owner.",
    "Competing-interest statement: placeholder for the owner.",
    "Author line and affiliation: placeholder for the owner (the freeze record holds a name, no affiliation, for confirmation).",
    "Manuscript title: proposed in M4, awaiting the owner's approval.",
]

ASSUMPTIONS = [
    ("Delay model", "d = L (1 + j), j uniform in [-0.1, 0.1], from a seeded stream shared by all arms (common random numbers)", "research/protocol.md; experiments/EXP-002.json (jitter 0.1)"),
    ("Interactions per session", "K = 10 scripted interactions of one path, fresh browser context per session", "research/protocol.md section 5"),
    ("Read latencies", "L in {50, 100, 300, 1000} ms", "experiments/EXP-002.json"),
    ("Write latencies and failure probabilities", "L in {100, 300, 1000} ms, p in {0, 0.1, 0.3}", "experiments/EXP-003.json"),
    ("Hover lead (PREFETCH)", "h = 150 ms in EXP-002; h = 0 and 600 ms in EXP-004 S3", "experiments/EXP-002.json; research/experiments/EXP-004/protocol.md"),
    ("Equivalence margin (SKELETON)", "17 ms, justified as one 60 Hz frame; the measured headless frame interval was larger (limitation 15)", "research/protocol.md section 4"),
    ("Seeds", "1 to 20 (EXP-002, EXP-003), 1 to 10 (EXP-004), 1001 to 1005 (EXP-001, exploratory); the seed is the independent unit", "research/experiment_registry.csv"),
    ("Reference model", "Zero-overhead lower bounds: BLANK and SKELETON TTUC >= d; PREFETCH >= max(0, d - h); OPTIMISTIC >= 0 on success and >= d on failure", "src/scroll/reference.py; manuscript Section 3"),
    ("Environment", "Google Chrome 158.0.8127.38 via Playwright 1.65.0, headless at CPU 1x except EXP-004 S2 and S4; Apple M1 Pro, macOS 15.3.1", "run manifests under results/raw/"),
]


class ExportError(RuntimeError):
    pass


def _read(rel: str) -> bytes:
    p = ROOT / rel
    if not p.exists():
        raise ExportError(f"missing input {rel}")
    return p.read_bytes()


def _json(rel: str):
    return json.loads(_read(rel).decode("utf-8"))


def _csv(rel: str) -> list[dict[str, str]]:
    return list(csv.DictReader(_read(rel).decode("utf-8").splitlines()))


def f1(x: float) -> str:
    s = f"{x:.1f}"
    return "0.0" if s == "-0.0" else s


def interval(lo: float, hi: float) -> str:
    return f"[{f1(lo)}, {f1(hi)}]"


def tost_bound(x: float) -> str:
    # The manuscript keeps two decimals for a bound that lies within 0.1 ms of the 17 ms margin
    # (-17.05 would round to -17.1 and hide how close it is); one decimal otherwise.
    return f"{x:.2f}" if abs(abs(x) - 17.0) < 0.1 else f1(x)


def holm(p: float) -> str:
    if p >= 0.9999995:
        return "1.0"
    return f"{p:.2g}"


def _claims() -> list[dict[str, str]]:
    return _csv(CLAIMS)


def claim_ids_for(exp: str, claims: list[dict[str, str]]) -> list[str]:
    pat = re.compile(rf"\b{exp}\b")
    # A claim belongs to every experiment its result id names, ignoring parenthesised provenance
    # notes such as "(S1 from EXP-002-...)".
    return [r["claim_id"] for r in claims if pat.search(re.sub(r"\([^)]*\)", "", r["result_id"]))]


def claim_for(result_suffix: str, claims: list[dict[str, str]]) -> str:
    hit = [r["claim_id"] for r in claims if r["result_id"].endswith(result_suffix)]
    if len(hit) != 1:
        raise ExportError(f"expected one claim for {result_suffix}, found {hit}")
    return hit[0]


def _registry() -> dict[str, dict[str, str]]:
    return {r["experiment_id"]: r for r in _csv(REGISTRY)}


def exp002(claims) -> list[dict]:
    d = _json(EXP002)
    if d["family_size"] != 8 or not d["family_size_matches"]:
        raise ExportError("EXP-002 family size is not the frozen 8")
    out = []
    for c in d["contrasts"]:
        L = int(float(c["cell"].split("L=")[1].split()[0]))
        arm = c["arm"]
        e = {
            "label": f"L = {L} ms: {arm} minus BLANK",
            "estimate": c["median_diff_ms"],
            "ci_low": c["ci95_low_ms"],
            "ci_high": c["ci95_high_ms"],
            "ci_level": 0.95,
            "unit": "ms",
            "display": f1(c["median_diff_ms"]),
            "interval_display": interval(c["ci95_low_ms"], c["ci95_high_ms"]),
            "group": "read",
            "seeds": c["pairs"],
            "holm_p_display": holm(c["holm_p"]),
            "reading_a": "reject" if c["reject_h0"] else "not rejected",
            "reading_b": "excludes 0" if c["ci95_excludes_0"] else "includes 0",
            "tost_display": None,
            "claim_id": claim_for(f"| EXP-002|{c['cell']}|{c['contrast']}|{c['stratum']}", claims),
        }
        if arm == "SKELETON":
            eq = "equivalent" if c["equivalent_17ms"] else "not shown"
            e["tost_display"] = f"[{tost_bound(c['ci90_low_ms'])}, {tost_bound(c['ci90_high_ms'])}], {eq}"
        out.append(e)
    order = {50: 0, 100: 1, 300: 2, 1000: 3}
    return sorted(out, key=lambda e: (order[int(e["label"].split()[2])], e["label"]))


def exp003(claims) -> list[dict]:
    d = _json(EXP003)
    if d["family_size"] != 15 or not d["family_size_matches"]:
        raise ExportError("EXP-003 family size is not the frozen 15")
    out = []
    for c in d["contrasts"]:
        parts = dict(kv.split("=") for kv in c["cell"].split()[1:])
        L, p = int(parts["L"]), parts["p"]
        out.append({
            "label": f"L = {L} ms, p = {p}, {c['stratum']}: OPTIMISTIC minus BLANK",
            "estimate": c["median_diff_ms"],
            "ci_low": c["ci95_low_ms"],
            "ci_high": c["ci95_high_ms"],
            "ci_level": 0.95,
            "unit": "ms",
            "display": f1(c["median_diff_ms"]),
            "interval_display": interval(c["ci95_low_ms"], c["ci95_high_ms"]),
            "group": c["stratum"],
            "seeds": c["pairs"],
            "holm_p_display": holm(c["holm_p"]),
            "reading_a": "reject" if c["reject_h0"] else "not rejected",
            "reading_b": "excludes 0" if c["ci95_excludes_0"] else "includes 0",
            "tost_display": None,
            "claim_id": claim_for(f"| EXP-003|{c['cell']}|{c['contrast']}|{c['stratum']}", claims),
        })
    return out


LEVEL_NAMES = {
    "main": "main method",
    "S1-raf1": "S1 rAF1",
    "S1-element": "S1 Element Timing",
    "S2-cpu4x": "S2 CPU 4x",
    "S4-headed": "S4 headed",
}


def _contrast_name(x: dict) -> str:
    if x["path"] == "read":
        return f"read L = {int(x['L'])} ms, {x['arm']}"
    p = x["p"]
    p_txt = "0" if p == 0 else f"{p:g}"
    return f"write L = {int(x['L'])} ms, p = {p_txt}, {x['stratum']}"


def exp004() -> tuple[list[dict], list[dict]]:
    s = _json(SENS)
    if len(s) != 23:
        raise ExportError("EXP-004 sensitivity must cover the 23 primary contrasts")
    narrow = _csv(X6)
    if len(narrow) != 23:
        raise ExportError("X6 must cover the 23 primary contrasts")
    estimates, robustness = [], []
    for x, n in zip(s, narrow):
        if (n["path"], float(n["L"]), n["arm"], n["stratum"]) != (x["path"], x["L"], x["arm"], x["stratum"]):
            raise ExportError("X6 and the sensitivity output are not in the same order")
        if n["frozen_verdict_dec011"] != x["verdict"]:
            raise ExportError("X6 frozen verdict differs from the sensitivity output")
        robustness.append({
            "contrast": _contrast_name(x),
            "verdict_dec011": x["verdict"],
            "verdict_narrow": n["verdict_element_only_s1"],
        })
        if x["verdict"] == "robust":
            continue
        for key, lv in x["levels"].items():
            if key not in LEVEL_NAMES:
                raise ExportError(f"unknown sensitivity level {key}")
            eq = lv.get("equivalent_17ms")
            estimates.append({
                "label": f"{_contrast_name(x)}: {LEVEL_NAMES[key]}"
                + ("" if eq is None else (", equivalent within 17 ms" if eq else ", equivalence not shown")),
                "estimate": lv["median_diff_ms"],
                "ci_low": lv["ci95_low_ms"],
                "ci_high": lv["ci95_high_ms"],
                "ci_level": 0.95,
                "unit": "ms",
                "display": f1(lv["median_diff_ms"]),
                "interval_display": interval(lv["ci95_low_ms"], lv["ci95_high_ms"]),
                "group": x["verdict"],
                "seeds": lv["pairs"],
                "holm_p_display": None,
                "reading_a": None,
                "reading_b": None,
                "tost_display": None,
                "claim_id": None,
            })
    return estimates, robustness


def _cells(rel: str) -> dict[tuple[str, str], dict[str, str]]:
    return {(r["cell"], r["arm"]): r for r in _csv(rel)}


def traces() -> dict:
    c2 = _cells(CELLS002)
    read = []
    for L in (50, 100, 300, 1000):
        for arm in ("BLANK", "SKELETON", "PREFETCH"):
            r = c2[(f"read L={L} h=150", arm)]
            read.append({
                "L": L, "arm": arm,
                "trials": int(r["trials_ok"]) - int(r["trials_excluded"]),
                "ttff_median_ms": float(r["ttff_median_ms"]),
                "ttuc_median_ms": float(r["ttuc_median_ms"]),
                "ttuc_q1_ms": float(r["ttuc_q1_ms"]),
                "ttuc_q3_ms": float(r["ttuc_q3_ms"]),
                "false_state_median_ms": None,
                "display": {
                    "ttff": f1(float(r["ttff_median_ms"])),
                    "ttuc": f1(float(r["ttuc_median_ms"])),
                    "iqr": interval(float(r["ttuc_q1_ms"]), float(r["ttuc_q3_ms"])),
                    "false_state": None,
                },
            })
    c3 = _cells(CELLS003)
    success = []
    for L in (100, 300, 1000):
        for arm in ("BLANK", "OPTIMISTIC"):
            r = c3[(f"write L={L} p=0", arm)]
            success.append({
                "L": L, "arm": arm,
                "trials": int(r["trials_ok"]) - int(r["trials_excluded"]),
                "ttff_median_ms": float(r["ttff_median_ms"]),
                "ttuc_median_ms": float(r["ttuc_median_ms"]),
                "ttuc_q1_ms": float(r["ttuc_q1_ms"]),
                "ttuc_q3_ms": float(r["ttuc_q3_ms"]),
                "false_state_median_ms": None,
                "display": {
                    "ttff": f1(float(r["ttff_median_ms"])),
                    "ttuc": f1(float(r["ttuc_median_ms"])),
                    "iqr": interval(float(r["ttuc_q1_ms"]), float(r["ttuc_q3_ms"])),
                    "false_state": None,
                },
            })
    failure = []
    for r in _csv(X7):
        failure.append({
            "L": int(float(r["L"])), "arm": r["arm"],
            "trials": int(r["failure_trials"]),
            "ttff_median_ms": None,
            "ttuc_median_ms": float(r["median_ttuc_ms"]),
            "ttuc_q1_ms": None,
            "ttuc_q3_ms": None,
            "false_state_median_ms": float(r["median_false_state_ms"]),
            "display": {
                "ttff": None,
                "ttuc": r["median_ttuc_ms"],
                "iqr": None,
                "false_state": r["median_false_state_ms"],
            },
        })
    return {
        "note": (
            "Cell medians of trials, copied from the committed cell summaries (read path and write path "
            "at p = 0) and from the committed exploratory table X7 (write path, failed saves, both p levels). "
            "The bar shows the interquartile range of trials, a spread, not a confidence interval. "
            "Documented exception to the manuscript check: the manuscript prints only the ranges of these medians."
        ),
        "sources": [CELLS002, CELLS003, X7],
        "series": {"read": read, "write_success": success, "write_failure": failure},
    }


def _limitations() -> list[str]:
    text = _read(LIMITATIONS).decode("utf-8")
    items = re.findall(r"^\d+\.\s+(.*)$", text, flags=re.M)
    if len(items) < 10:
        raise ExportError("limitations list not found")
    return [re.sub(r"[*`]", "", i).strip() for i in items]


def _sources() -> list[dict[str, str]]:
    paths = [EXP002, EXP003, SENS, CELLS002, CELLS003, X6, X7, REGISTRY, CLAIMS, MANIFEST, LIMITATIONS]
    return [{"path": p, "sha256": hashlib.sha256(_read(p)).hexdigest()} for p in paths]


def _code_revision() -> str:
    m = _json(MANIFEST)
    revs = {a.get("code_revision") for a in m["artifacts"] if a.get("label") == "confirmatory" and a.get("code_revision")}
    if len(revs) != 1:
        raise ExportError(f"confirmatory artifacts do not share one code revision: {sorted(revs)}")
    return revs.pop()


def build() -> dict:
    claims = _claims()
    reg = _registry()
    e4, robustness = exp004()
    titles = {k: reg[k]["title"] for k in ("EXP-001", "EXP-002", "EXP-003", "EXP-004")}
    estimates = {"EXP-001": [], "EXP-002": exp002(claims), "EXP-003": exp003(claims), "EXP-004": e4}
    experiments = []
    for k in ("EXP-001", "EXP-002", "EXP-003", "EXP-004"):
        experiments.append({
            "id": k,
            "title": titles[k],
            "status": STATUS[k],
            "verdict": ". ".join(VERDICTS[k]) + ".",
            "estimates": estimates[k],
            "claim_ids": claim_ids_for(k, claims),
            "report_path": reg[k]["report_path"],
            "notes": NOTES[k],
        })
    return {
        "schema": "lab-demo-results",
        "schema_version": "1.0.0",
        "project": "SCROLL",
        "question": QUESTION,
        "status_label": STATUS_LABEL,
        "code_revision": _code_revision(),
        "sources": _sources(),
        "experiments": experiments,
        "assumptions": [{"name": a, "value": v, "source": s} for a, v, s in ASSUMPTIONS],
        "limitations": _limitations(),
        "traces": traces(),
        "robustness": robustness,
        "pending_decisions": PENDING,
        "placeholders": PLACEHOLDERS,
    }


def render(data: dict) -> str:
    return json.dumps(data, indent=1, ensure_ascii=False, sort_keys=False) + "\n"


def main(argv: list[str]) -> int:
    text = render(build())
    if "--check" in argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("EXPORT-CHECK FAIL: demo/public/data/results.json is stale")
            return 1
        print("EXPORT-CHECK PASS")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
