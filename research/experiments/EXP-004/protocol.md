<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# EXP-004: Sensitivity analyses for EXP-002 and EXP-003

- Status: planned (protocol draft, awaiting owner freeze).
- Version: draft v0.1, 2026-11-24. Protocol hash: not yet recorded (computed at freeze).
- Depends on: EXP-002 and EXP-003 completed.

## 1. Precise question

Do the primary verdicts of EXP-002 and EXP-003 (sign of each contrast, and the SKELETON equivalence verdict) survive changes in measurement method, CPU load, prefetch lead time and rendering mode?

## 2. Why this could invalidate the main interpretation

If TTUC differences of a few frames come from how frames are timed rather than from the strategy, the measurement method will change the verdict. If skeleton or rollback costs appear only under CPU load, the 1x results understate them.

## 3. Factors (one at a time against the main configuration)

| ID | Factor | Levels |
|---|---|---|
| S1 | Frame-time method | double rAF marker (main) versus alternative chosen in EXP-001 (Element Timing or trace) |
| S2 | CPU throttling | 1x versus 4x (mechanism to be verified; CDP documentation not opened in M0) |
| S3 | Prefetch lead time h | 0, 150, 600 ms |
| S4 | Rendering mode | headless versus headed |

Reduced matrix: L in {300, 1000} ms, p in {0, 0.3} for the write path, seeds 1..10, K = 10. About 2,000 interactions in total (exact count fixed at freeze).

## 4. Decision rule

For each primary contrast, report the main and sensitivity estimates side by side. A verdict is "robust" only if its sign (or equivalence verdict) is the same under every factor level. Any change is reported prominently as method-dependent or condition-dependent; the main interpretation is then qualified in the manuscript.

## 5. Uncertainty

Same bootstrap as the parent protocol, with 10 seeds; intervals will be wider, and this is stated.

## 6. Reproduction (planned)

`uv run python -m scroll.run --experiment EXP-004` (not yet implemented).
