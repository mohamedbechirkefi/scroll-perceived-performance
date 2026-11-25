# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Check that every relative link in the tracked Markdown files resolves (M6).

For each `[text](target)` or `![alt](target)` link outside fenced code blocks and code spans,
external targets (http, https, mailto) are skipped; every other target must name an existing file
or folder relative to the Markdown file, and a `#anchor` must match a heading of the target
Markdown file (GitHub-style slug) or an explicit `{#id}`.

Usage: .venv/bin/python scripts/check_links.py   (prints LINK-CHECK PASS or the failures; exit 1 on failure)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")


def tracked_markdown() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / line for line in out.splitlines() if line and "node_modules/" not in line]


def strip_code(text: str) -> str:
    text = re.sub(r"^(```|~~~).*?^\1[^\n]*$", "", text, flags=re.S | re.M)
    return re.sub(r"`[^`\n]*`", "", text)


def slug(heading: str) -> str:
    h = re.sub(r"\{#[^}]*\}\s*$", "", heading).strip().lower()
    h = re.sub(r"[`*_~]", "", h)
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h)
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(md: Path) -> set[str]:
    text = strip_code(md.read_text(encoding="utf-8"))
    out: set[str] = set()
    counts: dict[str, int] = {}
    for m in re.finditer(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, flags=re.M):
        s = slug(m.group(1))
        n = counts.get(s, 0)
        out.add(s if n == 0 else f"{s}-{n}")
        counts[s] = n + 1
    out.update(re.findall(r"\{#([\w\-]+)", text))
    out.update(re.findall(r"<a\s+(?:name|id)=\"([^\"]+)\"", text))
    return out


def check() -> tuple[int, list[str]]:
    checked, failures = 0, []
    for md in tracked_markdown():
        for m in LINK.finditer(strip_code(md.read_text(encoding="utf-8"))):
            target = m.group(1)
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, flags=re.I):
                continue
            checked += 1
            path_part, _, anchor = target.partition("#")
            dest = md if not path_part else (md.parent / unquote(path_part)).resolve()
            rel = md.relative_to(ROOT)
            if not dest.exists():
                failures.append(f"{rel}: missing target {target}")
                continue
            if anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                failures.append(f"{rel}: missing anchor {target}")
    return checked, failures


def main() -> int:
    checked, failures = check()
    for f in failures:
        print("FAIL", f)
    print(f"relative links checked: {checked}; failures: {len(failures)}")
    print("LINK-CHECK PASS" if not failures else "LINK-CHECK FAIL")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
