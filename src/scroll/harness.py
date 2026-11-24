# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Browser harness: drives the mock page with scripted, identical input in every arm.

Uses the installed Google Chrome through Playwright's `channel="chrome"` (DEC-005 option b,
the only option available without a download). Every session runs in a fresh browser
context, offline (`context.set_offline(True)`); any non-file request is recorded as a defect.
"""
from __future__ import annotations

import time
import traceback
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from .config import SessionSpec
from .metrics import compute_trial_metrics, empty_metrics
from .manifest import repo_root

NEUTRAL_XY = (5, 5)
WEB_INDEX = repo_root() / "src" / "web" / "index.html"


def page_url(spec: SessionSpec, cfg: dict[str, Any], index: Path = WEB_INDEX) -> str:
    q = {
        "path": spec.path, "arm": spec.arm, "seed": spec.seed, "L": _fmt(spec.latency_ms),
        "p": _fmt(spec.failure_prob), "jitter": _fmt(cfg["jitter"]), "items": cfg["interactions_per_session"],
        "settle": _fmt(cfg["settle_ms"]), "reserve": "1" if cfg["reserve_space_blank"] else "0",
    }
    return index.as_uri() + "?" + urlencode(q)


def _fmt(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else repr(float(x))


def _center(page: Any, selector: str) -> tuple[float, float]:
    box = page.locator(selector).bounding_box()
    if box is None:
        raise RuntimeError(f"element not visible: {selector}")
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


class Harness:
    def __init__(self, browser_cfg: dict[str, Any]):
        self.browser_cfg = browser_cfg
        self._pw = None
        self.browser = None

    def __enter__(self) -> "Harness":
        from playwright.sync_api import sync_playwright

        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(channel=self.browser_cfg["channel"], headless=self.browser_cfg["headless"])
        return self

    def __exit__(self, *exc: Any) -> None:
        try:
            if self.browser is not None:
                self.browser.close()
        finally:
            if self._pw is not None:
                self._pw.stop()

    def info(self) -> dict[str, Any]:
        return {"channel": self.browser_cfg["channel"], "version": self.browser.version if self.browser else None,
                "headless": self.browser_cfg["headless"], "cpu_throttle": self.browser_cfg["cpu_throttle"],
                "viewport": list(self.browser_cfg["viewport"])}

    def run_session(self, spec: SessionSpec, cfg: dict[str, Any]) -> dict[str, Any]:
        t0 = time.perf_counter()
        rec: dict[str, Any] = {"spec": spec.to_dict(), "status": "ok", "failure": None, "wall_s": 0.0, "summary": None, "trials": []}
        w, h = self.browser_cfg["viewport"]
        context = self.browser.new_context(viewport={"width": w, "height": h})
        external: list[str] = []
        page_errors: list[str] = []
        try:
            context.set_offline(True)
            page = context.new_page()
            page.on("request", lambda r: external.append(r.url) if not r.url.startswith("file:") else None)
            page.on("pageerror", lambda e: page_errors.append(str(e)))
            if self.browser_cfg["cpu_throttle"] != 1:
                cdp = context.new_cdp_session(page)
                cdp.send("Emulation.setCPUThrottlingRate", {"rate": self.browser_cfg["cpu_throttle"]})
            page.goto(page_url(spec, cfg))
            page.wait_for_function("window.__scroll !== undefined")
            if not page.evaluate("window.__scroll.ready"):
                raise RuntimeError("page refused configuration: " + str(page.evaluate("window.__scroll.error")))
            K = cfg["interactions_per_session"]
            timeout_ms = spec.latency_ms * (1 + cfg["jitter"]) + cfg["settle_ms"] + cfg["trial_timeout_extra_ms"]
            for k in range(K):
                tt = time.perf_counter()
                page.mouse.move(*NEUTRAL_XY)
                info = page.evaluate("k => window.__scroll.prepare(k)", k)
                page.evaluate("window.__scroll.nextFrames()")
                page.wait_for_timeout(cfg["pre_input_ms"])
                if cfg["decoy_hovers"] and info.get("decoy"):
                    page.mouse.move(*_center(page, info["decoy"]))
                    page.wait_for_timeout(spec.hover_lead_ms)
                    page.mouse.move(*NEUTRAL_XY)
                page.mouse.move(*_center(page, info["target"]))
                page.wait_for_timeout(spec.hover_lead_ms)
                page.mouse.down()
                page.mouse.up()
                raw = page.evaluate(
                    "([k, ms]) => Promise.race([window.__scroll.whenDone(k), new Promise(r => setTimeout(() => r(null), ms))])",
                    [k, timeout_ms])
                metrics = compute_trial_metrics(raw, cfg["settle_ms"], timed_out=raw is None)
                rec["trials"].append({"k": k, "wall_s": time.perf_counter() - tt, "raw": raw, "metrics": metrics})
                if raw is None:
                    for k2 in range(k + 1, K):
                        rec["trials"].append({"k": k2, "wall_s": 0.0, "raw": None, "metrics": empty_metrics("not run: an earlier trial timed out")})
                    break
            summary = page.evaluate("window.__scroll.sessionSummary()")
            summary["js_heap_used_bytes"] = page.evaluate("performance.memory ? performance.memory.usedJSHeapSize : null")
            summary["external_requests"] = external
            summary["page_errors"] = page_errors
            rec["summary"] = summary
            problems = []
            if page_errors or summary.get("errors"):
                problems.append(f"page errors: {page_errors or summary.get('errors')}")
            if external:
                problems.append(f"network requests while offline: {external}")
            if summary.get("stray_clicks"):
                problems.append(f"stray clicks: {summary['stray_clicks']}")
            if problems:
                rec["status"] = "failed"
                rec["failure"] = "; ".join(problems)
        except Exception as exc:  # harness failure: recorded, never silently dropped
            rec["status"] = "failed"
            rec["failure"] = f"{type(exc).__name__}: {exc}\n{traceback.format_exc(limit=3)}"
        finally:
            context.close()
            rec["wall_s"] = time.perf_counter() - t0
        return rec
