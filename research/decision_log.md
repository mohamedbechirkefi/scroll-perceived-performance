<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Decision log

Append-only. Each entry: id, date, decision, decided by, rationale, alternatives, consequences. Entries marked "proposed" await the owner and are not in force until the owner confirms them.

## DEC-001: Repository licence (owner decision)

- Date: 2026-11-24
- Decided by: the owner
- Status: in force
- Decision: all original material in this repository is licensed under the "SCROLL Source-Available Non-Commercial Research License v1.0" (SPDX id `LicenseRef-SCROLL-NC-Research-1.0`), with a contributor licence agreement (CLA v1.0). The licence package (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `CONTRIBUTING.md`, `.github/CODEOWNERS`, `.github/workflows/cla.yml`) was committed at the first commit.
- Rationale: the owner chose this protective licence for their own protection.
- Deviation from the master prompt: section 2 of `master_prompt.md` asks for an "owner-approved permissive code license". The owner instead chose this custom, source-available, non-commercial licence. It is not an OSI-approved open-source licence. Sessions must not change the licence files.
- Consequences: the project is "source-available", not "open source", in every public text. Third-party data and dependencies keep their own licences (recorded in `data/manifest.json` and `uv.lock`).

## DEC-002: Zero-cost publication toolchain

- Date: 2026-11-24
- Decided by: the AI assistant within the brief; confirmable by the owner
- Status: in force (tooling choice, no scientific consequence)
- Decision: there is no TeX distribution on the machine. Markdown stays the canonical source. PDFs are produced by pandoc 3.6.3 (Markdown to Typst), compiled with the `typst` Python package 0.15.0 from `/Users/bechir/research/labs/.tools/py/bin/`. `research/paper/manuscript.tex` is generated from Markdown by pandoc (`-t latex -s`) as a source artifact only; it is not compiled locally.
- Alternatives considered: installing TeX Live or Tectonic (large download, outside the tools allowed in this session); a paid typesetting service (forbidden).
- Consequences: every PDF claim in the repository must name the Typst route. A LaTeX PDF is not claimed until a TeX engine exists.

## DEC-003: Dependency lock policy

- Date: 2026-11-24
- Decided by: the AI assistant within the brief
- Status: in force
- Decision: Python dependencies are locked with uv 0.9.5 in `uv.lock`. `pyproject.toml` sets `[tool.uv] exclude-newer = "2026-11-10T00:00:00Z"` so that only distributions uploaded at least two weeks before 2026-11-24 are resolved. No `package.json` yet: the demo is not set up in M0.
- Consequences: adding or upgrading a dependency is a recorded decision.

## DEC-004 (proposed): Deterministic in-page mock transport for latency and failure injection

- Date: 2026-11-24
- Decided by: proposal, awaiting the owner
- Decision: latency and failures are injected by a seeded in-page mock transport (a pure function from `(seed, request index)` to `(delay_ms, outcome)`), not by network throttling or Playwright route handlers. The same schedule module will drive the browser harness and the demo.
- Rationale: identical schedules across arms (common random numbers), no network, offline by construction, reusable by the static demo.
- Alternatives: Playwright `page.route` with an async pause before `route.fulfill` (not documented as a delay feature on the page read on 2026-11-24); Chrome DevTools network throttling (shapes bandwidth, not per-request latency).
- Consequences: timer resolution and main-thread scheduling of the mock become a threat to construct validity, checked in EXP-001.

## DEC-005 (proposed): Browser binary for the harness

- Date: 2026-11-24
- Decided by: proposal, awaiting the owner
- Decision options: (a) download Playwright's pinned Chromium build with `playwright install chromium` (free, about 150 MB order of magnitude, unverified size), giving a version pinned with the lockfile; (b) use the installed Google Chrome 158.0.8127.38 through `channel="chrome"`, which auto-updates and can change between runs.
- Recommendation: option (a), with the browser version recorded in every run manifest.
