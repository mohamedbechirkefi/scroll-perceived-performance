<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# EXP-004: Sensitivity analyses for EXP-002 and EXP-003

- Status: frozen (owner-approved 2026-11-24), not yet run. Confirmatory.
- Version: v1.0, 2026-11-24 (draft v0.1 plus the owner-approved amendments listed in section "Amendments before freeze"). Protocol hash: SHA-256 recorded in `research/freeze.json` and `research/experiment_registry.csv` (a file cannot contain its own hash).
- Parent protocol: `research/protocol.md` v1.0 (frozen).
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

Reduced matrix: L in {300, 1000} ms, p in {0, 0.3} for the write path, seeds 1..10, K = 10. Exact counts at freeze, from the frozen configurations: S2 (`experiments/EXP-004-S2.json`) 140 sessions, 1,400 interactions; S3 (`experiments/EXP-004-S3.json`) 80 sessions, 800 interactions; S4 (`experiments/EXP-004-S4.json`) 140 sessions, 1,400 interactions; S1 reuses the EXP-002 and EXP-003 runs (no new sessions). Total 3,600 interactions (the draft estimate was about 2,000).

Contrasts are computed with the frozen estimand of the parent protocol (amendments A1 and A2: trial-level pairing; write path at p = 0.3 split into success and failure strata, the failure stratum having 9 of the 10 seeds by schedule). The hover-lead control (A3) applies to the read path, including S3 with h = 0 and h = 600 ms. The installed Google Chrome is used with its version recorded (A5); the seed count stays at 10 (A6 concerns the main experiments).

## 4. Decision rule

For each primary contrast, report the main and sensitivity estimates side by side. A verdict is "robust" only if its sign (or equivalence verdict) is the same under every factor level. Any change is reported prominently as method-dependent or condition-dependent; the main interpretation is then qualified in the manuscript.

## 5. Uncertainty

Same bootstrap as the parent protocol, with 10 seeds; intervals will be wider, and this is stated.

## 6. Reproduction (planned)

`.venv/bin/python -m scroll run --config experiments/EXP-004-S2.json` (and `-S3`, `-S4`); frozen configurations, hashes in `research/freeze.json`. Editorial correction at freeze: the draft named a command that was never implemented.

## Amendments before freeze (owner-approved 2026-11-24)

- A1, A2, A3, A5 applied through the parent protocol (section 3 above). A4: Event Timing descriptive only. A6: no change to EXP-004 (10 seeds).
- Details and quotes: `research/protocol.md`, section 11; `research/decision_log.md`, DEC-009.
