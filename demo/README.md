<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# demo/: SCROLL results page (M5)

A static, offline page built with TypeScript, React and Vite (versions pinned by the shared lab template and `package-lock.json`).

What it shows:

- **Overview** with the status label, and the pending owner decision DEC-011 with each reading the manuscript reports (none is chosen).
- **Side-by-side traces** (measured): per-arm cell medians of first feedback and usable content, with the interquartile range of trials, for the read path, the write path with successful saves (p = 0) and the write path with failed saves; a latency slider moves between the measured levels. Each view lists the published contrasts at that delay.
- **Published results** (measured): every contrast of EXP-002 (8), EXP-003 (15) and the four non-robust EXP-004 contrasts at each level, with 95% intervals, Holm p, both test readings and the TOST interval, plus the robustness of all 23 contrasts under both S1 readings. Null results carry the same weight as positive ones. Numbers are printed exactly as in the manuscript.
- **Assumptions**, **method and limitations**, and the owner placeholders.
- **Sandbox** (sandbox output): an exact port of the seeded schedule and the zero-overhead reference model, run in a Web Worker with seed, path, latency, hover lead, failure probability and reset. It computes lower bounds and measures nothing. Its side-by-side replay uses browser timers and is labelled "illustrative, not a measurement"; nothing is recorded.

Data: `public/data/results.json`, written by `scripts/export_demo_data.py` from committed results only (schema `lab-demo-results` 1.0.0 with the SCROLL keys `traces`, `robustness`, `pending_decisions` and `placeholders`). The page validates it and fails closed: a malformed file shows no numbers. `tests/test_demo_export.py` checks that every displayed estimate appears verbatim in the manuscript. The trace medians are a documented exception: the manuscript gives only their ranges, so the test checks them against the committed source files.

Privacy: no visitor input is collected or stored, there is no analytics, no font, image or script from another host, and no request leaves the origin that served the page (checked by `tools/a11y_check.mjs`).

Commands (Node 22):

    npm ci && npm test && npm run build && npm run preview
    node tools/a11y_check.mjs dist --screenshots <dir>

Regenerate the data and the sandbox fixture (from the repository root):

    .venv/bin/python scripts/export_demo_data.py
    .venv/bin/python scripts/export_sandbox_fixture.py

Demo URL: [OWNER PLACEHOLDER: not hosted; publication is the owner's decision].
