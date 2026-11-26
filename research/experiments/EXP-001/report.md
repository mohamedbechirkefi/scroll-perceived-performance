<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# EXP-001 report: Smoke run and instrumentation validation (EXPLORATORY)

**Label: exploratory.** EXP-001 is exploratory by design and was never frozen. Its values are not evidence for any research hypothesis. This report was composed in M4 (2026-11-25) from committed outputs only; no number in it was recomputed.

## 1. Identification

| Field | Value |
|---|---|
| Experiment | EXP-001 (exploratory, instrumentation validation) |
| Runs | `EXP-001-20261124T161058Z` (pre-freeze, 2026-11-24, 16:10:58Z to 16:21:49Z); `EXP-001-20261125T065102Z` (M3 metric validation, 2026-11-25, 06:51:02Z to 07:01:48Z) |
| Protocol | `research/experiments/EXP-001/protocol.md`, draft v0.1, not frozen and not hashed |
| Configuration | `experiments/EXP-001.json`, canonical hash `f39023e2ef11d9ea44951792ee5fa0316711486e081cd8c5d758d4aab0996c6c` (both runs) |
| Code revision | First run `2059ba7e5f2955c65297cca1de9dcc3c95586f69` (clean). Second run `7c8f7d10d14629a230536b4db42ba2fc81883538` plus the then-uncommitted inference module (manifest `dirty: true`; the module was committed in `b5a72c3` before any confirmatory run) |
| Status | Both runs complete; all four instrumentation checks passed in both |
| Authorship | Mohamed Bechir Kefi, independent researcher. An AI system was used as a research and development assistant; it is not an author |

## 2. Executive summary

- **Question.** Does the harness measure what the protocol says, and how noisy is it?
- **Method.** 3 read arms x L {100, 1000} ms and 2 write arms x L {100, 1000} ms x p {0, 0.5}, 5 exploratory seeds (1001 to 1005), 5 interactions per session: 350 interactions per run.
- **Outcome.** In both runs, no BLANK trial reached usable content before its injected delay, the median excess over the reference model was below the 50 ms planning threshold in every cell, rollback was correct in every write trial, and every PREFETCH trial used the prefetched response.
- **Principal caveat.** The first run took place on a heavily loaded machine and is noisy; it informed the pre-freeze amendments A1, A2, A3 and A6. The protocol said that EXP-001 would choose the alternative paint method for EXP-004 S1; that choice was not recorded (DEC-012).

## 3. Rationale and literature

The mock transport delays every response by a known amount `d`, so in BLANK content cannot appear before `t_in + d`. Comparing TTUC with this lower bound tests the timing chain before any comparison. Standard browser metrics cannot time post-interaction content directly: Largest Contentful Paint stops at the first input, and Event Timing hides durations under 16 ms (sources W3C-ET and MDN-LCP in `research/literature_review.md`, opened as model-written page summaries, not full text).

## 4. Hypotheses and operational definitions

These are instrumentation checks, not research hypotheses.

- **C1:** in BLANK, `TTUC >= d` in 100% of trials. Contradicted by any trial with `TTUC < d`.
- **C2:** median `TTUC - d` in BLANK is under 50 ms at both latency levels (planning threshold).
- **C3:** rollback correctness is 1.0 in OPTIMISTIC with p = 0.5.
- **C4:** with h = 150 ms, PREFETCH uses the prefetched response in 100% of clicked trials.
- **sigma_d:** the standard deviation of the per-seed paired differences, for the sample-size rule of protocol section 5.1 (owner to be asked if it exceeded 28 ms).

## 5. Methodology

- Page, harness and schedule as in the parent protocol: one local mock page, installed Google Chrome 158.0.8127.38 through Playwright 1.65.0, headless, CPU 1x, seeded delays with 10% jitter.
- Session: fresh browser context, K = 5 interactions; seeds 1001 to 1005, reserved for exploratory runs and never reused confirmatorily.
- Machine: Apple M1 Pro, 10 cores, 16 GiB, macOS 15.3.1.
  - First run: load average 25.31/34.98/22.02 at the start and 3.14/8.87/14.17 at the end, with other agents running.
  - Second run: load average 1.98/4.69/13.26 at the start and 1.27/1.85/7.05 at the end, mains power, under `nice -n 10`.
- Budget: at most 30 minutes; 651.6 s and 645.4 s were used.
- Analysis: descriptive only (cell medians, interquartile ranges, minimum excess, sigma_d). No hypothesis test on research contrasts.

## 6. Implementation verification

- Tests before the first run: 137 passed (`progress.md`, M2 session). Before the second run: 171 passed at `7c8f7d1`.
- The first smoke attempt in M2 found a defect (the page passed a stream id instead of a stream name; every trial timed out), fixed before the EXP-001 run (journal J-0002).
- C1 to C4 are themselves the verification of the timing chain against the reference model.

## 7. Execution record

- Commands: `PYTHONPATH=src .venv/bin/python -m scroll run --config experiments/EXP-001.json` (second run under `nice -n 10`), then `python -m scroll report --run <run dir>`; for the second run also `python -m scroll.inference primary --run <run dir>`, whose output is exploratory and carries no verdict.
- Samples: 70 of 70 sessions in both runs; 350 trials each. First run: no exclusion. Second run: 1 hover-lead exclusion (BLANK, read L = 100 ms, measured lead 178.8 ms), 1 of 25 trials in that group.
- Deviations: the first run preceded the freeze and the A3 rule, so it applied no hover-lead exclusion. Neither run is confirmatory.

## 8. Results

Instrumentation checks (journal J-0003 and J-0005):

| Check | First run (pre-freeze, loaded machine) | Second run (quiet window) |
|---|---|---|
| C1, BLANK TTUC at least the delay | pass, minimum excess 2.5 ms | pass, minimum excess 3.2 ms |
| C2, BLANK median excess under 50 ms | pass, cell medians 11.5 to 23.8 ms | pass, cell medians 12.0 to 27.0 ms |
| C3, rollback correct | pass, 1.0 in every write cell | pass, 200 of 200 write trials |
| C4, prefetch used | pass, 1.0 | pass, 50 of 50 trials |
| Defect flags | 0 | 0 |

Paired noise (seed-level standard deviation of paired differences; 5 seeds; descriptive):

| Contrast | First run, draft estimand | Second run, trial-paired estimand (A1) |
|---|---|---|
| SKELETON - BLANK, read L = 100 ms | 4.1 ms | 2.3 ms |
| SKELETON - BLANK, read L = 1000 ms | 9.3 ms | 1.3 ms |
| PREFETCH - BLANK, read L = 100 ms | 8.3 ms | 5.8 ms |
| PREFETCH - BLANK, read L = 1000 ms | 22.5 ms | 3.6 ms |
| OPTIMISTIC - BLANK, write L = 100 ms, p = 0 | 4.3 ms | 4.1 ms |
| OPTIMISTIC - BLANK, write L = 1000 ms, p = 0 | 49.5 ms | 55.3 ms |
| OPTIMISTIC - BLANK, write p = 0.5 (mixed) | 45.0 and 498.0 ms | 43.1 and 506.5 ms |

- The mixed write cells at p = 0.5 are bimodal (a mixture of success and failure regimes); this motivated amendment A2 (outcome strata). In the second run the strata separate cleanly: the success strata at p = 0.5 had sigma_d 4.6 ms (L = 100 ms) and 20.6 ms (L = 1000 ms), and the failure strata 4.3 and 4.4 ms (4 seeds).
- Runtime: 651.6 s and 645.4 s for 350 interactions. The projection from the first run (EXP-002 65.3 min, EXP-003 104.2 min) compares with the measured 64.8 and 105.3 min.
- Outputs: `results/exploratory/EXP-001/<run>/report/` (`cell_summary.csv`, `paired_contrasts.csv`, `trial_paired_contrasts.csv` for the second run, figures `fig-ttuc`, `fig-paired`, `fig-excess`).

## 9. Interpretation

- **Measured.** The timing chain respects the known lower bound in every BLANK trial, and its overhead is a few tens of milliseconds. The arms behave as specified.
- **Noise.** With trial-level pairing, sigma_d was well under the 28 ms planning threshold for the read path and for the write path at L = 100 ms; at L = 1000 ms p = 0 it was 49.5 and 55.3 ms, above the threshold. Twenty seeds were kept (A6), which was the owner's decision; the confirmatory runs then measured seed spreads far smaller than these exploratory values (for example 1.6 to 4.5 ms in EXP-002).
- **Not established here.** EXP-001 does not test any research hypothesis, and its contrast values are not reported as findings.

## 10. Threats to validity

- The first run's load (average 25.31 at the start) inflates its noise; its sigma_d values overstate the quiet-machine values.
- Five seeds and five interactions per session give imprecise noise estimates.
- The alternative paint method for S1 was not chosen here, as the EXP-004 protocol expected (DEC-012).
- The second run's code had an uncommitted analysis module; the run path was unchanged.

## 11. Conclusion and next experiment

The instrumentation passed every check in both runs, so the confirmatory experiments could proceed. The next experiments were EXP-002 and EXP-003 under the frozen protocol. A future protocol should record the chosen alternative paint method explicitly and record alternative paint times for the first-feedback frame.

## 12. Reproduction appendix

- Dependencies: `uv.lock` (`uv sync --frozen --all-groups --all-extras`), Python 3.12.1, Playwright 1.65.0, installed Google Chrome (version recorded per run).
- Clean run: `PYTHONPATH=src .venv/bin/python -m scroll run --config experiments/EXP-001.json`, then `python -m scroll report --run <run dir>`.
- Raw results: `results/exploratory/EXP-001/EXP-001-20261124T161058Z/results.json` and `results/exploratory/EXP-001/EXP-001-20261125T065102Z/results.json`, schema `src/scroll/schemas/result-1.0.0.json`.
- Tolerance: timings vary with machine state; the schedule is identical by seed.
- Records: journal J-0003 and J-0005; DEC-008, DEC-009, DEC-012; freeze record C4 disclosure.
