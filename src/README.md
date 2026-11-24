<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# src/

M2 layout (2026-11-24). Ingestion, simulation, metrics, runner and serialization are separate modules.

| Path | Role |
|---|---|
| `web/schedule.js`, `scroll/schedule.py` | Seeded latency and failure schedule (DEC-004, proposed). Pure functions; the two twins agree bit for bit (Node differential test). Delay `floor(L (1 + jitter (2u - 1)) + 0.5)` ms; failure iff `u < p`. |
| `web/index.html`, `web/app.js` | The mock catalogue page. One page; the arm (`BLANK`, `SKELETON`, `PREFETCH`, `OPTIMISTIC`) is the only switch. Fails closed on an invalid query. Records raw timestamps and raw `PerformanceObserver` entries only. |
| `scroll/harness.py` | Playwright driver on the installed Google Chrome (`channel="chrome"`), fresh context per session, offline, identical scripted input in every arm. |
| `scroll/reference.py` | Reference model: ideal zero-overhead timing per arm (lower bounds for differential checks). |
| `scroll/metrics.py` | Per-trial metrics from raw records (TTUC, TTFF, alternative paint methods, Event Timing, layout shift, wrong/stale/false-state exposure, correctness, stop-rule checks). |
| `scroll/stats.py` | Seed-level statistics: paired differences, percentile bootstrap, sigma_d, required n, Holm, TOST, Wilcoxon. |
| `scroll/config.py`, `scroll/schemas/config-1.0.0.json` | Config validation, hashing, matrix expansion with seeded arm order. |
| `scroll/schema.py`, `scroll/schemas/result-1.0.0.json` | Versioned result schema, validated at export and at import. |
| `scroll/manifest.py` | Run manifest: config hash, seeds, git revision and dirty flag, package versions, OS, CPU, load average, runtime, peak RSS. |
| `scroll/freeze.py` | Read-only freeze check; never freezes. |
| `scroll/runner.py` | Config to validated `results.json`, `run_manifest.json`, `config.json`, `trials.csv`. |
| `scroll/analysis.py`, `scroll/report.py` | Cell summaries, paired contrasts, degenerate cases, runtime projection; tables, figures and `report.md` (optional PDF through pandoc and Typst). |
| `scroll/cli.py` | `python -m scroll smoke | run | report | test`. |

Run from the repository root with `PYTHONPATH=src` (the project is not an installable package, `tool.uv.package = false`).
