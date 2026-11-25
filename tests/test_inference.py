# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Confirmatory inference wiring (DEC-011): Holm over Wilcoxon, TOST, failed-cell rule, stop rule,
mixed-trend check and the EXP-004 sensitivity table, on the deterministic fake harness."""
import copy

import pytest

from scroll import inference as I
from scroll.runner import run_experiment
from scroll.schema import read_result
from test_pipeline_integration import FakeHarness

SEEDS = [1001, 1002, 1003, 1004, 1005, 1006]


@pytest.fixture
def fake(tmp_path, smoke_cfg):
    def make(name, read_L=(300,), write_p=(0, 0.5), h=None):
        cfg = copy.deepcopy(smoke_cfg)
        cfg["seeds"] = SEEDS
        cfg["interactions_per_session"] = 4
        cfg["conditions"][0]["latency_ms"] = list(read_L)
        if h is not None:
            cfg["conditions"][0]["hover_lead_ms"] = list(h)
        cfg["conditions"][1]["failure_prob"] = list(write_p)
        out = run_experiment(cfg, out_dir=tmp_path / name, harness_factory=FakeHarness, log=lambda s: None)
        return read_result(out / "results.json")
    return make


def test_parse_cell():
    assert I.parse_cell("read L=300 h=150") == {"path": "read", "L": 300.0, "h": 150.0, "p": None}
    assert I.parse_cell("write L=100 p=0.1") == {"path": "write", "L": 100.0, "h": None, "p": 0.1}
    with pytest.raises(ValueError):
        I.parse_cell("read L=300")


def test_primary_inference_known_effects(fake):
    inf = I.primary_inference(fake("a"), n_boot=500)
    c = {(r["cell"], r["contrast"], r["stratum"]): r for r in inf["contrasts"]}
    sk = c[("read L=300 h=150", "SKELETON - BLANK", "all")]
    assert sk["wilcoxon_p"] == 1.0 and sk["reject_h0"] is False and sk["equivalent_17ms"] is True
    pf = c[("read L=300 h=150", "PREFETCH - BLANK", "all")]
    assert pf["median_diff_ms"] == -150 and pf["prefetch_expected_ms"] == -150 and pf["prefetch_contradiction"] is False
    assert pf["wilcoxon_p"] == pytest.approx(0.03125)  # six identical negative differences, exact two-sided test
    # Holm: the family holds every primary contrast; adjusted p >= raw p.
    assert all(r["holm_p"] >= r["wilcoxon_p"] for r in inf["contrasts"])
    assert inf["stop_rule"]["triggered"] is False and inf["stop_rule"]["rollback_correct_share"] == 1.0
    assert not any(r["failed_cell"] for r in inf["contrasts"])
    # no secondary (mixed) row enters the family
    assert all(r["stratum"] != "mixed" for r in inf["contrasts"])


def test_failed_cell_gets_no_verdict_and_p_one(fake):
    res = fake("b")
    s = next(x for x in res["sessions"] if x["spec"]["path"] == "read" and x["spec"]["arm"] == "SKELETON")
    s["trials"][0]["metrics"]["status"] = "excluded"  # 1 of 24 trials of the group = 4.2%: not failed
    assert not I.failed_groups(res)
    s["trials"][1]["metrics"]["status"] = "excluded"  # 2 of 24 = 8.3%: failed
    assert list(I.failed_groups(res)) == [("read L=300 h=150", "SKELETON")]
    inf = I.primary_inference(res, n_boot=500)
    sk = next(r for r in inf["contrasts"] if r["arm"] == "SKELETON")
    assert sk["failed_cell"] and sk["reject_h0"] is None and sk["holm_p"] == 1.0 and "failed cell" in sk["verdict"]


def test_stop_rule_triggers_on_rollback_defect(fake):
    res = fake("c")
    s = next(x for x in res["sessions"] if x["spec"]["path"] == "write")
    s["trials"][0]["metrics"]["final_correct"] = False
    assert I.stop_rule_checks(res)["triggered"] is True


def test_mixed_trend(fake):
    rows = I.mixed_trend(fake("d", write_p=(0, 0.5)), n_boot=500)
    assert len(rows) == 1 and rows[0]["p_levels"] == [0.0, 0.5]
    assert rows[0]["magnitude_strictly_decreasing"] is True and rows[0]["contradiction"] is False


def test_sensitivity_same_data_is_robust_and_s3_levels(fake):
    main = fake("m", read_L=(300, 1000), write_p=(0, 0.3))
    s3 = fake("s3", read_L=(300, 1000), write_p=(0,), h=(0, 600))
    rows = I.sensitivity({"EXP-002": main}, main, s3, main, n_boot=500)
    by = {(r["path"], r["L"], r["p"], r["arm"], r["stratum"]): r for r in rows}
    sk = by[("read", 300.0, None, "SKELETON", "all")]
    assert sk["rule_basis"] == "equivalence verdict" and sk["verdict"] == "robust"
    assert {"S1-raf1", "S2-cpu4x", "S4-headed"} <= set(sk["levels_compared"])
    pf = by[("read", 1000.0, None, "PREFETCH", "all")]
    assert {"S3-h0", "S3-h600"} <= set(pf["levels"])
    # in the fake, h = 0 gives a zero difference: the sign changes against the main -150 ms
    assert pf["levels"]["S3-h0"]["sign"] == 0 and "condition-dependent" in pf["verdict"]
    assert pf["levels"]["S3-h600"]["median_diff_ms"] < 0
    long = I.sensitivity_long(rows)
    assert all("level" in r for r in long)


def test_cli_primary_and_sensitivity(fake, tmp_path):
    fake("cli")
    run = tmp_path / "cli"
    assert I.main(["primary", "--run", str(run)]) == 0
    assert (run / "report" / "inference.json").is_file() and (run / "report" / "inference.csv").is_file()
    out = tmp_path / "sens"
    assert I.main(["sensitivity", "--exp002", str(run), "--exp003", str(run), "--s2", str(run), "--out", str(out)]) == 0
    for f in ("sensitivity.json", "sensitivity_long.csv", "sensitivity_verdicts.csv", "figures/fig-sensitivity.svg"):
        assert (out / f).is_file(), f
