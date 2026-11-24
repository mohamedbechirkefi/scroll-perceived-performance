# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Reference model: the ideal, zero-overhead timing of each arm.

Used as the simple reference for differential tests and for the instrumentation
checks of EXP-001. All times in ms, measured from the input event.
A real browser can only be slower than this model, never faster.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Expected:
    ttuc_lower_bound_ms: float
    ttff_lower_bound_ms: float
    final_pressed: bool | None
    error_shown: bool | None


def residual_wait_ms(delay_ms: float, request_start_before_input_ms: float) -> float:
    """Remaining wait after input for a request started `request_start_before_input_ms` before input."""
    if delay_ms < 0 or request_start_before_input_ms < 0:
        raise ValueError("delay and lead must be >= 0")
    return max(0.0, delay_ms - request_start_before_input_ms)


def expected(path: str, arm: str, delay_ms: float, ok: bool = True, lead_ms: float = 0.0, before: bool = False) -> Expected:
    """Ideal timings. `lead_ms` is how long before input the request started (PREFETCH only)."""
    if delay_ms < 0:
        raise ValueError("delay_ms must be >= 0")
    if path == "read":
        if not ok:
            raise ValueError("read requests never fail in this design")
        if arm == "BLANK":
            return Expected(delay_ms, delay_ms, None, None)
        if arm == "SKELETON":
            return Expected(delay_ms, 0.0, None, None)
        if arm == "PREFETCH":
            w = residual_wait_ms(delay_ms, lead_ms)
            return Expected(w, w, None, None)
        raise ValueError(f"arm {arm} undefined for read path")
    if path == "write":
        final = (not before) if ok else before
        if arm == "BLANK":
            return Expected(delay_ms, delay_ms, final, not ok)
        if arm == "OPTIMISTIC":
            return Expected(0.0 if ok else delay_ms, 0.0, final, not ok)
        raise ValueError(f"arm {arm} undefined for write path")
    raise ValueError(f"unknown path {path}")
