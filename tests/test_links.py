# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""M6: every relative link in the tracked Markdown files resolves (scripts/check_links.py)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("check_links", ROOT / "scripts" / "check_links.py")
check_links = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_links)


def test_all_relative_links_resolve():
    checked, failures = check_links.check()
    assert checked > 0
    assert failures == []


def test_link_pattern_and_code_spans_are_handled():
    text = "See [a](docs/x.md#part) and ![img](docs/demo.png), not `[b](missing.md)` or [c](https://example.org)."
    targets = [m.group(1) for m in check_links.LINK.finditer(check_links.strip_code(text))]
    assert targets == ["docs/x.md#part", "docs/demo.png", "https://example.org"]


def test_anchor_slugs(tmp_path):
    md = tmp_path / "a.md"
    md.write_text("# Title\n\n## 2. Related work\n\n## Data and code availability\n\n## Title\n", encoding="utf-8")
    assert check_links.anchors(md) >= {"title", "2-related-work", "data-and-code-availability", "title-1"}
