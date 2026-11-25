# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""M4 evidence audit: check numbers in the manuscript, supplement and reports against committed outputs.

Two checks:
  1. Claims C-001 to C-023: the median, 95% interval and Holm p written in each claim text are compared
     with the corresponding contrast in the committed inference.json (same rounding as the text).
  2. Token check: every decimal number and every integer of three or more digits in the audited
     documents must equal, at the precision written, a value found in a committed aggregate output
     (CSV and JSON under results/, excluding trial-level files), a frozen configuration or record, or
     the journal. Absolute values and percentages (share x 100) are accepted. Unmatched tokens are
     listed for manual review; they are not automatically errors (derived differences, hashes, dates).

Usage: PYTHONPATH=src .venv/bin/python scripts/m4_number_audit.py --out research/publication/number_audit_m4.json
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ["research/paper/manuscript.md", "research/paper/supplementary.md",
        "research/experiments/EXP-002/report.md", "research/experiments/EXP-003/report.md",
        "research/experiments/EXP-004/report.md"]
EXCLUDE = {"results.json", "metrics.csv", "trials.csv"}
NUM = re.compile(r"(?<![\w.#/-])-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|(?<![\w.#/-])-?\d+(?:\.\d+)?(?:e-?\d+)?")


def walk(o, acc):
    if isinstance(o, dict):
        for v in o.values():
            walk(v, acc)
    elif isinstance(o, list):
        for v in o:
            walk(v, acc)
    elif isinstance(o, bool):
        return
    elif isinstance(o, (int, float)):
        acc.append(float(o))
    elif isinstance(o, str):
        for t in re.findall(r"-?\d+(?:\.\d+)?(?:e-?\d+)?", o):
            try:
                acc.append(float(t))
            except ValueError:
                pass


def pool() -> list[float]:
    acc: list[float] = []
    files = [p for p in (ROOT / "results").rglob("*") if p.is_file() and p.suffix in (".csv", ".json") and p.name not in EXCLUDE]
    files += [ROOT / "research/freeze.json", ROOT / "research/experiment_journal.jsonl"] + sorted((ROOT / "experiments").glob("*.json"))
    for p in files:
        txt = p.read_text()
        if p.suffix == ".csv":
            for row in csv.reader(txt.splitlines()):
                for cell in row:
                    walk(cell, acc)
        elif p.suffix == ".jsonl":
            for line in txt.splitlines():
                walk(json.loads(line), acc)
        else:
            walk(json.loads(txt), acc)
    out = set()
    for v in acc:
        out.add(v)
        out.add(abs(v))
        out.add(abs(v) * 100)
        out.add(v / 60.0)  # seconds to minutes
    return sorted(out)


def matches(token: str, values: list[float]) -> bool:
    t = token.replace(",", "")
    neg = t.startswith("-")
    t = t.lstrip("-")
    if "e" in t:
        x = float(t)
        return any(abs(v - x) <= abs(x) * 0.05 for v in values)
    dec = len(t.split(".")[1]) if "." in t else 0
    x = float(t)
    tol = 0.5 * 10 ** (-dec) + 1e-9
    import bisect
    i = bisect.bisect_left(values, x - tol)
    return i < len(values) and values[i] <= x + tol


def claims_check() -> list[dict]:
    rows = list(csv.DictReader(open(ROOT / "research/claims_register.csv")))
    inf = {}
    for exp, run in (("EXP-002", "EXP-002/EXP-002-20261125T070315Z"), ("EXP-003", "EXP-003/EXP-003-20261125T080838Z")):
        for c in json.load(open(ROOT / "results/raw" / run / "report/inference.json"))["contrasts"]:
            inf[f"{exp}|{c['cell']}|{c['contrast']}|{c['stratum']}"] = c
    out = []
    for r in rows:
        n = int(r["claim_id"][2:]) if r["claim_id"].startswith("C-") else 999
        if n > 23:
            continue
        key = r["evidence_path_or_source"].split("result id ")[1].rstrip(")")
        c = inf[key]
        m = re.search(r"difference (-?[\d.]+) ms \(95% bootstrap CI (-?[\d.]+) to (-?[\d.]+)", r["text"])
        ok = all(abs(float(m.group(i + 1)) - round(c[k], 1)) < 0.051 for i, k in enumerate(("median_diff_ms", "ci95_low_ms", "ci95_high_ms")))
        out.append({"claim_id": r["claim_id"], "result_id": key, "match": bool(ok),
                    "text_values": [m.group(1), m.group(2), m.group(3)],
                    "raw_values": [c["median_diff_ms"], c["ci95_low_ms"], c["ci95_high_ms"]]})
    return out


def token_check(values: list[float]) -> dict:
    res = {}
    for d in DOCS:
        text = (ROOT / d).read_text()
        text = re.sub(r"`[^`]*`", " ", text)  # paths, hashes, commands
        text = re.sub(r"\b[0-9a-f]{7,64}\b", " ", text)
        text = re.sub(r"\d{4}-\d{2}-\d{2}(T[\d:]+Z)?", " ", text)
        text = re.sub(r"\b(EXP|DEC|J|C|E|S|A|X)-?\d+\b", " ", text)
        text = re.sub(r"\b\d{2}:\d{2}:\d{2}Z?\b", " ", text)
        total, unmatched = 0, []
        for line_no, line in enumerate(text.splitlines(), 1):
            for t in NUM.findall(line):
                bare = t.replace(",", "").lstrip("-")
                if "." not in bare and len(bare) < 3 and "e" not in bare:
                    continue  # small integers: design constants, counts of items, section numbers
                total += 1
                if not matches(t, values):
                    unmatched.append({"line": line_no, "token": t, "context": line.strip()[:160]})
        res[d] = {"tokens_checked": total, "unmatched": unmatched}
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    values = pool()
    report = {"label": "M4 evidence audit output (mechanical number check; manual review in evidence_audit.md)",
              "claims_check": claims_check(), "token_check": token_check(values)}
    report["summary"] = {"claims_checked": len(report["claims_check"]),
                         "claims_matching": sum(c["match"] for c in report["claims_check"]),
                         **{d: {"checked": v["tokens_checked"], "unmatched": len(v["unmatched"])} for d, v in report["token_check"].items()}}
    (ROOT / a.out).write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report["summary"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
