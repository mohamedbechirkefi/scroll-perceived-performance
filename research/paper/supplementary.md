<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Supplementary material

Status: M4 synthesis, 2026-11-25. Independent research manuscript / preprint draft, not peer-reviewed. Every number comes from a committed result file; the mapping is in `research/publication/artifact_manifest.json`.

## S1. Complete experimental matrix

| Experiment | Label | Arms | Conditions | Seeds | K | Sessions | Interactions | Runs |
|---|---|---|---|---|---|---|---|---|
| EXP-001 | exploratory | read BLANK, SKELETON, PREFETCH; write BLANK, OPTIMISTIC | L {100, 1000} ms; p {0, 0.5} (write); h 150 ms | 1001 to 1005 | 5 | 70 per run | 350 per run | `EXP-001-20261124T161058Z`, `EXP-001-20261125T065102Z` |
| EXP-002 | confirmatory | BLANK, SKELETON, PREFETCH | L {50, 100, 300, 1000} ms; h 150 ms | 1 to 20 | 10 | 240 | 2,400 | `EXP-002-20261125T070315Z` |
| EXP-003 | confirmatory | BLANK, OPTIMISTIC | L {100, 300, 1000} ms; p {0, 0.1, 0.3} | 1 to 20 | 10 | 360 | 3,600 | `EXP-003-20261125T080838Z` |
| EXP-004 S1 | confirmatory | as EXP-002 and EXP-003 | alternative paint methods on the main runs | as main | 10 | 0 (reuse) | 0 (reuse) | main runs |
| EXP-004 S2 | confirmatory | all EXP-002 and EXP-003 arms | CPU 4x; L {300, 1000} ms; p {0, 0.3} | 1 to 10 | 10 | 140 | 1,400 | `EXP-004-20261125T095434Z` |
| EXP-004 S3 | confirmatory | BLANK, PREFETCH | h {0, 600} ms; L {300, 1000} ms | 1 to 10 | 10 | 80 | 800 | `EXP-004-20261125T103912Z` |
| EXP-004 S4 | confirmatory | all EXP-002 and EXP-003 arms | headed; L {300, 1000} ms; p {0, 0.3} | 1 to 10 | 10 | 140 | 1,400 | `EXP-004-20261125T110537Z` |
| M4 re-analysis | exploratory, post hoc | none (no browser run) | committed traces of the five confirmatory runs | none | none | 0 | 0 | `results/exploratory/M4-REANALYSIS/` |

## S2. Execution and sample counts

| Run | Sessions ok | Trials analysed | Exclusions | Runtime (s) | Load at start (1, 5, 15 min) |
|---|---|---|---|---|---|
| EXP-002 | 240 of 240 | 2,387 of 2,400 | 13 (A3 hover lead) | 3,887.4 | 1.78, 1.83, 6.55 |
| EXP-003 | 360 of 360 | 3,600 of 3,600 | 0 | 6,318.7 | 2.36, 1.77, 1.74 |
| EXP-004 S2 | 140 of 140 | 1,400 of 1,400 | 0 | 2,677.9 | 1.37, 1.41, 1.51 |
| EXP-004 S3 | 80 of 80 | 796 of 800 | 4 (A3 hover lead) | 1,584.4 | 2.29, 2.12, 1.74 |
| EXP-004 S4 | 140 of 140 | 1,400 of 1,400 | 0 | 2,676.1 | 2.19, 2.42, 2.28 |

No session failed, no cell failed, no defect flag was raised and the stop rule was never triggered. Chrome 158.0.8127.38 throughout; code revision `b5a72c3` (clean) for every confirmatory run.

## S3. Configurations and hashes

| Item | Path | SHA-256 or canonical hash |
|---|---|---|
| Parent protocol v1.0 | `research/protocol.md` | `a87ae45e049c16ed42abef0ab853a0e3fcf28daec9d5482d11bbb1dfb365f004` |
| EXP-002 protocol | `research/experiments/EXP-002/protocol.md` | `3d263935e5ed7f97f673b0c4b2beb27ea3b3016184c6d58186655358c73b2f1d` |
| EXP-003 protocol | `research/experiments/EXP-003/protocol.md` | `2667ba2f078ba5eeccdcecf05a38cf8b8553343ff4d1ec2c5e75cdd1bcda151c` |
| EXP-004 protocol | `research/experiments/EXP-004/protocol.md` | `9d67a8e91d965456c9fddaf372db1d21156840f311478d8647509aa46e5ae54d` |
| EXP-001 configuration | `experiments/EXP-001.json` | `f39023e2ef11d9ea44951792ee5fa0316711486e081cd8c5d758d4aab0996c6c` |
| EXP-002 configuration | `experiments/EXP-002.json` | `1040b20e1c79173c4393a2529af2f5abc8450c49bdba57beec0b0c7c7aacf752` |
| EXP-003 configuration | `experiments/EXP-003.json` | `11ad05387d0a71c879db8bcab4ced8f19b401aba46b988ee696bb3c4c0ddd58c` |
| EXP-004 S2 configuration | `experiments/EXP-004-S2.json` | `200f25f294f699d3128b815bd130deeab7829e0121d82e4a3a78ac355ee9339e` |
| EXP-004 S3 configuration | `experiments/EXP-004-S3.json` | `5a8b8a7d9e8b4f2c091f6ceaa69a874ce5b9f45b424334b5749a1d90de7d62a5` |
| EXP-004 S4 configuration | `experiments/EXP-004-S4.json` | `7c7b667ce8baebb24379af137c3d2f5f66c5f0df8ccba720f461f639f189fc50` |
| Freeze record | `research/freeze.json` | freeze revision `b4bd25b02368dbde1805bf56864c2db680d93178` |

## S4. Extended tables

### S4.1 EXP-002 cell summaries (trial level, medians)

| L (ms) | Arm | Trials | TTUC (ms) | IQR (ms) | TTFF (ms) | Excess over model (ms) | Event Timing below 16 ms |
|---|---|---|---|---|---|---|---|
| 50 | BLANK | 200 | 77.2 | 75.2 to 79.9 | 77.2 | 27.2 | 71% |
| 50 | SKELETON | 200 | 60.9 | 59.2 to 63.7 | 27.5 | 10.9 | 20% |
| 50 | PREFETCH | 199 | 27.7 | 25.8 to 30.1 | 27.7 | 27.7 | 17% |
| 100 | BLANK | 198 | 112.4 | 109.8 to 125.3 | 112.4 | 16.3 | 71% |
| 100 | SKELETON | 198 | 112.3 | 109.2 to 124.3 | 28.0 | 15.7 | 23% |
| 100 | PREFETCH | 199 | 27.7 | 25.8 to 30.2 | 27.7 | 27.7 | 16% |
| 300 | BLANK | 200 | 323.8 | 295.6 to 331.9 | 323.8 | 15.6 | 74% |
| 300 | SKELETON | 199 | 314.9 | 296.4 to 328.1 | 27.9 | 14.4 | 19% |
| 300 | PREFETCH | 199 | 159.8 | 143.2 to 176.7 | 159.8 | 14.9 | 76% |
| 1000 | BLANK | 198 | 1029.3 | 960.3 to 1075.2 | 1029.3 | 14.5 | 79% |
| 1000 | SKELETON | 199 | 1026.6 | 958.4 to 1073.6 | 27.9 | 13.7 | 19% |
| 1000 | PREFETCH | 198 | 867.7 | 808.9 to 915.3 | 867.7 | 15.4 | 76% |

Source: `results/raw/EXP-002/EXP-002-20261125T070315Z/report/cell_summary.csv`.

### S4.2 EXP-003 secondary mixed estimand and trend check

| L (ms) | p = 0 | p = 0.1 | p = 0.3 | Strictly decreasing magnitude |
|---|---|---|---|---|
| 100 | -85.2 | -84.0 [-85.3, -82.6] | -81.8 [-84.2, -81.1] | yes |
| 300 | -288.5 | -283.8 [-288.9, -281.5] | -274.6 [-281.3, -270.9] | yes |
| 1000 | -998.6 | -974.1 [-998.1, -956.4] | -951.5 [-967.8, -929.2] | yes |

Source: `results/raw/EXP-003/EXP-003-20261125T080838Z/report/inference.json` (`mixed_trend`).

### S4.3 EXP-003 wrong-state exposure in failure trials (medians, ms; 83 failure trials per delay and arm)

| L (ms) | BLANK false state | OPTIMISTIC false state | Injected delay |
|---|---|---|---|
| 100 | 0.0 | 83.4 | 101.0 |
| 300 | 0.0 | 283.9 | 304.0 |
| 1000 | 0.0 | 999.1 | 1014.0 |

Stale state was 0.0 in both arms in failure trials. Source: `results/raw/EXP-003/EXP-003-20261125T080838Z/results.json`, fields `false_state_ms`, `stale_state_ms` and `wrong_state_ms` of trials with `request_ok = false` (computed by a one-off command in M3; not yet produced by the generator, see the evidence audit).

### S4.4 EXP-002 SKELETON at L = 50 ms, frame decomposition (exploratory, X2)

| Quantity (median, ms) | BLANK | SKELETON |
|---|---|---|
| TTUC, main method | 77.2 | 60.9 |
| First frame relative to the reference delay (rAF1 minus delay) | 8.1 | -7.0 |
| Second-frame gap (main minus rAF1) | 18.9 | 18.8 |
| Element Timing minus rAF1 | 11.5 | 16.2 |
| Share of trials whose first frame starts before the reference | 1% | 83% |

Trial-level SKELETON minus BLANK at L = 50 ms (200 pairs): main method median -16.5 ms (IQR -19.3 to -14.2), rAF1 -15.5 ms, Element Timing -9.3 ms. Source: `results/exploratory/M4-REANALYSIS/x2_frame_decomposition.csv` and `x2_skeleton_l50_trial_distribution.csv`.

## S5. Robustness results

The complete side-by-side table of all 23 primary contrasts at every level is in `research/experiments/EXP-004/report.md`, section 8, generated from `results/raw/EXP-004/sensitivity/sensitivity.json`. Summary of the readings:

| Reading | Robust | Method-dependent | Condition-dependent | Both | Not assessed |
|---|---|---|---|---|---|
| Frozen rule, S1 = rAF1 and Element Timing (DEC-011 item 5; frozen verdicts) | 19 | 2 | 1 | 1 | 0 |
| Frozen rule, S1 = Element Timing only (X6; exploratory) | 11 | 1 | 2 | 0 | 9 |
| Interval reading, non-SKELETON contrasts only (X4; exploratory) | 18 of 19 consistent (12 excluding 0 on the same side at every level, 6 including 0 at every level); 1 mixed (PREFETCH L = 300 ms, at h = 0 only) | | | | |

## S6. Experiment report links

- EXP-001 (exploratory): `research/experiments/EXP-001/report.md` (composed in M4; see `progress.md` for how it was written).
- EXP-002: `research/experiments/EXP-002/report.md`.
- EXP-003: `research/experiments/EXP-003/report.md`.
- EXP-004: `research/experiments/EXP-004/report.md`.
- Generated run reports: `results/raw/<EXP>/<run>/report/report.md` and `report.pdf` (generated, not visually inspected).

## S7. Confounder inspection per conclusion

| Conclusion | Competing explanations (protocol) | Addressed by | Not addressed |
|---|---|---|---|
| PREFETCH reduces TTUC by about min(h, L) | cache-lookup overhead; frame alignment; hover-lead jitter | mechanical check (deviation at most 15.1 ms); S1 and S3 robust; A3 exclusions and X3 (no verdict change) | real hover behaviour; network caching; other engines |
| SKELETON equivalent at L of 100 ms and more | placeholder rendering cost (positive Delta); frame alignment | every estimate within 1.2 ms of 0 at every level, including CPU 4x (S2) and headed (S4) | complex placeholders; large DOM; framework rendering |
| SKELETON at L = 50 ms | frame alignment (EXP-002 protocol: "artificial 8 to 17 ms steps") | S1 (method-dependent); X2 (difference sits in first-frame alignment; second-frame gap equal) | why the renderer was idle for BLANK at 50 ms only; display-tied rendering |
| OPTIMISTIC success benefit of about the delay | confirmation-callback scheduling | S1, S2, S4 robust; shifts of 5.9 to 27.0 ms | retries; real servers |
| No TTUC difference on failure | rollback re-render cost; error-message layout shift; callback scheduling | largest estimate 2.7 ms (interval to 5.4 ms); layout shift 0 in every write cell; X4 intervals include 0 at every level | no equivalence test registered; 12 or 18 seeds |
| Mixed advantage shrinks with p | mixture of strata | frozen trend check passes at every L | p above 0.3 |
| Every conclusion | machine load and time drift; arm order; browser version | quiet rule (load below 3.0); arm order randomised within seed and X5 (no order effect large enough to change a verdict); one Chrome version recorded | other machines; Chrome updates; display refresh rate |

## S8. Deviations, gaps and pending decisions

1. **DEC-011 (pending owner review).** The test reading (Holm over Wilcoxon p-values decides H0; the unadjusted 95% interval is reported beside it) and the S1 levels (rAF1 and Element Timing) were fixed before data by the AI. Both readings are shown where they differ.
2. **DEC-012.** Runs under `nice -n 10`; an inaccurate fixed sentence about other agents in the frozen generator output; TTFF part of S1 not computable; S1 alternative not chosen in EXP-001; Holm values inside the EXP-004 run folders are not frozen verdicts; two scratch log files overwritten outside the repository.
3. **EXP-001** ran twice on exploratory seeds; the pre-freeze run's values were seen before the freeze (freeze record, C4).
4. **M4 corrections to the experiment reports** (no verdict changed): EXP-004 shift ranges; EXP-003 BLANK wrong-state range, Event Timing share and failure-pair wording; EXP-002 minimum-excess wording and the interpretation of the 50 ms skeleton effect. Listed in `research/publication/evidence_audit.md`.
5. **Owner placeholders** (repository URL, funding, competing interests, author line) remain placeholders; see `progress.md`.
