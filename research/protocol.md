<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# SCROLL research protocol

**Status: FROZEN v1.0 (owner-approved 2026-11-24, gate G-FREEZE).** This version is draft v0.1 plus the owner-approved amendments of section 11. Its SHA-256, the SHA-256 of every confirmatory experiment protocol and of every confirmatory configuration, and the code revision are recorded in `research/freeze.json` (a file cannot contain its own hash); the experiment hashes are also in `research/experiment_registry.csv`. The runner refuses any confirmatory run whose protocol or configuration differs from the frozen one. Every result obtained before the freeze (EXP-001, seeds 1001 to 1005) is exploratory. Any change after this point is a dated deviation reported separately from the frozen analysis.

## 1. Research question

How do loading strategies affect measurable interface responsiveness under controlled delays? (`master_prompt.md`, section 10.)

Operational version: in one locally served mock interface, with an identical seeded latency and failure schedule, how does each loading strategy change the time from a user input to the first frame that shows the requested content in its final, correct, usable state, compared with a blank baseline?

Claims boundary: objective timing is not perceived speed. No statement about human perception is made without a human study, which is out of scope.

## 2. System under test

One mock interface ("catalogue" page: a list of items and an item detail panel), implemented once, with the loading strategy as the only switch. Two interaction paths:

- **Read path (open item):** a click on a list item requests the item's detail from the mock transport.
- **Write path (save item):** a click on a "save" toggle sends a mutation to the mock transport, which may fail.

Arms (strategies):

| Arm | Read path | Write path |
|---|---|---|
| `BLANK` (baseline) | The detail region stays empty until the response arrives, then renders. | The toggle shows its old state until the server confirms; on failure an error message appears. |
| `SKELETON` | A placeholder with the final layout box size renders on input; content replaces it on response. | Not applicable. |
| `PREFETCH` | The detail request starts on a scripted pointer-hover intent signal, a fixed lead time `h` before the click; a cached response renders on click. | Not applicable. |
| `OPTIMISTIC` | Not applicable. | The toggle shows the new state on input; on failure it rolls back to the old state and shows an error message. |

The baseline is `BLANK` in both paths: the simplest strategy, showing nothing new until the server answers.

Browser: the installed Google Chrome, driven through Playwright with `channel="chrome"` (DEC-005 option b, amendment A5). Chrome updates itself, so its version is recorded in every run manifest and reported with every result; a version change between or within experiments is reported.

Latency and failure injection: a seeded mock transport (DEC-004) maps `(seed, request index)` to a delay `d = L x (1 + j)`, with `j` drawn uniformly in [-0.1, 0.1], and to an outcome (success, or failure with probability `p`). The same seed yields the same schedule in every arm (common random numbers).

## 3. Metrics

Notation: `t_in` is the input event's `timeStamp` (ms, `performance.now()` clock). A "paint" time is estimated by the instrumented frame marker (section 3.3).

### 3.1 Primary metric: time to usable content (TTUC), ms, lower is better

`TTUC = t_final - t_in`, where `t_final` is the time of the first frame from which the displayed state of the target region equals the final server-consistent state, is fully rendered (no placeholder) and is actionable, and stays so until the trial ends.

- Read path: the frame in which the requested detail content is rendered.
- Write path, success: the frame showing the new state (for `OPTIMISTIC` this is the first frame after input; for `BLANK` it is the frame after the confirmation).
- Write path, failure: the frame showing the rolled-back or unchanged old state together with the error message, after the failure is known.

Justification for a single primary metric: TTUC is the only candidate outcome that is defined for every arm in both paths and that directly operationalises "usable content". Time to first feedback rewards any visual change, including placeholders and possibly wrong optimistic states, which is exactly the confusion the project examines ("faster-feeling is not always faster"). It is therefore a secondary metric.

### 3.2 Secondary metrics

1. **Time to first feedback (TTFF)**, ms: `t_in` to the first frame with any visible change in the target region (placeholder, optimistic state or content).
2. **Interaction duration (Event Timing)**, ms: the `duration` of the `PerformanceEventTiming` entry for the click (8 ms granularity, observer threshold 16 ms; entries under 16 ms are recorded as "below threshold", not as zero). Descriptive only (amendment A4): it is reported with its below-threshold share, together with `input_to_handler_ms` (handler start minus input time), and no contrast, test or verdict is based on either.
3. **Layout shift during the trial**: sum of `LayoutShift.value` from input to `t_final + 1000 ms`, reported twice: all entries, and entries with `hadRecentInput = false` (the CLS-eligible ones).
4. **Wrong-state exposure (write path)**, ms: total time the displayed state differed from the final server-consistent state after input.
5. **Rollback correctness (write path)**: share of trials whose final displayed state equals the server state (must be 1.0; anything else is a defect).
6. **Prefetch waste (read path, `PREFETCH`)**: share of prefetched responses never used, under scripted hover-without-click events.
7. **Run resources**: wall-clock per trial, browser version, CPU throttle setting.

### 3.3 Frame-time estimation

Primary method: the application records a mark when it commits the DOM change, then the time of the next frame through a double `requestAnimationFrame` callback. Alternative method for sensitivity: Chromium Element Timing on the content element, or a performance trace (to be chosen in EXP-001). The disagreement between methods is itself reported.

## 4. Hypotheses

For each non-baseline arm `s` and latency level `L`, the estimand is the trial-paired difference (amendment A1)

`Delta_s(L) = median over seeds of [ median over k of ( TTUC_s,k - TTUC_BLANK,k ) ]`,

where trial `k` of arm `s` and trial `k` of `BLANK` in the same seed and cell share the same scheduled delay and outcome (common random numbers). Only interactions analysed in both arms form a pair. The seed remains the independent unit. On the write path with `p > 0` the estimand is computed separately for success trials and for failure trials (amendment A2): both strata are primary contrasts, and the mixed estimand over all trials is secondary. The draft estimand (difference of per-seed session medians) is reported as a secondary, descriptive analysis.

- **H0 (primary, per contrast):** `Delta_s(L) = 0`.
- **H1 (two-sided):** `Delta_s(L) != 0`.

Pre-stated directional expectations (stated before data, not used to choose tests):

- `SKELETON`: no TTUC benefit; `|Delta| < 17 ms` (one 60 Hz frame), tested by two one-sided tests (TOST) with margin 17 ms. Lower TTFF than `BLANK`.
- `PREFETCH`: `Delta` close to `-min(h, L)` (mechanical expectation). The test checks the instrumentation as much as the strategy.
- `OPTIMISTIC`: large negative `Delta` when `p = 0`; the advantage shrinks as `p` rises, while wrong-state exposure grows.

What would contradict the main interpretation ("strategies that change first feedback do not necessarily change time to usable content"): a `SKELETON` TTUC difference outside the equivalence margin in either direction, or a reversal of any contrast under the sensitivity conditions in section 8.

## 5. Design

- **Experimental unit:** one browser session (fresh browser context, fresh page) per (arm, condition, seed), running K = 10 scripted interactions of one path.
- **Independent unit for inference:** the seed. Interactions within a session are correlated (same page, warm caches) and are summarised by their median before inference.
- **Seeds:** 20 per stochastic cell (minimum 5 required by the master prompt; confirmed by the owner, amendment A6). Seeds `1..20` for confirmatory runs; seeds `1001..1005` reserved for smoke and exploratory runs, never reused confirmatorily.
- **Matching:** the same seed gives the same latency and failure schedule in every arm. Arm order within each seed block is randomised with a fixed meta-seed and recorded.
- **Conditions:** latency `L` in {50, 100, 300, 1000} ms (read) and {100, 300, 1000} ms (write); failure probability `p` in {0, 0.1, 0.3} (write); prefetch lead time `h = 150 ms` (main), {0, 600} ms in sensitivity; CPU throttle 1x (main), 4x in sensitivity.

### 5.1 Sample-size rationale (to be confirmed by EXP-001)

The latency schedule is deterministic given the seed, so variance comes from browser scheduling and frame quantisation. For a paired comparison with standard deviation of differences `sigma_d` and smallest effect of interest `delta = 17 ms`, `n = ((z_0.975 + z_0.80) x sigma_d / delta)^2`. With an assumed `sigma_d = 20 ms` (planning assumption, not measured), `n` is about 11. Twenty seeds give margin. EXP-001 will measure `sigma_d`; if it exceeds 28 ms, the owner is asked before freezing whether to raise the seed count (cost estimate in section 9).

## 6. Uncertainty and inference

- Per contrast: point estimate = median of paired per-seed differences; 95% percentile bootstrap interval over seeds (10,000 resamples, fixed bootstrap seed); Wilcoxon signed-rank test as a secondary check.
- Multiplicity: Holm correction across the primary contrasts within each experiment.
- Equivalence (`SKELETON` only): TOST with margin 17 ms at alpha 0.05, using the bootstrap interval at 90%.
- Raw distributions (all interactions, all seeds) are plotted for every cell.
- Non-significance is never reported as equivalence.

## 7. Exclusion and stopping rules

- A trial is excluded only for harness failure: browser crash, missing instrumentation mark, or no `t_final` within `L + 10 s`. Every exclusion is logged with its reason and reported.
- Hover-lead control (amendment A3): on the read path, in every arm, a trial is excluded when the measured hover-to-click lead (`t_in - t_hover`, page clock) deviates from the scheduled lead `h` by more than 25 ms, or when no hover was recorded. The trial's values are kept in the raw record with the reason. With trial-level pairing, the same interaction index then drops out of the contrast. These exclusions count toward the 5% rule below and are reported per cell. The write path is not affected: no write arm reacts to the hover and the lead is not recorded there.
- If more than 5% of trials in a cell are excluded, the cell is reported as failed; it is not rerun silently. Any rerun is a dated deviation.
- Fixed sample size, no optional stopping, no interim look at confirmatory contrasts.
- Stop rule: if rollback correctness is below 1.0 or `BLANK` TTUC is below the injected delay (impossible if the instrumentation is right), the campaign stops, the defect is recorded, and all affected runs are discarded and rerun after the fix as a recorded deviation.

## 8. Sensitivity analyses (EXP-004)

1. **Measurement method** (could invalidate the main interpretation): recompute TTUC and TTFF with the alternative frame-time method. If the sign or equivalence verdict of any primary contrast changes, the main interpretation is reported as method-dependent.
2. **CPU throttling 4x**: skeleton rendering and rollback costs may become visible only under CPU load.
3. **Prefetch lead time** `h` in {0, 600} ms.
4. **Headless versus headed browser** on a reduced matrix, because frame scheduling may differ.

## 9. Matrices and budget

| Experiment | Matrix | Interactions | Planning wall-clock (unmeasured estimate) |
|---|---|---|---|
| EXP-001 smoke | read: 3 arms x L {100, 1000} x 5 seeds x 5 interactions; write: 2 arms x L {100, 1000} x p {0, 0.5} x 5 seeds x 5 interactions | 150 + 200 = 350 | about 15 min |
| EXP-002 read | 3 arms x 4 L x 20 seeds x 10 | 2,400 | about 1 h |
| EXP-003 write | 2 arms x 3 L x 3 p x 20 seeds x 10 | 3,600 | about 1.5 h |
| EXP-004 sensitivity | reduced: L {300, 1000}, 10 seeds, conditions of section 8 | about 2,000 | about 1 h |

Budget: local machine only, zero cost. If wall-clock exceeds twice the estimate in EXP-001, the matrices shrink (fewer latency levels first, never fewer than 10 seeds) before the freeze.

## 10. Feasibility audit (M0, 2026-11-24)

Commands and outputs are recorded verbatim in `progress.md`.

| Item | Measured |
|---|---|
| CPU | Apple M1 Pro, 10 cores (8 performance, 2 efficiency) |
| RAM | 17,179,869,184 bytes (16 GiB) |
| OS | macOS 15.3.1 (build 24D70) |
| Free disk | 129 GiB on the data volume (`df -h`) |
| Python | 3.12.1 at `/usr/local/bin/python3` |
| uv | 0.9.5 (`/Users/bechir/research/labs/.tools/py/bin/uv`) |
| typst (Python package) | 0.15.0; pypdf 6.20.0; pillow 11.3.0 |
| pandoc | 3.6.3 (`/Users/bechir/research/labs/.tools/pandoc`) |
| Node | v22.23.3 (`/Users/bechir/research/helix/.tools/node/bin`, read-only). Its `npm` fails unless that folder is first on `PATH`, because an older Node (v15.14.0 through nvm) is found first; with `PATH` prefixed, npm 10.9.9 runs. |
| git | 2.42.1 |
| TeX | none (`tex`, `pdflatex`, `xelatex`, `tectonic` not found) |
| Browsers | Google Chrome 158.0.8127.38 and Safari installed; Playwright browsers not installed |

Toolchain decision (DEC-002): pandoc to Typst, compiled with the typst Python package; `manuscript.tex` generated by pandoc as source only.

Risks:

1. **Display and frame rate.** The M1 Pro built-in display may run at up to 120 Hz; headless Chromium frame scheduling is not tied to a display. Frame quantisation differs between modes; covered by sensitivity 4.
2. **Event Timing floor.** Durations under 16 ms are not observable through `PerformanceObserver`, and all durations are rounded to 8 ms. TTFF uses the custom frame marker instead.
3. **Timer and scheduler noise.** The mock transport uses timers on the main thread; background load on the laptop adds noise. Runs are done on mains power with other heavy jobs stopped, and the load average is recorded.
4. **Browser version drift.** See DEC-005.
5. **Single machine, single browser engine.** External validity is limited to Chromium on this laptop.

## 11. Amendments before freeze (owner-approved 2026-11-24)

The owner approved the following amendments on 2026-11-24, in answer to DEC-008 and DEC-005 (`research/decision_log.md`, DEC-009). They were proposed after the exploratory EXP-001 run (`results/exploratory/EXP-001/EXP-001-20261124T161058Z/`). No value below was tuned on the primary contrast.

| ID | Approved wording | Change in this protocol | Source |
|---|---|---|---|
| A1 | "Pair trials one to one within each seed." | Section 4: trial-level pairing within seed and cell; the draft seed-median estimand becomes secondary. | DEC-008 A1 |
| A2 | "Split the p > 0 write path by outcome." | Section 4 and EXP-003: success and failure strata are primary at `p > 0`; the mixed estimand is secondary. | DEC-008 A2 |
| A3 | "Control the hover-to-click lead." | Section 7: pre-specified exclusion when the measured lead deviates from `h` by more than 25 ms (the tolerance stated in DEC-008 A3). The click stays a trusted Playwright input; the in-page timer alternative of DEC-008 A3 was not adopted because a script-dispatched click would change `t_in` and remove the Event Timing entry. | DEC-008 A3 |
| A4 | "Event Timing is descriptive only." | Section 3.2 item 2. | DEC-008 A4 |
| A5 | "Use the installed Google Chrome, with its version recorded." | Section 2; DEC-005 resolved as option (b). Confirmatory configs must use `channel = "chrome"`. | DEC-005 |
| A6 | "20 seeds." | Section 5: seeds 1 to 20 confirmed for EXP-002 and EXP-003. EXP-004 keeps its reduced 10 seeds (not changed by this amendment). | DEC-008 A5 |

Consequences fixed by the schedule (not by data): with K = 10 and seeds 1 to 20, the number of seeds with at least one failure trial, which therefore contribute to the failure stratum, is 12 at `p = 0.1` and 18 at `p = 0.3`; every seed has at least one success trial at both levels. In EXP-004 (seeds 1 to 10, `p = 0.3`) it is 9 seeds.

Any amendment after the freeze is dated, justified and reported separately from the frozen analysis.
