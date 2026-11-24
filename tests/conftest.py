# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def smoke_cfg() -> dict:
    return copy.deepcopy(json.loads((ROOT / "experiments" / "smoke.json").read_text()))


@pytest.fixture(scope="session")
def harness():
    from scroll.harness import Harness

    cfg = {"channel": "chrome", "headless": True, "cpu_throttle": 1, "viewport": [1280, 800]}
    try:
        h = Harness(cfg).__enter__()
    except Exception as exc:  # recorded as a skip with the reason, never as a pass
        pytest.skip(f"installed Chrome not available through Playwright: {exc}")
    yield h
    h.__exit__(None, None, None)
