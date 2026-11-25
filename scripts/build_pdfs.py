# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Build the publication PDFs (M6) through the DEC-002 route: pandoc to Typst, compiled with the
`typst` Python package. Same route as `scroll.report.build_pdf`, with three additions:

- the manuscript is converted with `--citeproc --bibliography research/paper/references.bib`
  (its citations do not resolve otherwise);
- the PDF document title is set from the first heading or the YAML title (`#set document`), so
  that the metadata carries a title and no local path;
- the intermediate `.typ` files go to a separate folder (default: a temporary folder), never next
  to the committed Markdown.

Optionally `--png DIR` renders every page to PNG for visual inspection, and `--tex` regenerates
`research/paper/manuscript.tex` (with its two header comment lines).

Usage: .venv/bin/python scripts/build_pdfs.py [--typ-dir DIR] [--png DIR] [--tex]
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import tempfile
from pathlib import Path

import typst

ROOT = Path(__file__).resolve().parents[1]
PANDOC = os.environ.get("SCROLL_PANDOC", str(ROOT.parent / ".tools" / "pandoc"))
BIB = "research/paper/references.bib"

DOCS = [
    ("research/paper/manuscript.md", "research/paper/manuscript.pdf", True, "ms"),
    ("research/paper/supplementary.md", "research/paper/supplementary.pdf", False, "supp"),
    ("research/experiments/EXP-001/report.md", "research/experiments/EXP-001/report.pdf", False, "exp001"),
    ("research/experiments/EXP-002/report.md", "research/experiments/EXP-002/report.pdf", False, "exp002"),
    ("research/experiments/EXP-003/report.md", "research/experiments/EXP-003/report.pdf", False, "exp003"),
    ("research/experiments/EXP-004/report.md", "research/experiments/EXP-004/report.pdf", False, "exp004"),
]

TEX_HEADER = (
    "% SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0\n"
    "% Generated from manuscript.md by pandoc 3.6.3 (-s --citeproc --bibliography research/paper/references.bib -t latex). "
    "Do not edit by hand. Not compiled locally: no TeX engine (DEC-002).\n"
)


def doc_title(md_text: str) -> str:
    m = re.search(r'^title:\s*"(.*)"\s*$', md_text, re.M)
    if m:
        return m.group(1)
    m = re.search(r"^# (.+)$", md_text, re.M)
    return m.group(1).strip() if m else "SCROLL"


def typst_string(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build(md: str, pdf: str, cite: bool, typ_dir: Path) -> Path:
    src = ROOT / md
    typ = typ_dir / (Path(md).parent.name + "-" + Path(md).stem + ".typ")
    cmd = [PANDOC, str(src), "-s", "-t", "typst-citations", "-V", "mainfont=Libertinus Serif",
           "--resource-path", str(src.parent), "-o", str(typ)]
    if cite:
        cmd[2:2] = ["--citeproc", "--bibliography", str(ROOT / BIB)]
    subprocess.run(cmd, check=True, cwd=ROOT)
    text = typ.read_text(encoding="utf-8")
    title = doc_title(src.read_text(encoding="utf-8"))
    # The template's `set document(title: title, ...)` runs inside `conf` and wins over any outer rule,
    # so the title is written into that rule (documents without YAML title would otherwise get none).
    old = "  set document(\n    title: title,"
    if old not in text:
        raise SystemExit(f"pandoc typst template changed: cannot set the document title for {md}")
    text = text.replace(old, f"  set document(\n    title: {typst_string(title)},", 1)
    # Readability (M6 visual inspection): pandoc gives Markdown pipe tables equal percentage widths,
    # which split short words over lines; let Typst size columns to their content instead, set
    # tables slightly smaller, and allow long tables to break across pages instead of leaving a
    # blank page before them.
    text = re.sub(r"columns: \((?:[\d.]+%(?:, )?)+\)",
                  lambda m: "columns: (" + "auto, " * m.group(0).count("%") + ")", text)
    rules = ("#show figure.where(kind: table): set block(breakable: true)\n"
             "#show table: set text(size: 0.85em)\n"
             "#show table: set par(justify: false)\n"
             # Inline code in table cells (paths, 64-character hashes) cannot break and overlapped the
             # next column: allow a line break after a slash, underscore, hyphen or comma and inside long hex runs.
             "#show table: it => { show raw.where(block: false): r => { "
             "show regex(\"[/_,-]|[0-9a-f]{16}\"): m => m + sym.zws; r }; it }\n")
    text = text.replace("\n#show: doc => conf(", "\n" + rules + "#show: doc => conf(", 1)
    typ.write_text(text, encoding="utf-8")
    typst.compile(str(typ), output=str(ROOT / pdf), root=str(typ.parent))
    return typ


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--typ-dir", type=Path)
    ap.add_argument("--png", type=Path)
    ap.add_argument("--ppi", type=int, default=60)
    ap.add_argument("--tex", action="store_true")
    a = ap.parse_args()
    typ_dir = a.typ_dir or Path(tempfile.mkdtemp(prefix="scroll-typ-"))
    typ_dir.mkdir(parents=True, exist_ok=True)
    for md, pdf, cite, tag in DOCS:
        typ = build(md, pdf, cite, typ_dir)
        print(f"wrote {pdf} ({(ROOT / pdf).stat().st_size} bytes)")
        if a.png:
            a.png.mkdir(parents=True, exist_ok=True)
            typst.compile(str(typ), output=str(a.png / f"{tag}-{{p}}.png"), format="png", ppi=a.ppi, root=str(typ.parent))
    if a.tex:
        out = ROOT / "research/paper/manuscript.tex"
        subprocess.run([PANDOC, "research/paper/manuscript.md", "-s", "--citeproc", "--bibliography", BIB,
                        "-t", "latex", "-o", str(out)], check=True, cwd=ROOT)
        out.write_text(TEX_HEADER + out.read_text(encoding="utf-8"), encoding="utf-8")
        print("wrote research/paper/manuscript.tex")


if __name__ == "__main__":
    main()
