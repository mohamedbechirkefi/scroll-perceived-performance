# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Hand-computed golden examples, edge cases and invariants for the per-trial metrics."""
import pytest
from hypothesis import given, settings, strategies as st

from scroll.metrics import HOVER_LEAD_TOLERANCE_MS, METRIC_KEYS, compute_trial_metrics, final_frame_index, state_exposure
from rawfactory import frame, read_raw, write_raw

SETTLE = 1000


def test_blank_read_golden():
    raw = read_raw(
        shifts=[{"startTime": 990, "value": 0.3, "hadRecentInput": False},      # before input: excluded
                {"startTime": 1110, "value": 0.1, "hadRecentInput": True},
                {"startTime": 1700, "value": 0.05, "hadRecentInput": False},
                {"startTime": 2121, "value": 0.2, "hadRecentInput": False}],    # after t_final + settle = 2120: excluded
        events=[{"name": "pointerdown", "startTime": 990, "duration": 40, "interactionId": 7},
                {"name": "click", "startTime": 1000, "duration": 24, "interactionId": 7}],
        element=[{"identifier": "content-0", "renderTime": 1112}, {"identifier": "content-0", "renderTime": 1110}])
    m = compute_trial_metrics(raw, SETTLE)
    assert m["status"] == "ok" and m["defects"] == []
    assert m["ttuc_ms"] == 120 and m["ttff_ms"] == 120 and m["ttuc_raf1_ms"] == 105
    assert m["ttuc_element_ms"] == 112
    assert m["residual_wait_ms"] == 100 and m["ttuc_reference_ms"] == 100 and m["ttuc_excess_ms"] == 20
    assert m["layout_shift_all"] == pytest.approx(0.15) and m["layout_shift_cls"] == pytest.approx(0.05)
    assert m["layout_shift_count"] == 2
    assert m["event_duration_ms"] == 40 and m["event_below_threshold"] is False
    assert m["final_correct"] is True
    assert m["input_to_handler_ms"] == pytest.approx(0.4)
    assert set(m) == set(METRIC_KEYS)


def test_skeleton_ttff_before_ttuc():
    raw = read_raw(arm="SKELETON", frames=[frame("skeleton", 1018, {"content": False, "aria_busy": "true"}),
                                           frame("content", 1125, {"content": True, "item": 0, "aria_busy": "false"})])
    m = compute_trial_metrics(raw, SETTLE)
    assert m["ttff_ms"] == 18 and m["ttuc_ms"] == 125 and m["ttuc_excess_ms"] == 25


def test_prefetch_residual_wait_golden():
    # Request started 150 ms before input with d = 100: residual wait 0; content painted 30 ms after input.
    raw = read_raw(arm="PREFETCH", t_req=850, hover=845, prefetch={"hit": True, "t_start": 850},
                   frames=[frame("content", 1030, {"content": True, "item": 0, "aria_busy": "false"})])
    m = compute_trial_metrics(raw, SETTLE)
    assert m["residual_wait_ms"] == 0 and m["ttuc_ms"] == 30 and m["ttuc_excess_ms"] == 30
    assert m["hover_lead_actual_ms"] == 155 and m["prefetch_hit"] is True and m["defects"] == []
    # Partial lead: request 40 ms before input with d = 100 => residual 60 ms.
    raw2 = read_raw(arm="PREFETCH", t_req=960, prefetch={"hit": True, "t_start": 960},
                    frames=[frame("content", 1075, {"content": True, "item": 0, "aria_busy": "false"})])
    m2 = compute_trial_metrics(raw2, SETTLE)
    assert m2["residual_wait_ms"] == 60 and m2["ttuc_excess_ms"] == 15


def test_prefetch_miss_is_a_defect():
    raw = read_raw(arm="PREFETCH", prefetch={"hit": False, "t_start": None})
    assert "C4: prefetched response not used" in compute_trial_metrics(raw, SETTLE)["defects"]


def test_blank_below_delay_is_a_defect():
    raw = read_raw(frames=[frame("content", 1090, {"content": True, "item": 0, "aria_busy": "false"})])
    d = compute_trial_metrics(raw, SETTLE)["defects"]
    assert "C1: BLANK TTUC below injected delay" in d and "TTUC below the reference lower bound" in d


def test_wrong_final_display_is_a_defect():
    raw = read_raw(final={"content_item": 3, "skeleton_present": False, "aria_busy": "false"})
    m = compute_trial_metrics(raw, SETTLE)
    assert m["final_correct"] is False and any(x.startswith("C3") for x in m["defects"])


def test_optimistic_failure_golden():
    # Optimistic paint at 16 ms (pressed), rollback with error at 320 ms; d = 300; server never changed.
    raw = write_raw("OPTIMISTIC", ok=False, frames=[frame("optimistic", 16, {"pressed": True, "error": False}),
                                                   frame("rollback", 320, {"pressed": False, "error": True})])
    m = compute_trial_metrics(raw, SETTLE)
    assert m["ttuc_ms"] == 320 and m["ttff_ms"] == 16
    assert (m["wrong_state_ms"], m["stale_state_ms"], m["false_state_ms"]) == (304, 0, 304)
    assert m["ttuc_reference_ms"] == 300 and m["ttuc_excess_ms"] == 20
    assert m["final_correct"] is True and m["focus_on_toggle"] is True and m["defects"] == []


def test_optimistic_success_golden():
    raw = write_raw("OPTIMISTIC", ok=True, frames=[frame("optimistic", 16, {"pressed": True, "error": False})])
    m = compute_trial_metrics(raw, SETTLE)
    assert m["ttuc_ms"] == 16 and m["ttuc_reference_ms"] == 0 and m["ttuc_excess_ms"] == 16
    assert (m["wrong_state_ms"], m["stale_state_ms"], m["false_state_ms"]) == (16, 16, 0)


def test_blank_write_success_and_failure_golden():
    ms = compute_trial_metrics(write_raw("BLANK", ok=True, frames=[frame("confirmed", 330, {"pressed": True, "error": False})]), SETTLE)
    assert ms["ttuc_ms"] == 330 and ms["ttff_ms"] == 330 and ms["stale_state_ms"] == 330 and ms["false_state_ms"] == 0
    mf = compute_trial_metrics(write_raw("BLANK", ok=False, frames=[frame("error", 315, {"pressed": False, "error": True})]), SETTLE)
    assert mf["ttuc_ms"] == 315 and mf["wrong_state_ms"] == 0 and mf["ttuc_excess_ms"] == 15


def test_failed_rollback_detected():
    raw = write_raw("OPTIMISTIC", ok=False, frames=[frame("optimistic", 16, {"pressed": True, "error": False}),
                                                   frame("rollback", 320, {"pressed": False, "error": True})],
                    final={"pressed": True, "error_text": "", "focus_on_toggle": False})
    m = compute_trial_metrics(raw, SETTLE)
    assert m["final_correct"] is False and m["focus_on_toggle"] is False


def test_event_below_threshold():
    m = compute_trial_metrics(read_raw(events=[{"name": "click", "startTime": 1500, "duration": 40, "interactionId": 1}]), SETTLE)
    assert m["event_duration_ms"] is None and m["event_below_threshold"] is True


@pytest.mark.parametrize("raw,timed_out,reason", [
    (None, False, "timeout"),
    (read_raw(), True, "timeout"),
    ({**read_raw(), "t_in": None}, False, "no input"),
    ({**read_raw(), "frames": []}, False, "no frame"),
    ({**read_raw(), "request": None}, False, "instrumentation"),
    (read_raw(frames=[frame("content", 1120, {"content": True, "item": 5})]), False, "instrumentation"),
    ({**read_raw(), "t_in": float("nan")}, False, "instrumentation"),
    (write_raw("OPTIMISTIC", ok=False, frames=[frame("optimistic", 16, {"pressed": True, "error": False})]), False, "instrumentation"),
])
def test_exclusions(raw, timed_out, reason):
    m = compute_trial_metrics(raw, SETTLE, timed_out=timed_out)
    assert m["status"] == "excluded" and reason in m["exclusion_reason"]
    assert m["ttuc_ms"] is None and set(m) == set(METRIC_KEYS)


def test_final_frame_index_rejects_frames_after_content():
    raw = read_raw(frames=[frame("content", 1120, {"content": True, "item": 0}), frame("skeleton", 1130, {"content": False})])
    with pytest.raises(ValueError):
        final_frame_index(raw)


@settings(max_examples=300, deadline=None)
@given(arm=st.sampled_from(["BLANK", "OPTIMISTIC"]), ok=st.booleans(), before=st.booleans(),
       d=st.integers(0, 5000), f1=st.floats(1, 40), overhead=st.floats(0, 60))
def test_write_invariants(arm, ok, before, d, f1, overhead):
    after = (not before) if ok else before
    frames = []
    if arm == "OPTIMISTIC":
        frames.append(frame("optimistic", f1, {"pressed": not before, "error": False}))
        if not ok:
            frames.append(frame("rollback", max(f1, d) + overhead, {"pressed": before, "error": True}))
    else:
        frames.append(frame("confirmed" if ok else "error", d + overhead, {"pressed": after, "error": not ok}))
    m = compute_trial_metrics(write_raw(arm, ok=ok, d=d, frames=frames, before=before), SETTLE)
    assert m["status"] == "ok", m["exclusion_reason"]
    assert m["wrong_state_ms"] == pytest.approx(m["stale_state_ms"] + m["false_state_ms"])
    assert 0 <= m["wrong_state_ms"] <= m["ttuc_ms"] + 1e-9
    assert m["ttff_ms"] <= m["ttuc_ms"]
    assert m["ttuc_excess_ms"] >= 0 and m["final_correct"] is True
    if arm == "BLANK":
        assert m["false_state_ms"] == 0  # waiting for confirmation never shows a state the server did not hold


@settings(max_examples=200, deadline=None)
@given(vals=st.lists(st.tuples(st.floats(900, 3000), st.floats(0, 1), st.booleans()), max_size=8))
def test_layout_shift_invariants(vals):
    shifts = [{"startTime": t, "value": v, "hadRecentInput": r} for t, v, r in vals]
    m = compute_trial_metrics(read_raw(shifts=shifts), SETTLE)
    assert 0 <= m["layout_shift_cls"] <= m["layout_shift_all"] + 1e-12
    assert m["layout_shift_count"] <= len(shifts)


def test_state_exposure_requires_server_states():
    raw = write_raw("BLANK", frames=[frame("confirmed", 330, {"pressed": True, "error": False})])
    raw["server_state_after"] = None
    with pytest.raises(ValueError):
        state_exposure(raw)


# Amendment A3 (owner-approved 2026-11-24): hover-to-click lead control.
@pytest.mark.parametrize("hover,expected", [
    (850.0, "ok"),        # lead 150 ms, exactly h
    (825.0, "ok"),        # lead 175 ms, deviation 25 ms: at the tolerance, kept
    (824.0, "excluded"),  # lead 176 ms, deviation 26 ms
    (876.0, "excluded"),  # lead 124 ms, deviation 26 ms (too short)
    (875.0, "ok"),        # lead 125 ms, deviation 25 ms
])
def test_hover_lead_rule_boundaries(hover, expected):
    raw = read_raw(hover=hover)
    m = compute_trial_metrics(raw, SETTLE, hover_lead_ms=150)
    assert HOVER_LEAD_TOLERANCE_MS == 25.0
    assert m["status"] == expected
    if m["status"] == "excluded":
        assert m["exclusion_reason"].startswith("hover lead") and m["ttuc_ms"] is not None  # values kept for the record


def test_hover_lead_rule_missing_hover_and_scope():
    assert compute_trial_metrics(read_raw(hover=None), SETTLE, hover_lead_ms=150)["exclusion_reason"].startswith("hover lead: no hover")
    # No scheduled lead given: rule not applied (exploratory callers and synthetic tests).
    assert compute_trial_metrics(read_raw(hover=None), SETTLE)["status"] == "ok"
    # Write path: no arm reacts to the hover and the lead is not recorded; rule not applied.
    raw = write_raw(frames=[frame("confirmed", 320, {"pressed": True, "error": False})])
    assert compute_trial_metrics(raw, SETTLE, hover_lead_ms=150)["status"] == "ok"
    # Zero lead (EXP-004 S3, h = 0).
    assert compute_trial_metrics(read_raw(hover=990.0), SETTLE, hover_lead_ms=0)["status"] == "ok"
    assert compute_trial_metrics(read_raw(hover=970.0), SETTLE, hover_lead_ms=0)["status"] == "excluded"
