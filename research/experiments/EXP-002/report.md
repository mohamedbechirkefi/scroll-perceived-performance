<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# EXP-002 report: Read path, BLANK versus SKELETON versus PREFETCH

## 1. Identification

| Field | Value |
|---|---|
| Experiment | EXP-002 (confirmatory) |
| Date of execution | 2026-11-25, 07:03:15Z to 08:08:02Z |
| Protocol | `research/experiments/EXP-002/protocol.md` v1.0, SHA-256 `3d263935e5ed7f97f673b0c4b2beb27ea3b3016184c6d58186655358c73b2f1d`; parent `research/protocol.md` v1.0, SHA-256 `a87ae45e049c16ed42abef0ab853a0e3fcf28daec9d5482d11bbb1dfb365f004` |
| Configuration | `experiments/EXP-002.json`, canonical hash `1040b20e1c79173c4393a2529af2f5abc8450c49bdba57beec0b0c7c7aacf752` |
| Code revision | `b5a72c32202cb66a17341a5022ad29e9344506b6` (clean). The run path is identical to the freeze revision `b4bd25b`; the only code difference is the analysis module `src/scroll/inference.py` (DEC-011), committed before any confirmatory output existed |
| Run | `EXP-002-20261125T070315Z` |
| Status | Complete. Full frozen matrix, no failed session, no failed cell |
| Authorship | Mohamed Bechir Kefi (no affiliation). An AI system was used as a research and development assistant; it is not an author |

## 2. Executive summary

- **Question.** When a user opens an item whose detail arrives after an injected delay L, does a skeleton placeholder or intent-based prefetching change the time to usable content (TTUC) compared with a blank region?
- **Method.** One mock page in the installed Google Chrome 158.0.8127.38 (headless, CPU 1x). The design covered 3 arms x 4 latency levels (50, 100, 300, 1000 ms) x 20 seeds x 10 interactions, which is 2,400 interactions. The trials were paired one to one within each seed. The analysis used the median over seeds, a 95% percentile bootstrap, and Wilcoxon signed-rank tests with Holm correction over 8 contrasts. SKELETON also had a TOST test with a 17 ms margin.
- **Outcome for PREFETCH.** TTUC fell at every latency level (Holm-adjusted p at most 0.00053). The reduction was close to the mechanical expectation of -min(h, L), within -10.5 to +15.1 ms.
- **Outcome for SKELETON, L = 100 to 1000 ms.** TTUC was equivalent to BLANK within 17 ms, with medians of -1.0 to 0.0 ms.
- **Outcome for SKELETON, L = 50 ms.** SKELETON reached usable content 16.7 ms earlier than BLANK (95% CI -17.1 to -16.0 ms; H0 rejected). Equivalence was not shown, because the 90% lower bound of -17.1 ms lies just beyond the margin.
- **Principal caveat.** The L = 50 ms SKELETON effect is about one display frame. Under both alternative paint-time methods it shrinks to -15.3 ms (rAF1) and -9.1 ms (Element Timing), and equivalence then holds (EXP-004, S1). It is therefore treated as a method-dependent, frame-scale effect, not a strategy benefit.

## 3. Rationale and literature

- **Skeleton.** A skeleton changes first feedback and, if it is sized correctly, avoids layout shift. Data cannot arrive earlier because of it. Sources: practitioner guidance NNG-SKEL and WEBDEV-OCLS, as listed in `research/literature_review.md`. MEJTOFT-18 was consulted as metadata only.
- **Prefetch.** Prefetching on hover starts the request a lead time h before the click, so the residual wait is max(0, d - h).
- **Gap.** The M0 search found no controlled objective comparison of these strategies against a blank baseline under identical seeded delays. That search was not systematic. No citation was re-verified in this session.

## 4. Hypotheses and operational definitions

- **TTUC** (ms, lower is better) is t_final minus t_in:
  - t_in is the click event's `timeStamp`.
  - t_final is `performance.now()` in the second `requestAnimationFrame` callback after the DOM commit that shows the requested detail, fully rendered and actionable.
- **Estimand** (amendment A1): Delta_s(L) is the median over seeds of [median over k of (TTUC_s,k - TTUC_BLANK,k)], for s in {SKELETON, PREFETCH} and L in {50, 100, 300, 1000} ms. This gives 8 primary contrasts.
- **Hypotheses:** H0 is Delta = 0; H1 is Delta != 0, two-sided, alpha 0.05, Holm over 8 contrasts.
- **SKELETON equivalence:** TOST with a 17 ms margin through the 90% bootstrap interval.
- **Disconfirmation of the expected pattern:**
  - SKELETON lies outside the equivalence margin, or
  - the PREFETCH estimate differs from -min(h, L) by more than 17 ms.
- **Fixed parameters:** h = 150 ms, jitter of plus or minus 10%, p = 0.
- **Test reading** (DEC-011, fixed before data): H0 is rejected when the Holm-adjusted Wilcoxon p is below 0.05. Whether the unadjusted 95% bootstrap interval excludes 0 is reported alongside; disagreements are flagged, not resolved.

## 5. Methodology

- **Page and harness.** A locally served mock page (`src/web/`), offline. It is driven by Playwright 1.65.0 through `channel = "chrome"` (amendment A5).
- **Input script.** The script is identical in every arm: pointer to a neutral point, two frames, a 50 ms pause, hover over the target, wait h = 150 ms, then a trusted click.
- **Session.** Each session is a fresh browser context with K = 10 interactions. The trial ends 1,000 ms (`settle_ms`) after the response and the last painted frame.
- **Schedule.** A seeded schedule (DEC-004, DEC-007 item 1) gives each trial k the same delay in every arm.
- **Arm order.** Arms are ordered within each seed block by a permutation seeded with meta-seed 20261124.
- **Seeds:** 1 to 20.
- **Hardware:**
  - Apple M1 Pro, 10 cores, 16 GiB, macOS 15.3.1, mains power.
  - The coordinator gave an exclusive window: no other lab agent was running.
  - Load average was 1.78/1.83/6.55 at the start and 2.07/1.67/1.71 at the end. The 15-minute value was still falling after the preceding SCALE runs.
  - The run executed under `nice -n 10`.
- **Software.** Python 3.12.1, numpy 2.5.4, scipy 1.18.1.
- **Budget.** 2 hours were allowed; 64.8 minutes were used.
- **Data.** Synthetic only (C1); no external data.

## 6. Implementation verification

- **Test suite before the run:** 171 passed at `7c8f7d1`, then 178 passed at `b5a72c3`, including 7 tests of the inference wiring on a deterministic fake harness with known effects.
- **Exploratory metric validation:** EXP-001 rerun on seeds 1001 to 1005 in the same window (journal J-0005).
  - C1: no BLANK trial below the injected delay.
  - C2: cell median excess over the reference model 12.0 to 27.0 ms.
  - C3 and C4 passed.
- **In this run:**
  - No BLANK trial had TTUC below its injected delay (0 of 796).
  - The excess over the reference lower bound was at least 3.1 ms in every cell (BLANK minima 3.9 to 6.4 ms; wording corrected in M4).
  - Prefetched responses were used in 100% of analysed PREFETCH trials.
  - The final displayed state was correct in 100% of trials.
  - No defect flag was raised.
- **Faithfulness:** the arms differ only in the strategy switch. The hover is performed in every arm, and only PREFETCH reacts to it.

## 7. Execution record

- **Command:** `PYTHONPATH=src nice -n 10 .venv/bin/python -m scroll run --config experiments/EXP-002.json`. It was started by a driver that first checked the DEC-011 quiet rule (result: quiet, 07:03:14Z).
- **Analysis:**
  - `python -m scroll report --run results/raw/EXP-002/EXP-002-20261125T070315Z --pdf`
  - `python -m scroll.inference primary --run results/raw/EXP-002/EXP-002-20261125T070315Z`
- **Samples:**
  - 240 of 240 sessions ok.
  - 2,400 trials, 2,387 analysed. The 13 exclusions all come from the hover-lead rule (A3: measured lead off by more than 25 ms), at most 2 of 200 per cell and arm.
  - No cell exceeded the 5% exclusion rule.
  - Trial pairs per contrast: 196 to 200.
- **Deviations from the frozen protocol:** none in design or analysis. Run conditions are recorded in DEC-012:
  - `nice -n 10`.
  - The generated `report.md` and the run manifest contain a fixed sentence saying other agents were running. That sentence is inaccurate for this exclusive window; the measured loads above apply.

## 8. Results

Primary contrasts. Unit: the seed (20 per contrast). Intervals: 95% percentile bootstrap over seeds, 10,000 resamples. p: two-sided Wilcoxon signed-rank, Holm over 8.

| L (ms) | Contrast | Median diff (ms) | 95% CI (ms) | Wilcoxon p | Holm p | TOST 90% CI (ms) | Verdict |
|---|---|---|---|---|---|---|---|
| 50 | PREFETCH - BLANK | -50.0 | [-51.2, -48.9] | 8.8e-05 | 0.00053 | | H0 rejected |
| 50 | SKELETON - BLANK | -16.7 | [-17.1, -16.0] | 8.8e-05 | 0.00053 | [-17.1, -16.1] | H0 rejected; equivalence not shown |
| 100 | PREFETCH - BLANK | -84.9 | [-86.3, -84.1] | 1.9e-06 | 1.5e-05 | | H0 rejected |
| 100 | SKELETON - BLANK | -0.6 | [-1.9, 0.1] | 0.0906 | 0.2719 | [-1.6, 0.0] | H0 not rejected; equivalent within 17 ms |
| 300 | PREFETCH - BLANK | -160.5 | [-163.5, -157.1] | 1.9e-06 | 1.5e-05 | | H0 rejected |
| 300 | SKELETON - BLANK | -1.0 | [-1.1, -0.4] | 0.0929 | 0.2719 | [-1.1, -0.6] | H0 not rejected; equivalent within 17 ms; the unadjusted 95% CI excludes 0 (readings disagree) |
| 1000 | PREFETCH - BLANK | -157.8 | [-159.1, -155.4] | 8.8e-05 | 0.00053 | | H0 rejected |
| 1000 | SKELETON - BLANK | 0.0 | [-0.9, 0.9] | 1.0000 | 1.0000 | [-0.7, 0.8] | H0 not rejected; equivalent within 17 ms |

PREFETCH mechanical check:

| L (ms) | Expected -min(h, L) | Observed | Deviation | Contradiction (more than 17 ms) |
|---|---|---|---|---|
| 50 | -50.0 | -50.0 | 0.0 | no |
| 100 | -100.0 | -84.9 | 15.1 | no |
| 300 | -150.0 | -160.5 | -10.5 | no |
| 1000 | -150.0 | -157.8 | -7.8 | no |

Descriptive cell summaries (trial level; medians):

| L | Arm | Trials analysed | TTUC (ms) | IQR (ms) | TTFF (ms) | Excess over model, median (ms) | Layout shift, all | CLS-eligible | Event Timing below 16 ms |
|---|---|---|---|---|---|---|---|---|---|
| 50 | BLANK | 200 | 77.2 | 75.2 to 79.9 | 77.2 | 27.2 | 0.035 | 0.000 | 71% |
| 50 | SKELETON | 200 | 60.9 | 59.2 to 63.7 | 27.5 | 10.9 | 0.035 | 0.000 | 20% |
| 50 | PREFETCH | 199 | 27.7 | 25.8 to 30.1 | 27.7 | 27.7 | 0.035 | 0.000 | 17% |
| 100 | BLANK | 198 | 112.4 | 109.8 to 125.3 | 112.4 | 16.3 | 0.035 | 0.000 | 71% |
| 100 | SKELETON | 198 | 112.3 | 109.2 to 124.3 | 28.0 | 15.7 | 0.035 | 0.000 | 23% |
| 100 | PREFETCH | 199 | 27.7 | 25.8 to 30.2 | 27.7 | 27.7 | 0.035 | 0.000 | 16% |
| 300 | BLANK | 200 | 323.8 | 295.6 to 331.9 | 323.8 | 15.6 | 0.035 | 0.000 | 74% |
| 300 | SKELETON | 199 | 314.9 | 296.4 to 328.1 | 27.9 | 14.4 | 0.035 | 0.000 | 19% |
| 300 | PREFETCH | 199 | 159.8 | 143.2 to 176.7 | 159.8 | 14.9 | 0.035 | 0.000 | 76% |
| 1000 | BLANK | 198 | 1029.3 | 960.3 to 1075.2 | 1029.3 | 14.5 | 0.035 | 0.035 | 79% |
| 1000 | SKELETON | 199 | 1026.6 | 958.4 to 1073.6 | 27.9 | 13.7 | 0.035 | 0.000 | 19% |
| 1000 | PREFETCH | 198 | 867.7 | 808.9 to 915.3 | 867.7 | 15.4 | 0.035 | 0.035 | 76% |

- **Seed spread** (SD of per-seed paired differences): 1.6 to 4.5 ms for every contrast.
- **Secondary draft estimand** (difference of per-seed session medians, descriptive): same signs and similar sizes, for example SKELETON at L = 50 ms -15.9 ms [-17.2, -15.4]. Full table in `paired_contrasts.csv`.
- **Event Timing** is descriptive only (A4); its median input-to-handler time was 0.3 ms in every cell.
- **Runtime:** 3,887.4 s for 2,400 interactions. Peak Python RSS was 78 MiB; Chrome memory was not recorded.
- **Figures** (generated from `results.json` by `python -m scroll report`):
  - `results/raw/EXP-002/EXP-002-20261125T070315Z/report/figures/fig-ttuc.png` (TTUC per trial by cell and arm, log scale)
  - `fig-paired.png` (per-seed paired differences with 95% intervals)
  - `fig-excess.png` (excess over the reference model)

## 9. Interpretation

- **Measured: PREFETCH.**
  - PREFETCH removes almost exactly the scripted lead from the wait (deviation within 17 ms at every L).
  - At L of 50 and 100 ms, h exceeds the maximum delay, so the residual wait is zero by construction. TTUC then equals the rendering cost of about 28 ms. The observed -84.9 ms at L = 100 ms differs from -100 ms because BLANK's own overhead at that level (16.3 ms median excess) is smaller than PREFETCH's 27.7 ms.
  - This result checks the instrumentation as much as the strategy, as the protocol anticipated.
- **Measured: SKELETON, L of 100 ms and above.** SKELETON does not change TTUC by more than a fraction of a frame. It lowers TTFF from roughly the full delay to about 28 ms: placeholders change first feedback, not usable content. This is the pattern the main interpretation predicts.
- **Measured: SKELETON, L = 50 ms.** SKELETON reaches content 16.7 ms earlier than BLANK.
- **Model-dependent explanation, not tested.** At such short delays BLANK pays a larger frame-scheduling cost: BLANK's median excess over the reference model is 27.2 ms at L = 50 ms against 10.9 ms for SKELETON. The skeleton's commit at input appears to keep the renderer's frame loop active, so the content commit lands in an earlier frame.
- **Measurement dependence.** EXP-004 (S1) shows that the alternative paint methods shrink the effect to -15.3 ms (rAF1) and -9.1 ms (Element Timing), and equivalence holds under both. The effect is of frame scale, about one frame, and its size depends on how paint time is measured. The direction is the same under all three methods, so the data do not show that it is absent; they show that it is not robust and do not establish a skeleton benefit. The M4 exploratory decomposition (`results/exploratory/M4-REANALYSIS/x2_frame_decomposition.csv`) locates it in frame alignment: the second-frame gap was the same in both arms, and the frame carrying the content had already started at the commit in 83% of SKELETON trials against 1% of BLANK trials. (Revised in M4 review pass 2; the M3 text called it an artefact and said it was not evidence that skeletons deliver content sooner.)
- **Expected-pattern contradiction.** Under the frozen wording ("SKELETON outside the equivalence margin"), the point estimate lies inside the margin but the TOST fails. The result is therefore reported as "equivalence not shown, method-dependent", not as a confirmed contradiction.
- **Test readings.** For SKELETON at L = 300 ms, the unadjusted 95% interval excludes 0 (-1.1 to -0.4 ms) while the Holm-adjusted Wilcoxon test does not reject. The difference is about one millisecond and lies well inside the equivalence margin; neither reading changes the equivalence verdict.
- **Non-significance is not equivalence.** Equivalence is claimed only where the TOST shows it.

## 10. Threats to validity

- **Internal:**
  - Arm order was randomised within seed blocks, and delays were common across arms.
  - Hover-lead jitter is controlled by the A3 exclusion (13 trials).
  - Background processes (editor, system services) remained, at a load average of about 2.
- **Construct:**
  - TTUC depends on the in-page frame marker. Frame quantisation (about 8 to 17 ms) is of the same order as the SKELETON effect at L = 50 ms (see S1).
  - Event Timing is mostly unobservable (below the 16 ms threshold in 71 to 79% of BLANK trials).
- **External:**
  - One synthetic page, one browser version (Chrome 158.0.8127.38) and one laptop, headless.
  - Prefetch benefit is bounded by a scripted lead and does not represent real hover behaviour.
  - BLANK's empty region collapses (DEC-007 item 3), so layout-shift differences are a design consequence.
- **Statistical:**
  - 20 seeds per contrast; the seed is the unit.
  - Holm controls the family-wise error over 8 tests. TOST is unadjusted, as frozen.
  - The test reading (DEC-011) was fixed before data.

## 11. Conclusion and next experiment

- **Answer to the registered question,** in this setting:
  - Intent prefetching with a 150 ms lead reduced time to usable content by about min(h, L), and the reduction was statistically clear at every delay.
  - A skeleton placeholder did not change time to usable content by more than 17 ms at delays of 100 ms or more.
  - At 50 ms the skeleton condition was about one frame faster, an effect that depends on the paint-time method.
- **Scope.** No statement about perceived speed is made.
- **Follow-up:**
  - Record alternative paint times for the first-feedback frame, so TTFF sensitivity can be computed.
  - Study frame-loop state (idle versus active renderer) as an explicit factor at delays below 100 ms, under a new owner-approved protocol.

## 12. Reproduction appendix

- **Dependencies:** `uv.lock` (uv sync --frozen --all-groups --all-extras); Python 3.12.1; Playwright 1.65.0; installed Google Chrome 158.0.8127.38.
- **Data manifest:** synthetic schedule only (`data/manifest.json`).
- **Clean run:**
  - `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`
  - `.venv/bin/python -m pytest`
  - `PYTHONPATH=src .venv/bin/python -m scroll run --config experiments/EXP-002.json`
  - `PYTHONPATH=src .venv/bin/python -m scroll report --run <run dir> --pdf`
  - `PYTHONPATH=src .venv/bin/python -m scroll.inference primary --run <run dir>`
- **Raw results:** `results/raw/EXP-002/EXP-002-20261125T070315Z/results.json`, SHA-256 `0ca46a419b9d00b1b262f0b3f72cd4aeb342070dbb317dd8f36b89016886fce3`, schema `src/scroll/schemas/result-1.0.0.json`. Checksums of every output: `results/raw/EXP-002/manifest_sha256.json`.
- **Machine-readable outputs:** `report/inference.json` and `inference.csv` (verdicts), `trial_paired_contrasts.csv`, `paired_contrasts.csv`, `cell_summary.csv`, `metrics.csv`, `analysis.json`, `run_manifest.json`.
- **Tolerance on rerun:** timing values vary with machine state and Chrome version; the schedule and pairing are bit-identical by seed.
- **Records:** journal J-0006; decisions DEC-011 and DEC-012; claims C-001 to C-008.
