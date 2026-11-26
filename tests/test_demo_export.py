# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""M5 consistency (master prompt 11.6): the demo shows exactly the numbers of the manuscript.

1. Re-running the export in memory reproduces the committed demo/public/data/results.json exactly.
2. Every display and interval_display string appears verbatim in research/paper/manuscript.md, the
   pair on one manuscript line (a table row). The same holds for the Holm p and TOST strings, the
   notes, the verdict pieces and the pending-decision readings.
3. Documented exception: the trace medians are copied from committed cell summaries and the X7
   table, which the manuscript gives only as ranges. They must match those source files exactly.
4. The sandbox parity fixture is reproduced by the Python engine.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = (ROOT / "research/paper/manuscript.md").read_text(encoding="utf-8")
LINES = MANUSCRIPT.splitlines()
COMMITTED = ROOT / "demo/public/data/results.json"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def export():
    return _load("export_demo_data")


@pytest.fixture(scope="module")
def data():
    return json.loads(COMMITTED.read_text(encoding="utf-8"))


def test_committed_export_is_reproduced(export):
    assert COMMITTED.read_text(encoding="utf-8") == export.render(export.build())


def test_schema_revision_and_no_timestamp(data):
    assert data["schema"] == "lab-demo-results" and data["schema_version"] == "1.0.0"
    assert data["code_revision"] == "b5a72c32202cb66a17341a5022ad29e9344506b6"
    text = COMMITTED.read_text(encoding="utf-8")
    assert "2026-11-25T" not in text and "generated" not in text


def test_source_hashes_match_files(data):
    assert len(data["sources"]) >= 10
    for s in data["sources"]:
        assert hashlib.sha256((ROOT / s["path"]).read_bytes()).hexdigest() == s["sha256"], s["path"]


def test_every_estimate_is_printed_in_the_manuscript(data):
    n = 0
    for e in data["experiments"]:
        for x in e["estimates"]:
            d, i = x["display"], x["interval_display"]
            row = [ln for ln in LINES if d in ln and i in ln]
            assert row, (e["id"], x["label"], d, i)
            for k in ("holm_p_display", "tost_display"):
                if x.get(k):
                    assert any(d in ln and i in ln and x[k] in ln for ln in row), (e["id"], x["label"], k, x[k])
            n += 1
    assert n == 8 + 15 + 13


def test_display_strings_match_the_numbers(data):
    for e in data["experiments"]:
        for x in e["estimates"]:
            assert float(x["display"]) == pytest.approx(x["estimate"], abs=0.05 + 1e-9)
            lo, hi = (float(v) for v in x["interval_display"].strip("[]").split(", "))
            assert lo == pytest.approx(x["ci_low"], abs=0.05 + 1e-9) and hi == pytest.approx(x["ci_high"], abs=0.05 + 1e-9)


def test_every_registered_experiment_is_exported(data):
    with open(ROOT / "research/experiment_registry.csv", encoding="utf-8") as f:
        registered = [r["experiment_id"] for r in csv.DictReader(f)]
    assert [e["id"] for e in data["experiments"]] == registered
    by = {e["id"]: e for e in data["experiments"]}
    assert by["EXP-001"]["status"].startswith("exploratory")
    for k in ("EXP-002", "EXP-003", "EXP-004"):
        assert by[k]["status"].startswith("confirmatory")
    # Null results carry the same fields as positive ones.
    failure = [x for x in by["EXP-003"]["estimates"] if x["group"] == "failure"]
    assert len(failure) == 6 and all(x["reading_a"] == "not rejected" for x in failure)


def test_texts_are_verbatim(export, data):
    for e in data["experiments"]:
        for n in e["notes"]:
            assert n in MANUSCRIPT, (e["id"], n)
        pieces = export.VERDICTS[e["id"]]
        assert e["verdict"] == ". ".join(pieces) + "."
        for p in pieces:
            assert p in MANUSCRIPT, (e["id"], p)
    for d in data["pending_decisions"]:
        assert d["state"] == "owner chose none; both readings shown"
        for r in d["readings"]:
            assert r["text"] in MANUSCRIPT, r


def test_trace_exception_matches_sources(data):
    t = data["traces"]
    cells = {}
    for rel in t["sources"][:2]:
        with open(ROOT / rel, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                cells[(r["cell"], r["arm"])] = r
    for p in t["series"]["read"]:
        r = cells[(f"read L={p['L']} h=150", p["arm"])]
        assert p["ttuc_median_ms"] == float(r["ttuc_median_ms"]) and p["ttff_median_ms"] == float(r["ttff_median_ms"])
        assert p["display"]["ttuc"] == f"{float(r['ttuc_median_ms']):.1f}"
    for p in t["series"]["write_success"]:
        r = cells[(f"write L={p['L']} p=0", p["arm"])]
        assert p["ttuc_median_ms"] == float(r["ttuc_median_ms"])
    with open(ROOT / t["sources"][2], encoding="utf-8") as f:
        x7 = {(int(float(r["L"])), r["arm"]): r for r in csv.DictReader(f)}
    for p in t["series"]["write_failure"]:
        r = x7[(p["L"], p["arm"])]
        assert p["display"]["false_state"] == r["median_false_state_ms"]
    # The three OPTIMISTIC false-state medians are also printed in the manuscript.
    for v in ("83.4", "283.9", "999.1"):
        assert v in MANUSCRIPT


def test_robustness_counts_match_the_manuscript(data):
    rob = data["robustness"]
    assert len(rob) == 23
    assert sum(r["verdict_dec011"] == "robust" for r in rob) == 19
    assert sum(r["verdict_narrow"] == "robust" for r in rob) == 11
    assert sum(r["verdict_narrow"] == "no sensitivity level" for r in rob) == 9


def test_owner_facts_are_filled(data):
    # Owner, 2026-11-26, decision sheet (B1 to B4, B6): the placeholders hold the owner's answers.
    text = " ".join(data["placeholders"])
    for k in ("Mohamed Bechir Kefi, independent researcher", "no funding was received",
              "no competing interests", "title: approved"):
        assert k in text
    assert "placeholder" not in text.lower()
    # The only addresses in the exported data are the repository and the demo.
    import re

    urls = set(re.findall(r"https?://[^\s\"]+", COMMITTED.read_text(encoding="utf-8")))
    assert urls == {"https://github.com/mohamedbechirkefi/scroll-perceived-performance", "https://scroll-perceived-performance.kefimohamedbechir.workers.dev"}


def test_sandbox_fixture_is_reproduced():
    fx = _load("export_sandbox_fixture")
    assert fx.OUT.read_text(encoding="utf-8") == fx.render(fx.build())


@pytest.mark.parametrize("rel", ["README.md", "articles/medium.md", "articles/linkedin.md", "demo/README.md"])
def test_decimal_numbers_in_public_texts_are_in_the_manuscript(rel):
    import re

    text = (ROOT / rel).read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)  # header comments cite master prompt sections
    for tok in re.findall(r"-?\d+\.\d+", text):
        assert tok in MANUSCRIPT, (rel, tok)
