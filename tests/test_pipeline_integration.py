# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Integration from config to validated results and report, with a deterministic fake harness
built on the reference model (no browser). Checks the analysis recovers known effects."""
import json

import pytest

from scroll import schedule as S
from scroll.analysis import paired_contrasts, runtime_model
from scroll.report import build_report
from scroll.runner import run_experiment
from scroll.schema import SchemaError, read_result, write_result
from rawfactory import frame, read_raw, write_raw

OVERHEAD = 20.0  # fixed synthetic rendering overhead, ms


class FakeHarness:
    def __init__(self, browser_cfg):
        self.cfg = browser_cfg

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def info(self):
        return {"channel": "fake", "version": "0", "headless": True, "cpu_throttle": 1, "viewport": [1, 1]}

    def run_session(self, spec, cfg):
        from scroll.metrics import compute_trial_metrics
        trials = []
        for k in range(cfg["interactions_per_session"]):
            d = S.delay_ms(spec.seed, spec.path, k, spec.latency_ms, cfg["jitter"])
            ok = S.succeeds(spec.seed, "write", k, spec.failure_prob) if spec.path == "write" else True
            if spec.path == "read":
                lead = spec.hover_lead_ms if spec.arm == "PREFETCH" else 0
                paint = 1000 + max(0, d - lead) + OVERHEAD
                frames = [frame("content", paint, {"content": True, "item": k, "aria_busy": "false"})]
                if spec.arm == "SKELETON":
                    frames.insert(0, frame("skeleton", 1016, {"content": False, "aria_busy": "true"}))
                raw = read_raw(spec.arm, k=k, d=d, t_req=1000 - lead + 0.5 if lead else None, frames=frames,
                               prefetch={"hit": True, "t_start": 1000 - lead} if spec.arm == "PREFETCH" else None)
            else:
                if spec.arm == "OPTIMISTIC":
                    frames = [frame("optimistic", 16, {"pressed": True, "error": False})]
                    if not ok:
                        frames.append(frame("rollback", d + OVERHEAD, {"pressed": False, "error": True}))
                else:
                    frames = [frame("confirmed" if ok else "error", d + OVERHEAD, {"pressed": ok, "error": not ok})]
                raw = write_raw(spec.arm, ok=ok, d=d, frames=frames)
            trials.append({"k": k, "wall_s": 0.01 + d / 1000, "raw": raw, "metrics": compute_trial_metrics(raw, cfg["settle_ms"])})
        return {"spec": spec.to_dict(), "status": "ok", "failure": None, "wall_s": 0.3 + sum(t["wall_s"] for t in trials),
                "summary": {"prefetch": {}, "a11y": {"passed": True, "issues": []}}, "trials": trials}


@pytest.fixture
def run_dir(tmp_path, smoke_cfg):
    smoke_cfg["seeds"] = [1001, 1002, 1003]
    smoke_cfg["interactions_per_session"] = 4
    smoke_cfg["conditions"][0]["latency_ms"] = [300]
    return run_experiment(smoke_cfg, out_dir=tmp_path / "run", harness_factory=FakeHarness, log=lambda s: None)


def test_results_validate_and_manifest(run_dir):
    r = read_result(run_dir / "results.json")
    m = r["manifest"]
    assert r["label"] == "exploratory" and len(r["sessions"]) == 3 * 5
    assert len(m["config_hash"]) == 64 and m["seeds"] == [1001, 1002, 1003]
    assert m["runtime_s"] >= 0 and m["peak_rss_bytes"] > 0 and m["versions"]["numpy"]
    assert (run_dir / "trials.csv").read_text().count("\n") == 1 + 15 * 4
    assert json.loads((run_dir / "run_manifest.json").read_text())["run_id"] == m["run_id"]


def test_analysis_recovers_known_effects(run_dir):
    r = read_result(run_dir / "results.json")
    c = {(x["cell"], x["contrast"]): x for x in paired_contrasts(r, n_boot=500)}
    # SKELETON has the same content paint as BLANK in the fake: zero difference in every seed.
    sk = c[("read L=300 h=150", "SKELETON - BLANK")]
    assert sk["diffs_ms"] == [0, 0, 0] and sk["sigma_d_ms"] == 0
    # PREFETCH with h = 150 and d in [270, 330]: difference exactly -150 in every seed.
    pf = c[("read L=300 h=150", "PREFETCH - BLANK")]
    assert pf["diffs_ms"] == [-150, -150, -150]
    # Fake trial wall = 0.01 s + d; the model subtracts d + settle (0.2) + pre-input (0.05) + hover lead (0.15).
    assert runtime_model(r)["trial_overhead_s"] == pytest.approx(0.01 - 0.4, abs=1e-9)
    assert runtime_model(r)["session_overhead_s"] == pytest.approx(0.3, abs=1e-9)


def test_report_builds_from_results_only(run_dir):
    md = build_report(run_dir)
    text = md.read_text()
    assert "EXPLORATORY" in text and "PREFETCH - BLANK" in text
    for f in ("metrics.csv", "cell_summary.csv", "paired_contrasts.csv", "runtime_projection.csv", "analysis.json",
              "figures/fig-ttuc.svg", "figures/fig-paired.png", "figures/fig-excess.svg"):
        assert (run_dir / "report" / f).is_file(), f


def test_report_fails_closed_on_tampered_results(run_dir):
    p = run_dir / "results.json"
    data = json.loads(p.read_text())
    data["sessions"][0]["trials"][0]["metrics"]["ttuc_ms"] = "fast"
    p.write_text(json.dumps(data))
    with pytest.raises(SchemaError):
        build_report(run_dir)


def test_write_result_refuses_invalid(tmp_path):
    with pytest.raises(SchemaError):
        write_result({"schema_version": "1.0.0"}, tmp_path / "r.json")
    assert not (tmp_path / "r.json").exists()


def test_read_result_missing_and_malformed(tmp_path):
    with pytest.raises(SchemaError):
        read_result(tmp_path / "none.json")
    (tmp_path / "bad.json").write_text("{")
    with pytest.raises(SchemaError):
        read_result(tmp_path / "bad.json")
