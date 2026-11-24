<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# tests/

Run: `PYTHONPATH=src .venv/bin/python -m scroll test` or `uv run pytest`. Browser tests carry the `browser` marker (`-m "not browser"` skips them); they launch the installed Google Chrome through Playwright and are skipped, not passed, if it is unavailable.

| File | Kind |
|---|---|
| `test_schedule.py` | Unit, hand-computed and regression examples, invalid inputs, property tests (jitter bounds, monotone failure in p, uniformity). |
| `test_schedule_differential.py` | Differential: JavaScript schedule in Node versus Python, 2,002 cases, bit-identical. |
| `test_metrics.py` | Hand-computed golden raw records for every arm, exclusions, defects, property tests (wrong = stale + false, bounds). |
| `test_reference.py` | Reference model values and invalid inputs. |
| `test_stats.py` | Hand-computed required n and Holm, bootstrap determinism, invalid inputs, invariants. |
| `test_config.py` | Shipped configs validate; matrix sizes equal the protocol's; invalid configs rejected. |
| `test_freeze_and_cli.py` | Freeze rules; the runner and CLI refuse confirmatory configs while unfrozen (exit 3, before any browser starts). |
| `test_pipeline_integration.py` | Config to results to report with a deterministic fake harness; known effects recovered; tampered results fail closed. |
| `test_browser.py` | Project-specific verification on Chrome: every arm clean, timing chain lower bound, in-page schedule equals Python, rollback under certain failure, layout-shift regressions, keyboard operation and live region, offline (file URLs only), fail-closed configuration, zero latency, CPU throttle path. |

Test counts are reported in `progress.md` from actual runs only.
