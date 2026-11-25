<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# EXP-003 report: Write path, BLANK (pessimistic) versus OPTIMISTIC with failure injection

## 1. Identification

| Field | Value |
|---|---|
| Experiment | EXP-003 (confirmatory) |
| Date of execution | 2026-11-25, 08:08:38Z to 09:53:57Z |
| Protocol | `research/experiments/EXP-003/protocol.md` v1.0, SHA-256 `2667ba2f078ba5eeccdcecf05a38cf8b8553343ff4d1ec2c5e75cdd1bcda151c`; parent `research/protocol.md` v1.0, SHA-256 `a87ae45e049c16ed42abef0ab853a0e3fcf28daec9d5482d11bbb1dfb365f004` |
| Configuration | `experiments/EXP-003.json`, canonical hash `11ad05387d0a71c879db8bcab4ced8f19b401aba46b988ee696bb3c4c0ddd58c` |
| Code revision | `b5a72c32202cb66a17341a5022ad29e9344506b6` (clean; run path identical to freeze revision `b4bd25b`) |
| Run | `EXP-003-20261125T080838Z` |
| Status | Complete. Full frozen matrix, no exclusion, stop rule not triggered |
| Authorship | Mohamed Bechir Kefi (no affiliation). An AI system was used as a research and development assistant; it is not an author |

## 2. Executive summary

- **Question.** When a save can fail with probability p after a delay L, how does an optimistic update change the time to the final correct state, and how much wrong-state exposure does it create?
- **Method.** 2 arms x L {100, 300, 1000} ms x p {0, 0.1, 0.3} x 20 seeds x 10 interactions, which is 3,600 interactions. Trials were paired within each seed. Success and failure strata were analysed separately at p > 0 (A2). Wilcoxon tests used Holm correction over 15 primary contrasts.
- **Successful saves.** OPTIMISTIC reached the final state sooner than BLANK by about the delay:
  - -85.2 to -85.3 ms at L = 100 ms;
  - -288.5 to -290.4 ms at L = 300 ms;
  - -990.7 to -998.6 ms at L = 1000 ms.
  
  H0 was rejected in all 9 cells.
- **Failed saves.** There was no detectable difference: medians were -1.6 to 2.7 ms and H0 was not rejected in any of the 6 cells. On those saves OPTIMISTIC showed a false state for about the whole delay (median 83.4, 283.9 and 999.1 ms).
- **Mixed estimand** (secondary): its magnitude shrank as p rose at every L, as expected.
- **Rollback** was correct in 3,600 of 3,600 trials.
- **Principal caveat.** The failure stratum has 12 seeds at p = 0.1 and 18 at p = 0.3. "Not rejected" is not shown equivalence.

## 3. Rationale and literature

- **Mechanism.** An optimistic update shows the expected state at input and rolls back on failure (REACT-OPT semantics, `research/literature_review.md`). On success it is final after about one frame. On failure it becomes final only when the failure is known, having displayed a wrong state for about the delay.
- **Gap.** No controlled objective measurement of this trade-off under seeded failure was found in the M0 search, which was not systematic. Citations were not re-verified in this session.

## 4. Hypotheses and operational definitions

- **TTUC, write path:**
  - On success: the first frame showing the new state.
  - On failure: the first frame showing the old state together with the error message, after the failure is known.
- **Estimand** (A1, A2): Delta(L, p, o) is the median over seeds of the per-seed median of trial-paired differences (OPTIMISTIC minus BLANK) within outcome stratum o.
- **Primary family:** 3 contrasts at p = 0 (success) plus 12 at p > 0 (success and failure at 2 levels of p and 3 of L), giving 15. Holm at alpha 0.05 over Wilcoxon p-values (DEC-011 reading).
- **Secondary measures:**
  - the mixed estimand over all trials of a cell;
  - the draft seed-median estimand;
  - wrong-state exposure: ms after input during which the displayed toggle differs from the final server state, split into stale and false state (DEC-007 item 4).
- **Contradiction of the expected pattern:**
  - the mixed estimand does not strictly decrease in magnitude as p rises (DEC-011 item 4), or
  - rollback correctness is below 1.0.

## 5. Methodology

- **Setup.** Same page, harness, browser (Chrome 158.0.8127.38, headless, CPU 1x), input script and machine as EXP-002.
- **Failure schedule.** The seeded failure schedule gives trial k the same delay and outcome in both arms.
- **Seeds:** 1 to 20. Seeds contributing to the failure stratum are fixed by the schedule: 12 at p = 0.1 and 18 at p = 0.3.
- **Machine conditions:**
  - Exclusive window.
  - Load 2.36/1.77/1.74 at the start and 1.45/1.44/1.52 at the end.
  - Mains power.
  - `nice -n 10`.
- **Budget.** 3 hours were allowed; 105.3 minutes were used.
- **Data.** Synthetic only.

## 6. Implementation verification

- **Tests:** 178 passed at `b5a72c3` before the run.
- **Exploratory check:** EXP-001 rerun (J-0005) gave rollback correct in 200 of 200 write trials.
- **In this run:**
  - The final displayed state equalled the server state, with the error message present exactly on failures, in 3,600 of 3,600 trials.
  - No BLANK trial reached usable content before the injected delay (0 of 1,800).
  - No defect flag was raised.
  - The outcome mismatch count between paired arms was 0 (common random numbers held).
- **Accessibility assertions** (protocol section 8; live-region announcement and focus): passed in 180 of 180 sessions per arm. Focus stayed on the toggle in 1,800 of 1,800 trials per arm.

## 7. Execution record

- **Command:** `PYTHONPATH=src nice -n 10 .venv/bin/python -m scroll run --config experiments/EXP-003.json`, after the quiet check (quiet, 08:08:38Z).
- **Analysis:** `scroll report --pdf` and `scroll.inference primary` on `results/raw/EXP-003/EXP-003-20261125T080838Z`.
- **Samples:**
  - 360 of 360 sessions ok.
  - 3,600 of 3,600 trials analysed.
  - Trial pairs per primary contrast: 200 (p = 0), 174 and 26 (p = 0.1, success and failure), 143 and 57 (p = 0.3).
- **Deviations from the frozen protocol:** none. Run conditions are as in DEC-012 (`nice`, the inaccurate fixed "other agents" sentence in the generated report and manifest).

## 8. Results

Primary contrasts (OPTIMISTIC minus BLANK). 95% percentile bootstrap over seeds; Wilcoxon two-sided; Holm over 15.

| L (ms) | p | Stratum | Seeds | Median diff (ms) | 95% CI (ms) | Wilcoxon p | Holm p | Verdict |
|---|---|---|---|---|---|---|---|---|
| 100 | 0 | success | 20 | -85.2 | [-88.0, -84.3] | 8.8e-05 | 0.00079 | H0 rejected |
| 100 | 0.1 | success | 20 | -85.3 | [-86.6, -84.8] | 1.9e-06 | 2.9e-05 | H0 rejected |
| 100 | 0.1 | failure | 12 | 0.5 | [-1.5, 1.7] | 0.9097 | 1.0000 | H0 not rejected |
| 100 | 0.3 | success | 20 | -85.3 | [-88.0, -83.9] | 8.8e-05 | 0.00079 | H0 rejected |
| 100 | 0.3 | failure | 18 | 2.7 | [-1.0, 5.4] | 0.0611 | 0.3665 | H0 not rejected |
| 300 | 0 | success | 20 | -288.5 | [-297.7, -282.3] | 8.8e-05 | 0.00079 | H0 rejected |
| 300 | 0.1 | success | 20 | -289.3 | [-297.6, -283.5] | 1.9e-06 | 2.9e-05 | H0 rejected |
| 300 | 0.1 | failure | 12 | -0.8 | [-3.0, 4.3] | 0.8501 | 1.0000 | H0 not rejected |
| 300 | 0.3 | success | 20 | -290.4 | [-297.4, -284.1] | 1.9e-06 | 2.9e-05 | H0 rejected |
| 300 | 0.3 | failure | 18 | -0.1 | [-2.6, 1.5] | 0.8960 | 1.0000 | H0 not rejected |
| 1000 | 0 | success | 20 | -998.6 | [-1012.2, -972.6] | 1.9e-06 | 2.9e-05 | H0 rejected |
| 1000 | 0.1 | success | 20 | -995.9 | [-1015.8, -967.3] | 1.9e-06 | 2.9e-05 | H0 rejected |
| 1000 | 0.1 | failure | 12 | -1.6 | [-7.1, 0.1] | 0.0923 | 0.4614 | H0 not rejected |
| 1000 | 0.3 | success | 20 | -990.7 | [-1016.6, -961.7] | 1.9e-06 | 2.9e-05 | H0 rejected |
| 1000 | 0.3 | failure | 18 | 0.6 | [-1.4, 3.4] | 0.3490 | 1.0000 | H0 not rejected |

Secondary mixed estimand (all trials of a cell; descriptive) and the frozen trend check:

| L (ms) | p = 0 | p = 0.1 | p = 0.3 | Magnitude strictly decreasing |
|---|---|---|---|---|
| 100 | -85.2 | -84.0 [-85.3, -82.6] | -81.8 [-84.2, -81.1] | yes |
| 300 | -288.5 | -283.8 [-288.9, -281.5] | -274.6 [-281.3, -270.9] | yes |
| 1000 | -998.6 | -974.1 [-998.1, -956.4] | -951.5 [-967.8, -929.2] | yes |

Wrong-state exposure in failure trials (83 failure trials per L and arm, all seeds; medians, ms):

| L | Arm | False state | Stale state | Wrong state total | Injected delay |
|---|---|---|---|---|---|
| 100 | BLANK | 0.0 | 0.0 | 0.0 | 101.0 |
| 100 | OPTIMISTIC | 83.4 | 0.0 | 83.4 | 101.0 |
| 300 | BLANK | 0.0 | 0.0 | 0.0 | 304.0 |
| 300 | OPTIMISTIC | 283.9 | 0.0 | 283.9 | 304.0 |
| 1000 | BLANK | 0.0 | 0.0 | 0.0 | 1014.0 |
| 1000 | OPTIMISTIC | 999.1 | 0.0 | 999.1 | 1014.0 |

- **Successful saves.** BLANK's wrong-state exposure is stale-state waiting of about the delay (cell medians 110.1 to 1024.5 ms over all trials; corrected in M4, the M3 text said 111.6), whereas OPTIMISTIC is about 27 to 30 ms.
- **Cell medians of TTUC:**
  - BLANK: 111.6 to 112.3 ms at L = 100, 312.1 to 313.1 ms at L = 300, 1024.4 to 1024.8 ms at L = 1000.
  - OPTIMISTIC: 27.0 to 29.7 ms.
  - With failures (p = 0.3), OPTIMISTIC's upper quartile rises to 108.0, 293.1 and 943.7 ms.
- **Layout shift:** 0 in every cell.
- **Event Timing** (descriptive, A4): below threshold in 62.5 to 75.5% of BLANK trials.
- **Runtime:** 6,318.7 s; peak Python RSS 78 MiB.
- **Figures:** `results/raw/EXP-003/EXP-003-20261125T080838Z/report/figures/fig-ttuc.png`, `fig-paired.png` and `fig-excess.png`, generated from `results.json`.

## 9. Interpretation

- **Measured: success.** On success, the optimistic update makes the final state visible about one delay earlier. The benefit equals the delay minus a rendering cost of about 27 ms, as the mechanism predicts.
- **Measured: failure.**
  - On failure, both arms reach the final correct state (old state plus error) at the same time, within a few milliseconds and with no detectable difference.
  - OPTIMISTIC displays a state the server never held for about the whole delay; BLANK displays no false state.
  - The trade-off is therefore not a TTUC penalty on failure, but false-state exposure.
- **Measured: mixed estimand.** The advantage falls with p, as the share of failure trials (which carry no advantage) rises. No contradiction under the frozen rule.
- **Model-dependent.** The size of the mixed advantage at other p values follows from the strata by mixture. It was not measured beyond p = 0.3.
- **Failure-stratum nulls.** These are not equivalence claims: no equivalence test was registered for them, and the intervals reach up to -7.1 ms and +5.4 ms.

## 10. Threats to validity

- **Internal:** as in EXP-002. Paired outcomes matched in every trial.
- **Construct:**
  - "Final correct state" on failure requires the error message. A different failure presentation would change TTUC.
  - Wrong-state exposure counts BLANK's waiting as stale state (DEC-007 item 4).
- **External:**
  - One mock toggle; failures are uniform Bernoulli with fixed delay, so no retries or timeouts are modelled.
  - One browser version and one machine.
- **Statistical:**
  - The failure strata have 12 or 18 seeds and few trials per seed (26 trial pairs per cell at p = 0.1 and 57 at p = 0.3), so their intervals are wider.
  - Holm over 15; the DEC-011 test reading.

## 11. Conclusion and next experiment

- **Answer to the registered question,** in this setting:
  - An optimistic update reached the final state about one delay earlier on every successful save (H0 rejected in all 9 success cells).
  - It did not change the time to the final state on failed saves (H0 not rejected in all 6 failure cells), but showed a false state for about the delay on those saves.
  - The mixed advantage decreases as the failure probability rises.
- **Scope.** No perception claim is made.
- **Follow-up:**
  - An equivalence test for the failure stratum.
  - Failure modes with retries and timeouts.
  - A human study (out of scope) on how false-state exposure is perceived.

## 12. Reproduction appendix

- **Dependencies, environment and commands:** as in EXP-002, with `--config experiments/EXP-003.json`.
- **Raw results:** `results/raw/EXP-003/EXP-003-20261125T080838Z/results.json`, SHA-256 `9bf70c80b0066dcba545dee718b13e886c3fd850fa9d49c9718801db2f474fe6`. Checksums: `results/raw/EXP-003/manifest_sha256.json`.
- **Verdicts:** `report/inference.json` (including `mixed_trend` and `stop_rule`) and `inference.csv`.
- **Other outputs:** `trial_paired_contrasts.csv` (includes the mixed rows), `paired_contrasts.csv`, `cell_summary.csv`, `metrics.csv`.
- **Failure-trial exposure table:** computed from `results.json` with a short one-off command over the `false_state_ms`, `stale_state_ms` and `wrong_state_ms` fields of trials with `request_ok = false`. It is not produced by the report generator; M4 should add it to the generator.
- **Records:** journal J-0007; DEC-011, DEC-012; claims C-009 to C-023 and C-029.
