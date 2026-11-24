# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Per-trial metrics from raw page records (research/protocol.md, section 3).

Pure functions. Input: one raw trial record as produced by src/web/app.js.
All times in ms on the page's performance.now() clock; outputs in ms except
layout shift (unitless) and booleans.

Paint-time methods for a frame record:
- "double_raf" (primary): performance.now() inside the second requestAnimationFrame
  callback after the DOM commit (the frame carrying the change has been produced).
- "raf1": the timestamp argument of the first rAF callback (start of the frame
  that will carry the change); an earlier, optimistic estimate.
- "element": Element Timing renderTime of the content (read path only).
"""
from __future__ import annotations

import math
from typing import Any

from .reference import expected, residual_wait_ms

METRIC_KEYS = (
    "status", "exclusion_reason", "delay_ms", "request_ok", "residual_wait_ms", "ttuc_ms", "ttff_ms",
    "ttuc_raf1_ms", "ttuc_element_ms", "ttuc_reference_ms", "ttuc_excess_ms", "event_duration_ms", "event_below_threshold",
    "layout_shift_all", "layout_shift_cls", "layout_shift_count", "wrong_state_ms", "stale_state_ms",
    "false_state_ms", "final_correct", "focus_on_toggle", "hover_lead_actual_ms", "prefetch_hit",
    "input_to_handler_ms", "defects",
)
EVENT_MATCH_TOLERANCE_MS = 1.0


class MetricError(ValueError):
    """A raw record is structurally invalid (a harness or instrumentation defect)."""


def empty_metrics(reason: str) -> dict[str, Any]:
    m: dict[str, Any] = {k: None for k in METRIC_KEYS}
    m["status"] = "excluded"
    m["exclusion_reason"] = reason
    m["defects"] = []
    return m


def _num(x: Any, name: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise MetricError(f"{name} must be a finite number, got {x!r}")
    return float(x)


def paint_time(frame: dict[str, Any], method: str = "double_raf") -> float:
    if method == "double_raf":
        return _num(frame.get("t_raf2"), "frame.t_raf2")
    if method == "raf1":
        return _num(frame.get("t_raf1_ts"), "frame.t_raf1_ts")
    raise MetricError(f"unknown paint method {method!r}")


def final_frame_index(raw: dict[str, Any]) -> int:
    """Index of the first frame from which the displayed state equals the final state and stays so."""
    frames = raw["frames"]
    if not frames:
        raise MetricError("no frames recorded")
    if raw["path"] == "read":
        for i, f in enumerate(frames):
            st = f.get("state") or {}
            if st.get("content") is True and st.get("item") == raw["k"]:
                if i != len(frames) - 1:
                    raise MetricError("frames recorded after the content frame")
                return i
        raise MetricError("no content frame for the requested item")
    req = raw.get("request") or {}
    final_pressed = raw.get("server_state_after")
    if not isinstance(final_pressed, bool):
        raise MetricError("server_state_after missing on write path")
    final_error = not bool(req.get("ok"))
    idx = None
    for i in range(len(frames) - 1, -1, -1):
        st = frames[i].get("state") or {}
        if st.get("pressed") == final_pressed and bool(st.get("error")) == final_error:
            idx = i
        else:
            break
    if idx is None:
        raise MetricError("the last frame does not show the final state")
    return idx


def state_exposure(raw: dict[str, Any], method: str = "double_raf") -> tuple[float, float, float]:
    """Write path: (wrong, stale, false) state exposure in ms after input.

    wrong = time the displayed toggle differs from the final server state (protocol 3.2 item 4, literal).
    stale = part of `wrong` showing the pre-input server state (waiting for confirmation).
    false = part of `wrong` showing a state the server never held in this trial (optimistic then rolled back).
    Intervals end at the paint of the final frame.
    """
    t_in = _num(raw["t_in"], "t_in")
    before = raw.get("server_state_before")
    final = raw.get("server_state_after")
    if not isinstance(before, bool) or not isinstance(final, bool):
        raise MetricError("server states missing on write path")
    fi = final_frame_index(raw)
    frames = raw["frames"][: fi + 1]
    shown = before
    t_prev = t_in
    wrong = stale = false = 0.0
    for f in frames:
        t = max(paint_time(f, method), t_prev)
        dt = t - t_prev
        if shown != final:
            wrong += dt
            if shown == before:
                stale += dt
            else:
                false += dt
        shown = (f.get("state") or {}).get("pressed", shown)
        t_prev = t
    return wrong, stale, false


def _event_duration(raw: dict[str, Any], t_in: float) -> tuple[float | None, bool]:
    entries = raw.get("event_entries") or []
    clicks = [e for e in entries if e.get("name") == "click" and abs(_num(e.get("startTime"), "event.startTime") - t_in) <= EVENT_MATCH_TOLERANCE_MS]
    if not clicks:
        return None, True
    click = clicks[0]
    iid = click.get("interactionId") or 0
    if iid:
        same = [_num(e.get("duration"), "event.duration") for e in entries if (e.get("interactionId") or 0) == iid]
        return max(same), False
    return _num(click.get("duration"), "event.duration"), False


def compute_trial_metrics(raw: dict[str, Any] | None, settle_ms: float, timed_out: bool = False) -> dict[str, Any]:
    """Metrics for one trial. Harness failures give status 'excluded' with a reason."""
    if timed_out or raw is None:
        return empty_metrics("timeout: no final frame within the trial limit")
    if raw.get("t_in") is None:
        return empty_metrics("no input event recorded")
    if not raw.get("frames"):
        return empty_metrics("no frame recorded")
    try:
        return _compute(raw, settle_ms)
    except MetricError as exc:
        return empty_metrics(f"instrumentation: {exc}")


def _compute(raw: dict[str, Any], settle_ms: float) -> dict[str, Any]:
    m: dict[str, Any] = {k: None for k in METRIC_KEYS}
    m["status"] = "ok"
    m["defects"] = []
    path, arm = raw["path"], raw["arm"]
    t_in = _num(raw["t_in"], "t_in")
    req = raw.get("request")
    if not req:
        raise MetricError("no request recorded")
    d = _num(req["d_ms"], "request.d_ms")
    t_req = _num(req["t_start"], "request.t_start")
    m["delay_ms"] = d
    m["request_ok"] = bool(req["ok"])
    lead = max(0.0, t_in - t_req)
    m["residual_wait_ms"] = residual_wait_ms(d, lead)
    if raw.get("t_handler") is not None:
        m["input_to_handler_ms"] = _num(raw["t_handler"], "t_handler") - t_in

    frames = raw["frames"]
    fi = final_frame_index(raw)
    t_final = paint_time(frames[fi])
    m["ttuc_ms"] = t_final - t_in
    m["ttff_ms"] = paint_time(frames[0]) - t_in
    m["ttuc_raf1_ms"] = paint_time(frames[fi], "raf1") - t_in
    ref = expected(path, arm, d, ok=bool(req["ok"]), lead_ms=lead, before=bool(raw.get("server_state_before")))
    m["ttuc_reference_ms"] = ref.ttuc_lower_bound_ms
    m["ttuc_excess_ms"] = m["ttuc_ms"] - ref.ttuc_lower_bound_ms
    if path == "read":
        renders = [_num(e.get("renderTime"), "element.renderTime") for e in (raw.get("element_entries") or []) if e.get("renderTime")]
        m["ttuc_element_ms"] = (max(renders) - t_in) if renders else None

    dur, below = _event_duration(raw, t_in)
    m["event_duration_ms"], m["event_below_threshold"] = dur, below

    lo, hi = t_in, t_final + settle_ms
    shifts = [s for s in (raw.get("layout_shifts") or []) if lo <= _num(s.get("startTime"), "shift.startTime") <= hi]
    m["layout_shift_all"] = float(sum(_num(s.get("value"), "shift.value") for s in shifts))
    m["layout_shift_cls"] = float(sum(_num(s.get("value"), "shift.value") for s in shifts if not s.get("hadRecentInput")))
    m["layout_shift_count"] = len(shifts)

    fd = raw.get("final_display") or {}
    if path == "read":
        m["final_correct"] = fd.get("content_item") == raw["k"] and fd.get("skeleton_present") is False and fd.get("aria_busy") == "false"
        if raw.get("t_hover") is not None:
            m["hover_lead_actual_ms"] = t_in - _num(raw["t_hover"], "t_hover")
        if arm == "PREFETCH":
            m["prefetch_hit"] = bool((raw.get("prefetch") or {}).get("hit"))
    else:
        wrong, stale, false = state_exposure(raw)
        m["wrong_state_ms"], m["stale_state_ms"], m["false_state_ms"] = wrong, stale, false
        expect_error = not bool(req["ok"])
        m["final_correct"] = fd.get("pressed") == raw.get("server_state_after") and (bool(fd.get("error_text")) == expect_error)
        m["focus_on_toggle"] = fd.get("focus_on_toggle")
        if raw.get("t_hover") is not None:
            m["hover_lead_actual_ms"] = t_in - _num(raw["t_hover"], "t_hover")

    # Stop-rule and instrumentation checks (protocol section 7; EXP-001 C1, C3, C4).
    if path == "read" and arm == "BLANK" and m["ttuc_ms"] < d:
        m["defects"].append("C1: BLANK TTUC below injected delay")
    if m["ttuc_excess_ms"] < 0:
        m["defects"].append("TTUC below the reference lower bound")
    if m["final_correct"] is False:
        m["defects"].append("C3: final displayed state differs from server state")
    if arm == "PREFETCH" and m["prefetch_hit"] is False:
        m["defects"].append("C4: prefetched response not used")
    return m
