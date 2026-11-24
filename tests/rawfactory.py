# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Builders for hand-written raw trial records (the shape produced by src/web/app.js)."""
from __future__ import annotations


def frame(kind, paint, state, raf1=None):
    return {"kind": kind, "t_commit": paint - 20, "t_raf1": paint - 10, "t_raf1_ts": paint - 15 if raf1 is None else raf1,
            "t_raf2": paint, "t_raf2_ts": paint - 1, "state": state}


def read_raw(arm="BLANK", k=0, t_in=1000.0, d=100, t_req=None, frames=None, shifts=(), events=(), element=(), hover=None,
             final=None, prefetch=None):
    t_req = t_in + 0.5 if t_req is None else t_req
    if frames is None:
        frames = [frame("content", t_in + 120, {"content": True, "item": k, "aria_busy": "false"}, raf1=t_in + 105)]
    return {"k": k, "path": "read", "arm": arm, "input_type": "pointer", "t_prepare": t_in - 300, "t_hover": hover,
            "t_in": t_in, "t_handler": t_in + 0.4, "request": {"stream": "read", "index": k, "d_ms": d, "ok": True, "t_start": t_req, "t_end": t_req + d},
            "prefetch": prefetch, "frames": frames, "event_entries": list(events), "layout_shifts": list(shifts),
            "element_entries": list(element),
            "final_display": final or {"content_item": k, "skeleton_present": False, "aria_busy": "false"},
            "server_state_before": None, "server_state_after": None, "t_finalize": t_in + 1200}


def write_raw(arm="BLANK", ok=True, t_in=0.0, d=300, frames=None, final=None, before=False):
    after = (not before) if ok else before
    return {"k": 0, "path": "write", "arm": arm, "input_type": "pointer", "t_prepare": -300, "t_hover": None, "t_in": t_in,
            "t_handler": t_in + 0.2, "request": {"stream": "write", "index": 0, "d_ms": d, "ok": ok, "t_start": t_in + 0.3, "t_end": t_in + d},
            "prefetch": None, "frames": frames, "event_entries": [], "layout_shifts": [], "element_entries": [],
            "final_display": final or {"pressed": after, "error_text": "" if ok else "Could not save Item 1.", "focus_on_toggle": True},
            "server_state_before": before, "server_state_after": after, "t_finalize": t_in + 2000}
