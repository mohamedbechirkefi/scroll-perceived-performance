# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Browser tests on the installed Google Chrome (project-specific verification, master prompt section 10):
accessibility, error rollback, timing instrumentation, layout-shift regressions and offline behaviour."""
from urllib.parse import urlencode

import pytest

from scroll import schedule as S
from scroll.config import SessionSpec
from scroll.harness import WEB_INDEX

pytestmark = pytest.mark.browser


def _cfg(smoke_cfg, **kw):
    c = dict(smoke_cfg)
    c.update(kw)
    return c


def _spec(path, arm, L=100.0, p=0.0, h=150.0, seed=1001):
    return SessionSpec("T0001", seed, 0, path, arm, float(L), float(p), float(h), 0)


def _ok(rec):
    assert rec["status"] == "ok", rec["failure"]
    return [t["metrics"] for t in rec["trials"]]


def _page(harness, **q):
    ctx = harness.browser.new_context()
    ctx.set_offline(True)
    page = ctx.new_page()
    urls = []
    page.on("request", lambda r: urls.append(r.url))
    page.goto(WEB_INDEX.as_uri() + "?" + urlencode(q))
    page.wait_for_function("window.__scroll !== undefined")
    return ctx, page, urls


@pytest.mark.parametrize("path,arm", [("read", "BLANK"), ("read", "SKELETON"), ("read", "PREFETCH"), ("write", "BLANK"), ("write", "OPTIMISTIC")])
def test_every_arm_runs_clean(harness, smoke_cfg, path, arm):
    rec = harness.run_session(_spec(path, arm, p=0.5 if path == "write" else 0), _cfg(smoke_cfg, interactions_per_session=3, settle_ms=100))
    ms = _ok(rec)
    assert len(ms) == 3 and all(m["status"] == "ok" for m in ms)
    assert all(m["defects"] == [] for m in ms), [m["defects"] for m in ms]
    assert all(m["final_correct"] for m in ms)
    assert rec["summary"]["a11y"]["passed"], rec["summary"]["a11y"]["issues"]
    assert rec["summary"]["external_requests"] == [] and rec["summary"]["errors"] == []


def test_timing_chain_lower_bound_and_order(harness, smoke_cfg):
    rec = harness.run_session(_spec("read", "BLANK", L=300), _cfg(smoke_cfg, interactions_per_session=3, settle_ms=100))
    for t in rec["trials"]:
        raw, m = t["raw"], t["metrics"]
        assert m["ttuc_ms"] >= m["delay_ms"]                      # C1
        assert raw["request"]["t_end"] - raw["request"]["t_start"] >= m["delay_ms"] - 1  # timer never early by > 1 ms
        f = raw["frames"][-1]
        assert f["t_commit"] <= f["t_raf1"] <= f["t_raf2"]
        assert raw["t_in"] <= raw["t_handler"]
        assert m["ttuc_element_ms"] is not None and m["ttuc_raf1_ms"] <= m["ttuc_ms"]


def test_page_schedule_equals_python(harness):
    ctx, page, _ = _page(harness, path="read", arm="BLANK", seed=1, L=100)
    try:
        cases = [(s, st, i, L, 0.1, p) for s in (0, 1001, 2**32 - 1) for st in ("read", "write", "decoy") for i in (0, 7) for L in (50, 1000) for p in (0, 0.3)]
        js = page.evaluate("cs => cs.map(c => { const r = ScrollSchedule.schedule(...c); return [r.delayMs, r.ok]; })", cases)
        assert js == [[S.schedule(*c).delay_ms, S.schedule(*c).ok] for c in cases]
    finally:
        ctx.close()


def test_optimistic_rollback_with_certain_failure(harness, smoke_cfg):
    rec = harness.run_session(_spec("write", "OPTIMISTIC", L=100, p=1.0), _cfg(smoke_cfg, interactions_per_session=3, settle_ms=100))
    for t in rec["trials"]:
        m, raw = t["metrics"], t["raw"]
        assert m["request_ok"] is False and m["final_correct"] is True
        assert [f["kind"] for f in raw["frames"]] == ["optimistic", "rollback"]
        assert m["false_state_ms"] > 0 and m["focus_on_toggle"] is True
        assert raw["final_display"]["pressed"] is False and "Could not save" in raw["final_display"]["error_text"]


def test_blank_write_never_shows_unconfirmed_state(harness, smoke_cfg):
    rec = harness.run_session(_spec("write", "BLANK", L=100, p=0.5), _cfg(smoke_cfg, interactions_per_session=4, settle_ms=100))
    assert all(t["metrics"]["false_state_ms"] == 0 for t in rec["trials"])


def test_layout_shift_regressions(harness, smoke_cfg):
    cfg = _cfg(smoke_cfg, interactions_per_session=2, settle_ms=300)
    sk = _ok(harness.run_session(_spec("read", "SKELETON", L=700), cfg))
    bl = _ok(harness.run_session(_spec("read", "BLANK", L=700), cfg))
    rs = _ok(harness.run_session(_spec("read", "BLANK", L=700), {**cfg, "reserve_space_blank": True}))
    wr = _ok(harness.run_session(_spec("write", "OPTIMISTIC", L=100, p=0.5), cfg))
    # The skeleton has the final box size: its only shift happens at input (hadRecentInput), never after.
    assert all(m["layout_shift_cls"] == 0 for m in sk)
    # The design contrast: a collapsed BLANK region shifts content after 500 ms without recent input.
    assert all(m["layout_shift_cls"] > 0 for m in bl)
    # Reserving the region removes it; the write panel (fixed-height status line) never shifts.
    assert all(m["layout_shift_all"] == 0 for m in rs)
    assert all(m["layout_shift_all"] == 0 for m in wr)


def test_keyboard_operation_and_live_region(harness):
    ctx, page, _ = _page(harness, path="write", arm="OPTIMISTIC", seed=1001, L=50, p=1, items=2, settle=50)
    try:
        page.evaluate("window.__scroll.prepare(0)")
        page.focus("#save")
        page.keyboard.press("Enter")
        r0 = page.evaluate("window.__scroll.whenDone(0)")
        assert r0["input_type"] == "keyboard" and r0["final_display"]["focus_on_toggle"] is True
        assert page.get_attribute("#status", "role") == "status" and "Could not save" in page.text_content("#status")
        page.evaluate("window.__scroll.prepare(1)")
        page.focus("#save")
        page.keyboard.press("Space")
        r1 = page.evaluate("window.__scroll.whenDone(1)")
        assert r1["input_type"] == "keyboard"
    finally:
        ctx.close()
    ctx, page, _ = _page(harness, path="read", arm="SKELETON", seed=1001, L=50, items=1, settle=50)
    try:
        page.evaluate("window.__scroll.prepare(0)")
        page.focus("#item-0")
        page.keyboard.press("Enter")
        r = page.evaluate("window.__scroll.whenDone(0)")
        assert r["input_type"] == "keyboard" and r["final_display"]["content_item"] == 0
        assert [f["state"]["aria_busy"] for f in r["frames"]] == ["true", "false"]
    finally:
        ctx.close()


def test_offline_only_local_files(harness):
    ctx, page, urls = _page(harness, path="read", arm="PREFETCH", seed=1001, L=50, items=1, settle=50)
    try:
        assert page.evaluate("window.__scroll.ready") is True
        assert urls and all(u.startswith("file:") for u in urls)
    finally:
        ctx.close()


@pytest.mark.parametrize("q", [dict(path="read", arm="OPTIMISTIC", seed=1, L=1), dict(path="write", arm="BLANK", seed=-1, L=1),
                               dict(path="read", arm="BLANK", seed=1, L=1, p=0.5), dict(path="read", arm="BLANK", seed=1),
                               dict(path="write", arm="BLANK", seed=1, L=1, p=2), dict(path="nope", arm="BLANK", seed=1, L=1)])
def test_invalid_configuration_fails_closed(harness, q):
    ctx, page, _ = _page(harness, **q)
    try:
        assert page.evaluate("window.__scroll.ready") is False
        assert page.is_visible("#config-error") and page.get_attribute("#config-error", "role") == "alert"
        assert not page.is_visible("#read-panel") and not page.is_visible("#write-panel")
    finally:
        ctx.close()


def test_extreme_parameters_zero_latency(harness, smoke_cfg):
    ms = _ok(harness.run_session(_spec("read", "BLANK", L=0), _cfg(smoke_cfg, interactions_per_session=2, settle_ms=0, jitter=0.0)))
    assert all(m["delay_ms"] == 0 and m["ttuc_ms"] >= 0 for m in ms)


def test_cpu_throttle_path(harness, smoke_cfg):
    from scroll.harness import Harness
    h = Harness({"channel": "chrome", "headless": True, "cpu_throttle": 4, "viewport": [1280, 800]})
    h.browser = harness.browser  # one Playwright instance per process; reuse its browser
    ms = _ok(h.run_session(_spec("read", "SKELETON", L=100), _cfg(smoke_cfg, interactions_per_session=2, settle_ms=50)))
    assert all(m["status"] == "ok" and m["defects"] == [] for m in ms)


def test_prepare_guards(harness):
    ctx, page, _ = _page(harness, path="read", arm="BLANK", seed=1, L=10, items=2, settle=0)
    try:
        with pytest.raises(Exception):
            page.evaluate("window.__scroll.prepare(5)")
        page.evaluate("window.__scroll.prepare(0)")
        with pytest.raises(Exception, match="not finished"):
            page.evaluate("window.__scroll.prepare(1)")
    finally:
        ctx.close()
