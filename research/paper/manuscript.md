---
# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
title: "Skeletons, prefetching and optimistic updates under controlled delays: time to usable content in a single-browser benchmark"
author: "Mohamed Bechir Kefi, independent researcher"
status: "Independent research manuscript / preprint draft, not peer-reviewed. Release candidate 0.1.0-rc1 (M6, 2026-11-25), owner answers applied 2026-11-26."
ai_disclosure: "An AI system (Claude, Anthropic) was used as a research and development assistant; it is not an author. See the AI assistance section."
---

**Status.** Independent research manuscript / preprint draft, not peer-reviewed. Every number in this text comes from a committed result file of this repository; the mapping is in `research/publication/artifact_manifest.json` and the audit in `research/publication/evidence_audit.md`. For DEC-011 (Section 4.5) the owner chose neither reading on 2026-11-26, so both readings stay shown where they matter.

# Abstract

Skeleton placeholders, intent-based prefetching and optimistic updates are recommended to make interfaces feel faster, but feeling faster and delivering usable content sooner are different quantities. We asked how these strategies change the time from a click to the first frame showing the final, correct and usable state (time to usable content, TTUC), compared with a blank baseline. One mock interface was driven by scripted input in Google Chrome 158.0.8127.38 on one laptop, with a seeded latency and failure schedule shared by all arms. The protocol was frozen before the confirmatory runs, which covered 6,000 interactions in the main experiments and 3,600 in a sensitivity experiment; the seed was the independent unit. Prefetching with a 150 ms lead reduced TTUC at every delay, by 50.0 to 160.5 ms (Holm-adjusted p at most 0.00053), close to the mechanical expectation. An optimistic update reached the final state about one delay earlier on every successful save (for example -998.6 ms, 95% CI -1012.2 to -972.6, at 1000 ms) and showed no detectable TTUC difference on failed saves, while displaying a state the server never held for about the whole delay. A skeleton was equivalent to the blank baseline within 17 ms at delays of 100 ms and more; at 50 ms it was 16.7 ms faster under the main paint-time method, but this equivalence verdict changed under both alternative methods and is not robust. The results describe timing in one browser and one synthetic page; they make no claim about perceived speed.

# Keywords

frontend performance; loading strategies; skeleton screens; prefetching; optimistic updates; reproducible benchmarking

# 1. Introduction

Interfaces that wait for a server must decide what to show during the wait. Common strategies show nothing new until the response arrives, show a placeholder with the final layout (a skeleton), start the request earlier on an intent signal such as a hover (prefetching), or show the expected result immediately and correct it if the server disagrees (an optimistic update). Practitioner guidance recommends reserving space, for example with a placeholder or skeleton, to reduce layout shift [@osmani_optimize_cls], and discusses when skeleton screens are appropriate [@tankala_skeleton], and browser standards define how the latency from an input to the next paint is measured [@w3c_event_timing; @wagner_inp]. These strategies act on different quantities. A skeleton changes what is shown first, but it cannot make the data arrive sooner; a prefetch can; an optimistic update shows the final state at once on success and a false state on failure.

The project's working question, set in its master prompt, is: how do loading strategies affect measurable interface responsiveness under controlled delays? We operationalise it as the time from a click to the first frame showing the requested content in its final, correct and usable state (TTUC), and we keep the time to first feedback (TTFF) as a secondary metric. The claims boundary is strict: objective timing is not perceived speed, and nothing here is a statement about human perception.

The gap addressed is narrow. The short, non-systematic search of the project (Section 2) found no controlled objective comparison of these strategies against a blank baseline under identical seeded delays; this is not evidence that none exists.

Hypotheses (frozen protocol v1.0, Section 4): for each non-baseline arm and condition, H0 is a zero trial-paired TTUC difference against the blank baseline, and H1 is two-sided. The pre-stated directional expectations were: no TTUC benefit for SKELETON (equivalence within 17 ms), a benefit of about -min(h, L) for PREFETCH, and a large benefit for OPTIMISTIC at p = 0 that shrinks as the failure probability rises, with growing wrong-state exposure.

Contributions:

1. A frozen, reproducible benchmark in which one mock page, one seeded schedule and one scripted input sequence are shared by four loading strategies, with every raw trial, manifest and checksum committed.
2. Confirmatory estimates for 23 primary contrasts (8 on the read path, 15 on the write path) with seed-level uncertainty and multiplicity control, including null results.
3. A pre-registered sensitivity experiment over paint-time method, CPU throttling, prefetch lead and headed rendering, which shows which verdicts depend on how a frame is timed.
4. An exploratory post hoc decomposition of the one frame-scale effect, from committed traces only, that locates it in frame alignment rather than in rendering cost.

# 2. Related work

This section is a scoping summary, not a systematic review. Every source was first opened on 2026-11-24 through a tool that returns a model-written summary of the page (`research/literature_review.md`). On 2026-11-25 (M6) the full text of the nine freely available web sources was retrieved and each claim below was checked against the cited section (`research/publication/evidence_audit.md`, section 8); the tenth source [@mejtoft2018] has no free full text and is cited for its existence only.

**Measurement standards.** The Event Timing API defines an event's duration from its timestamp to the next rendering update after dispatch, rounded to 8 ms, with an observer threshold of at least 16 ms [@w3c_event_timing]. Interaction to Next Paint aggregates such durations into a page-level responsiveness metric [@wagner_inp]. The Layout Instability API defines layout-shift values and excludes shifts shortly after discrete input [@wicg_layout_instability; @mihajlija_cls]. Largest Contentful Paint stops reporting at the first input, so it cannot time content that appears after a click [@mdn_lcp]. These sources motivate the custom TTUC marker used here and explain why Event Timing could only be descriptive: most of our interactions fell below its 16 ms threshold.

**Strategy guidance.** Practitioner guidance recommends reserving space with a placeholder or skeleton to avoid late layout shifts [@osmani_optimize_cls] and discusses when skeleton screens are appropriate [@tankala_skeleton]. Response-time limits of 0.1, 1 and 10 s [@nielsen1993response] were used only to choose latency levels. The React documentation of optimistic state describes the rollback semantics our optimistic arm imitates [@react_useoptimistic].

**Perception studies.** A study of skeleton screens and perceived speed exists [@mejtoft2018]; only its bibliographic metadata was verified and its findings are not used. Perception is outside the scope of this work.

**Relation to this work.** The study does not replicate any prior experiment. It extends standard browser instrumentation with a usable-content marker and applies it to a controlled comparison; its contribution is methodological and descriptive about one page in one browser.

# 3. Background and formal model

Let `t_in` be the click event's timestamp on the page clock. For a trial, the mock transport returns after a scheduled delay `d = L (1 + j)`, with `j` uniform in [-0.1, 0.1] and drawn from a seeded stream, and the write path fails with probability `p`. The same seed yields the same delays and outcomes in every arm (common random numbers).

TTUC is `t_final - t_in`, where `t_final` is the time of the first frame from which the target region shows the final, server-consistent, fully rendered and actionable state and keeps it until the trial ends. On a failed save, the final state is the unchanged old state together with the error message. The main paint-time method takes `performance.now()` inside the second `requestAnimationFrame` callback after the DOM commit. Two alternatives are recorded by the frozen code: the timestamp argument of the first `requestAnimationFrame` callback (rAF1, the start of the frame that will carry the change) and, on the read path, the Element Timing `renderTime` of the content.

A reference model gives each arm's ideal timing with zero overhead: for BLANK and SKELETON on the read path, `TTUC >= d`; for PREFETCH, `TTUC >= max(0, d - h)`, where `h` is the hover lead; for OPTIMISTIC, `TTUC >= 0` on success and `>= d` on failure. The excess over this bound is rendering and scheduling overhead.

For arm `s` and cell `c`, the estimand (amendment A1) is

`Delta_s(c) = median over seeds of [ median over k of ( TTUC_s,k - TTUC_BLANK,k ) ]`,

where trial `k` in both arms shares its scheduled delay and outcome. On the write path with `p > 0`, success and failure trials form separate primary strata (amendment A2); the mixed estimand over all trials is secondary.

# 4. Methods

## 4.1 Design and protocol registration

All confirmatory work followed `research/protocol.md` v1.0, frozen by the owner on 2026-11-24 (SHA-256 `a87ae45e049c16ed42abef0ab853a0e3fcf28daec9d5482d11bbb1dfb365f004`), with per-experiment protocols and configurations whose hashes are recorded in `research/freeze.json`. A run guard refused any confirmatory run whose protocol or configuration differed from the frozen one. Six amendments (A1 to A6) were approved before the freeze, after an exploratory pre-freeze run whose values of the contrasts were seen (freeze record, C4 disclosure). EXP-001 (instrumentation validation) is exploratory by design. EXP-002 (read path), EXP-003 (write path) and EXP-004 (sensitivity) are confirmatory. The analyses of Section 5.5 are exploratory and post hoc.

## 4.2 System under test and loading strategies

One locally served page shows a list of items and a detail panel, implemented once with the strategy as the only switch (`src/web/`). On the read path, a click on an item requests its detail: BLANK leaves the region empty until the response, SKELETON renders a placeholder with the final box size at input, and PREFETCH starts the request on a scripted hover 150 ms before the click. On the write path, a click on a save toggle sends a mutation: BLANK keeps the old state until the server confirms, and OPTIMISTIC shows the new state at once and rolls it back with an error message on failure. The input script is identical in every arm, and only PREFETCH reacts to the hover.

The page ran in the installed Google Chrome 158.0.8127.38, driven by Playwright 1.65.0 through `channel = "chrome"` (amendment A5), headless at CPU 1x except in EXP-004 S2 and S4. The machine was an Apple M1 Pro (10 cores, 16 GiB) under macOS 15.3.1 on mains power.

## 4.3 Latency and failure injection

Read latencies were L in {50, 100, 300, 1000} ms and write latencies L in {100, 300, 1000} ms, with p in {0, 0.1, 0.3}. Each session is a fresh browser context with K = 10 scripted interactions of one path; arms are ordered within each seed block by a seeded permutation. Confirmatory seeds were 1 to 20 (EXP-002, EXP-003) and 1 to 10 (EXP-004). With K = 10 the schedule fixes, before data, that the failure stratum has 12 seeds at p = 0.1 and 18 seeds at p = 0.3 (9 seeds in EXP-004).

## 4.4 Metrics and instrumentation

The primary metric is TTUC (Section 3), in milliseconds, lower is better. Secondary metrics are TTFF, layout shift (all entries and CLS-eligible entries), wrong-state exposure on the write path (split into false state, a state the server never held, and stale state, a superseded state), rollback correctness, and Event Timing duration, which is descriptive only (amendment A4). Exclusions were allowed only for harness failure and for the hover-lead control (amendment A3: a read trial is excluded when the measured hover-to-click lead deviates from h by more than 25 ms). A cell with more than 5% of its trials excluded is a failed cell. The stop rule required rollback correctness of 1.0 and no BLANK trial below its injected delay.

## 4.5 Statistical analysis

The seed is the independent unit. Each contrast is summarised by the median of its per-seed paired differences, with a 95% percentile bootstrap interval over seeds (10,000 resamples, fixed seed). The hypothesis test is the two-sided Wilcoxon signed-rank test on the per-seed values, with Holm correction over each experiment's primary family (8 contrasts in EXP-002, 15 in EXP-003). SKELETON equivalence uses two one-sided tests through the 90% bootstrap interval with a margin of 17 ms. Non-significance is never reported as equivalence.

The frozen protocol names the bootstrap interval, the Wilcoxon test and the Holm correction without stating which one decides H0. Before any confirmatory output existed, DEC-011 fixed the reading "H0 is rejected when the Holm-adjusted Wilcoxon p is below 0.05" and required the alternative reading, "the unadjusted 95% interval excludes 0", to be reported beside it. **For DEC-011 the owner chose neither reading (2026-11-26); both stay shown.** Both readings are shown in Table 1 and Table 2; they differ for exactly one of the 23 primary contrasts (Section 5.2).

EXP-004 applies the frozen robustness rule: a verdict is robust only if the sign of the point estimate is the same at every available factor level; for SKELETON the rule uses the equivalence verdict. DEC-011 item 5 also fixed which alternative paint methods form level S1 (both rAF1 and Element Timing); the owner chose neither S1 reading either, and Section 5.4 shows the effect of the narrower reading.

## 4.6 Reproducibility

Commands are in each experiment report's reproduction appendix. Raw results are committed under `results/raw/` with SHA-256 manifests; all 110 listed files matched their checksums in the M4 audit. Tables and figures are produced by the frozen generators `python -m scroll report` and `python -m scroll.inference`, and the exploratory analyses by `scripts/m4_reanalysis.py`. Confirmatory runs used code revision `b5a72c3`, whose run path is identical to the freeze revision `b4bd25b`.

# 5. Results

## 5.1 EXP-001: instrumentation validation (exploratory)

EXP-001 was run twice on exploratory seeds 1001 to 1005, which are disjoint from the confirmatory seeds: once before the freeze on a loaded machine (`EXP-001-20261124T161058Z`, load average 25.31 at the start), and once as the metric validation in the quiet window before the confirmatory runs (`EXP-001-20261125T065102Z`). Both runs had 70 of 70 sessions and 350 interactions. All four instrumentation checks passed in both: no BLANK trial below its injected delay (minimum excess 2.5 and 3.2 ms), cell median excess over the reference model of 11.5 to 23.8 ms and 12.0 to 27.0 ms, against a planning threshold of 50 ms, rollback correct in every write trial, and prefetched responses used in every PREFETCH trial. The second run had one hover-lead exclusion. The pre-freeze run motivated amendments A1 to A3 and A6; its values are not evidence. The protocol said EXP-001 would choose the alternative paint method for S1; no choice was recorded (DEC-012).

## 5.2 EXP-002: read path

EXP-002 (`EXP-002-20261125T070315Z`) completed 240 of 240 sessions in 3,887.4 s; 2,387 of 2,400 trials were analysed after 13 hover-lead exclusions (at most 2 of 200 in any cell and arm), and no cell failed. No BLANK trial had TTUC below its injected delay (0 of 796), and the final state was correct in every trial.

Table 1. EXP-002 primary contrasts. Median trial-paired TTUC difference against BLANK, ms; 20 seeds per contrast; 95% percentile bootstrap interval; two-sided Wilcoxon with Holm over 8. Reading A is DEC-011 (Holm-adjusted Wilcoxon); reading B is the unadjusted 95% interval. Source: `results/raw/EXP-002/EXP-002-20261125T070315Z/report/inference.json`.

| L (ms) | Contrast | Median (ms) | 95% CI (ms) | Holm p | Reading A | Reading B | TOST 90% CI (ms), equivalence |
|---|---|---|---|---|---|---|---|
| 50 | PREFETCH | -50.0 | [-51.2, -48.9] | 0.00053 | reject | excludes 0 | |
| 50 | SKELETON | -16.7 | [-17.1, -16.0] | 0.00053 | reject | excludes 0 | [-17.05, -16.1], not shown |
| 100 | PREFETCH | -84.9 | [-86.3, -84.1] | 1.5e-05 | reject | excludes 0 | |
| 100 | SKELETON | -0.6 | [-1.9, 0.1] | 0.27 | not rejected | includes 0 | [-1.6, 0.0], equivalent |
| 300 | PREFETCH | -160.5 | [-163.5, -157.1] | 1.5e-05 | reject | excludes 0 | |
| 300 | SKELETON | -1.0 | [-1.1, -0.4] | 0.27 | not rejected | **excludes 0** | [-1.1, -0.6], equivalent |
| 1000 | PREFETCH | -157.8 | [-159.1, -155.4] | 0.00053 | reject | excludes 0 | |
| 1000 | SKELETON | 0.0 | [-0.9, 0.9] | 1.0 | not rejected | includes 0 | [-0.7, 0.8], equivalent |

**PREFETCH.** Prefetching reduced TTUC at every delay. The estimates were within 17 ms of the mechanical expectation -min(h, L): deviations 0.0, 15.1, -10.5 and -7.8 ms at L = 50, 100, 300 and 1000 ms, so the frozen contradiction rule was not met. At L of 50 and 100 ms the residual wait is zero by construction, and TTUC equals the rendering cost (cell median 27.7 ms); the deviation at L = 100 ms arises because BLANK's own overhead there (median excess 16.3 ms) is smaller than PREFETCH's.

**SKELETON at L of 100 ms and more.** The skeleton was equivalent to BLANK within 17 ms, with estimates of -1.0 to 0.0 ms, while it lowered TTFF from about the full delay to about 28 ms (cell medians 27.5 to 28.0 ms). The two test readings disagree at L = 300 ms: the unadjusted interval [-1.1, -0.4] ms excludes 0, the Holm-adjusted Wilcoxon test does not reject. The difference is about 1 ms, and neither reading changes the equivalence verdict.

**SKELETON at L = 50 ms.** The skeleton reached usable content 16.7 ms earlier than BLANK under the main paint method, H0 was rejected, and equivalence was not shown because the lower 90% bound, -17.05 ms, lies just beyond the margin. Section 5.4 shows that this verdict is not robust.

Layout shift was identical across arms in most cells (median 0.035 in all entries); the CLS-eligible median was 0.035 for BLANK and PREFETCH at L = 1000 ms and 0 elsewhere, a design consequence of BLANK's collapsing empty region (DEC-007). Event Timing was below its 16 ms threshold in 71 to 79% of BLANK trials. Figures: `results/raw/EXP-002/EXP-002-20261125T070315Z/report/figures/fig-ttuc.svg` (TTUC per trial by cell and arm, log scale) and `fig-paired.svg` (per-seed paired differences with 95% intervals).

## 5.3 EXP-003: write path

EXP-003 (`EXP-003-20261125T080838Z`) completed 360 of 360 sessions in 6,318.7 s, with 3,600 of 3,600 trials analysed, no exclusion and rollback correctness 1.0; the stop rule was not triggered.

Table 2. EXP-003 primary contrasts, OPTIMISTIC minus BLANK, ms. Seeds per stratum fixed by the schedule; Holm over 15. Reading A and reading B as in Table 1; they agree for all 15 contrasts. Source: `results/raw/EXP-003/EXP-003-20261125T080838Z/report/inference.json`.

| L (ms) | p | Stratum | Seeds | Median (ms) | 95% CI (ms) | Holm p | Reading A | Reading B |
|---|---|---|---|---|---|---|---|---|
| 100 | 0 | success | 20 | -85.2 | [-88.0, -84.3] | 0.00079 | reject | excludes 0 |
| 100 | 0.1 | success | 20 | -85.3 | [-86.6, -84.8] | 2.9e-05 | reject | excludes 0 |
| 100 | 0.1 | failure | 12 | 0.5 | [-1.5, 1.7] | 1.0 | not rejected | includes 0 |
| 100 | 0.3 | success | 20 | -85.3 | [-88.0, -83.9] | 0.00079 | reject | excludes 0 |
| 100 | 0.3 | failure | 18 | 2.7 | [-1.0, 5.4] | 0.37 | not rejected | includes 0 |
| 300 | 0 | success | 20 | -288.5 | [-297.7, -282.3] | 0.00079 | reject | excludes 0 |
| 300 | 0.1 | success | 20 | -289.3 | [-297.6, -283.5] | 2.9e-05 | reject | excludes 0 |
| 300 | 0.1 | failure | 12 | -0.8 | [-3.0, 4.3] | 1.0 | not rejected | includes 0 |
| 300 | 0.3 | success | 20 | -290.4 | [-297.4, -284.1] | 2.9e-05 | reject | excludes 0 |
| 300 | 0.3 | failure | 18 | -0.1 | [-2.6, 1.5] | 1.0 | not rejected | includes 0 |
| 1000 | 0 | success | 20 | -998.6 | [-1012.2, -972.6] | 2.9e-05 | reject | excludes 0 |
| 1000 | 0.1 | success | 20 | -995.9 | [-1015.8, -967.3] | 2.9e-05 | reject | excludes 0 |
| 1000 | 0.1 | failure | 12 | -1.6 | [-7.1, 0.1] | 0.46 | not rejected | includes 0 |
| 1000 | 0.3 | success | 20 | -990.7 | [-1016.6, -961.7] | 2.9e-05 | reject | excludes 0 |
| 1000 | 0.3 | failure | 18 | 0.6 | [-1.4, 3.4] | 1.0 | not rejected | includes 0 |

On success, the optimistic update showed the final state about one delay earlier; OPTIMISTIC cell medians of TTUC were 27.0 to 29.7 ms against 111.6 to 1024.8 ms for BLANK. On failure, no stratum rejected H0, with estimates from -1.6 to 2.7 ms; no equivalence test was registered for these strata, so they are not equivalence claims. The secondary mixed estimand decreased strictly in magnitude from p = 0 to 0.1 to 0.3 at each delay (for example -998.6, -974.1 and -951.5 ms at L = 1000 ms), as expected, so the frozen trend check found no contradiction.

The cost of the optimistic update is visible in wrong-state exposure rather than in TTUC. In failure trials (83 per delay and arm over both p levels), OPTIMISTIC displayed a false state for a median of 83.4, 283.9 and 999.1 ms at L = 100, 300 and 1000 ms, and BLANK displayed none. Layout shift was 0 in every write cell. Figures: `results/raw/EXP-003/EXP-003-20261125T080838Z/report/figures/fig-ttuc.svg` and `fig-paired.svg`.

## 5.4 EXP-004: sensitivity

EXP-004 ran S2 (CPU 4x, 140 sessions), S3 (h = 0 and 600 ms, 80 sessions, 4 hover-lead exclusions) and S4 (headed, 140 sessions) in full, 3,596 of 3,600 trials analysed, with no failed cell; S1 recomputed every EXP-002 and EXP-003 contrast with the alternative paint methods. Under the frozen rule, 19 of 23 primary contrasts were robust, including every PREFETCH and every OPTIMISTIC success contrast and the SKELETON equivalence at L of 100 ms and more.

Table 3. The four contrasts that the frozen rule does not call robust. Median trial-paired TTUC difference, ms, with 95% interval. Source: `results/raw/EXP-004/sensitivity/sensitivity.json`.

| Contrast | Main | S1 rAF1 | S1 Element | S2 CPU 4x | S4 headed | Frozen verdict |
|---|---|---|---|---|---|---|
| read L=50 SKELETON | -16.7 [-17.1, -16.0], eq no | -15.3 [-16.0, -14.8], eq yes | -9.1 [-9.8, -8.3], eq yes | | | method-dependent |
| write L=300 p=0.1 failure | -0.8 [-3.0, 4.3] | 0.7 [-1.9, 4.3] | | | | method-dependent |
| write L=300 p=0.3 failure | -0.1 [-2.6, 1.5] | 0.4 [-1.4, 1.7] | | -0.3 [-0.9, 2.0] | 0.4 [-2.7, 0.9] | method- and condition-dependent |
| write L=1000 p=0.3 failure | 0.6 [-1.4, 3.4] | 1.2 [-0.8, 2.1] | | -1.3 [-4.2, 0.9] | 0.0 [-1.3, 2.8] | condition-dependent |

**The 50 ms skeleton effect is not robust.** Its equivalence verdict changes under both alternative paint methods, so under the frozen rule the result is method-dependent. The direction is the same under all three methods, but the size is not (-16.7, -15.3 and -9.1 ms), and whether it exceeds the equivalence margin depends on the method. We therefore do not report a skeleton benefit at 50 ms.

**The three failure strata.** Their main estimates lie within 1 ms of zero, none rejects H0, and the frozen sign rule flags them because the sign of a near-zero estimate flips. Under the exploratory interval reading of Section 5.5, every level's 95% interval includes 0 for all six failure strata, which is the pattern expected of a null contrast. The frozen verdicts stand as reported.

**Reading of level S1 (both readings shown).** The frozen EXP-004 protocol names the S1 alternative as "Element Timing or trace". DEC-011 counted rAF1 as well, which made S1 available on the write path. Under the narrower reading (Element Timing only, which exists on the read path only; X6 in Section 5.5), the read-path verdicts are unchanged, but the nine write contrasts at L = 100 ms or p = 0.1 have no sensitivity level at all, because S2 to S4 cover only L in {300, 1000} ms and p in {0, 0.3}. The count becomes 11 robust, 1 method-dependent (the 50 ms skeleton), 2 condition-dependent (write L = 300 and 1000 ms, p = 0.3, failure) and 9 not assessed. The skeleton result at 50 ms is method-dependent under both readings.

**Shifts within robust contrasts.** Under CPU 4x the prefetch benefit shrank by 5.9 to 7.6 ms and the optimistic success benefit grew by 5.9 to 13.7 ms; headed rendering enlarged the optimistic success benefit by 15.3 to 27.0 ms (10 seeds each; differences of point estimates, not tests). The headed shift has an untested competing explanation: in S4 the median second-frame gap was 8.6 to 9.0 ms for OPTIMISTIC but 16.45 to 16.75 ms for BLANK on the write path (exploratory X2), which suggests that the display ran a faster frame cadence shortly after input; the refresh rate was not recorded, and the S4 run also took place one to three hours after the main runs. In S3 the prefetch benefit scaled with the lead: -293.9 and -609.6 ms at h = 600 ms (L = 300 and 1000 ms), and -1.9 and -1.7 ms at h = 0. TTFF sensitivity could not be computed, because the frozen code records alternative paint times only for the usable-content frame. Figure: `results/raw/EXP-004/sensitivity/figures/fig-sensitivity.svg`; it shows only the 10 contrasts of the reduced matrix, so the 50 ms skeleton contrast and the contrasts checked under S1 only appear in Table 3 and the EXP-004 report, not in the figure.

## 5.5 Exploratory re-analysis of committed traces (M4, post hoc)

The following analyses were run on 2026-11-25 by `scripts/m4_reanalysis.py` (code revision and input checksums in the output manifest), on the committed `results.json` files only, with no browser run. They are exploratory, post hoc and never replace a frozen verdict. Outputs: `results/exploratory/M4-REANALYSIS/`.

**X1, test readings.** Tabulating both readings over the 23 primary contrasts confirms that they disagree only for EXP-002 SKELETON at L = 300 ms (`x1_test_readings.csv`).

**X2, where the 50 ms skeleton effect sits.** The double-rAF TTUC can be split into the first-frame time relative to the reference delay and the gap to the second frame. At L = 50 ms the second-frame gap was the same in both arms (median 18.9 ms for BLANK, 18.8 ms for SKELETON), whereas the first frame began 8.1 ms after the reference delay for BLANK and 7.0 ms before it for SKELETON. In other words, for SKELETON the frame that carries the content was already under way when the content was committed (83% of trials), and for BLANK it almost never was (1%). At L of 100 ms and more, BLANK behaved like SKELETON (first frame before the reference in 72 to 79% of read trials). At the trial level the main-method difference was concentrated, not driven by a few outliers: median -16.5 ms, interquartile range -19.3 to -14.2 ms, and 80.5% of the 200 trial pairs between -25 and -8 ms. Under Element Timing the trial-level median was -9.3 ms. These observations locate the effect in frame alignment, the competing explanation that the EXP-002 protocol named ("frame alignment could create artificial 8 to 17 ms steps"), not in a rendering cost. Why the renderer was idle for BLANK only at 50 ms is not tested (`x2_frame_decomposition.csv`, `x2_skeleton_l50_trial_distribution.csv`).

**X2, frame interval against the margin.** In the headless runs the median second-frame gap, an estimate of the frame interval, was 18.0 to 18.9 ms in every cell, larger than the 17 ms margin that the protocol justified as one 60 Hz frame. A difference of one frame under the main method therefore cannot pass the equivalence test.

**X2, the rAF1 method.** The rAF1 time precedes the reference delay in most trials (for example 72 to 79% of BLANK read trials at L of 100 ms and more), because it is the start of the frame rather than a paint time. It is a lower, optimistic estimate, as the code documents, and the instrumentation check "no BLANK trial below the injected delay" holds only for the main method (0% of trials).

**X3, hover-lead exclusions.** Keeping the 13 trials excluded by the A3 rule changes no EXP-002 verdict; the largest change of a point estimate is 0.2 ms (`x3_a3_inclusion_exp002.csv`).

**X4, interval reading of robustness.** For every non-SKELETON contrast, we classified each factor level by whether its 95% interval excludes 0. Twelve of the 13 PREFETCH and OPTIMISTIC success contrasts excluded 0 on the same side at every level; the exception, PREFETCH at L = 300 ms, includes 0 only at h = 0, where the benefit is removed by design. All six failure strata included 0 at every level (`x4_interval_robustness.csv`). This reading is post hoc; it is a candidate for a future protocol, not a revised verdict.

**X6, narrow S1 reading.** The frozen robustness rule recomputed with S1 restricted to Element Timing gives the counts reported in Section 5.4 (`x6_narrow_s1_reading.csv`).

**X5, arm order.** Splitting seeds by whether the arm ran before BLANK in its block (5 to 15 seeds per group) gave differences of group medians of at most 9.1 ms for contrasts of 85 to 999 ms, at most 3.8 ms for the failure strata, and 0.05 ms for SKELETON at L = 50 ms (`x5_arm_order.csv`). No order effect large enough to change a verdict is visible, but the groups are small and this is not a test.

## 5.6 Expected versus observed

Table 4. Pre-stated expectations, observations and the verdict under the frozen rule.

| Experiment | Prediction (frozen) | Observation | Verdict under the frozen rule |
|---|---|---|---|
| EXP-001 | C1 to C4 pass (instrumentation checks) | Pass in both exploratory runs | Instrumentation validated (exploratory) |
| EXP-002 | PREFETCH about -min(h, L), within 17 ms | Deviations 0.0 to 15.1 ms | No contradiction; H0 rejected at all 4 delays |
| EXP-002 | SKELETON equivalent within 17 ms | Equivalent at L of 100 to 1000 ms; at 50 ms -16.7 ms, TOST lower bound -17.05 ms | Equivalence shown at 3 of 4 delays; not shown at 50 ms |
| EXP-002 | SKELETON lowers TTFF | TTFF about 28 ms against about the full delay | Descriptive; TTFF was not tested |
| EXP-003 | OPTIMISTIC large negative at p = 0 | -85.2, -288.5, -998.6 ms | H0 rejected in all 9 success strata |
| EXP-003 | Mixed advantage shrinks as p rises | Strictly decreasing at every delay | No contradiction |
| EXP-003 | Wrong-state exposure grows with failures | False state about the delay on every failed save | Descriptive, as expected |
| EXP-003 | (no direction pre-stated for failure strata) | -1.6 to 2.7 ms | H0 not rejected in all 6; no equivalence claim |
| EXP-004 | No reversal of any contrast; SKELETON equivalence stable | 19 of 23 robust; 50 ms SKELETON method-dependent; 3 null failure strata flagged by the sign rule | Literal contradiction criterion met for 4 contrasts; main interpretation qualified at 50 ms (see Section 6) |

# 6. Discussion

**What the evidence supports.** Two strategies changed time to usable content in the direction and of the size that their mechanisms imply. Prefetching removes the hover lead from the wait, and the measured benefit matched -min(h, L) within 17 ms at every delay, scaled with h in S3, and kept its sign under CPU throttling and headed rendering. An optimistic update removes the whole wait on success, at a rendering cost of about 27 to 30 ms, and the benefit was robust under every sensitivity factor. These results check the implementation and instrumentation as much as the strategies: they confirm that the benchmark recovers effects that are known by construction.

**Feedback versus usable content.** The skeleton changed first feedback without changing time to usable content beyond a fraction of a frame at delays of 100 ms and more, and this equivalence held under every method and condition tested. That is the pattern the working title anticipated. At 50 ms the picture is less clean. Under all three paint methods the skeleton arm showed content earlier, by between about half a frame and one frame, and the exploratory decomposition places the difference in when the frame carrying the content started, not in rendering cost. Because the equivalence verdict changes with the paint method, and because a one-frame difference cannot pass a 17 ms margin when the measured headless frame interval is 18.0 to 18.9 ms, we treat this result as not robust and do not report it as a benefit. We also do not claim that it is absent: the evidence supports "a frame-scale, method-dependent difference of uncertain mechanism", nothing stronger.

**Failure and the cost of optimism.** On failed saves no TTUC difference between the optimistic update and the pessimistic baseline was detected (estimates -1.6 to 2.7 ms, intervals reaching 5.4 ms; no equivalence test was registered), but the optimistic arm displayed a state the server never held for almost the whole delay. In this benchmark, the measured cost of an optimistic update is therefore wrong-state exposure; a slower recovery of a few milliseconds cannot be excluded. The frozen sign rule flagged three failure strata as method- or condition-dependent. Their estimates are within 1 ms of zero, not significant, and their intervals include 0 at every level, so the flags carry no directional information; they show a limitation of a sign rule without a tolerance band.

**The frozen contradiction criterion.** Protocol section 4 states what would contradict the main interpretation: a SKELETON difference outside the equivalence margin in either direction, or a reversal of any contrast under the sensitivity conditions. Read literally, this criterion is met: equivalence was not shown at 50 ms, and three failure strata changed sign under some level. We report the main interpretation as qualified rather than refuted because the 50 ms estimate lies inside the margin with a method-dependent size, and because the three sign changes concern estimates within 1 ms of zero whose intervals include 0 at every level. That judgement was made after seeing the data. A reader who applies the criterion literally should conclude that the frozen test of the main interpretation was failed at the shortest delay and on the failure strata.

**Competing explanations.** The protocols named placeholder rendering cost, prefetch cache overhead and frame alignment on the read path, and rollback re-rendering, error-message layout shift and callback scheduling on the write path. Placeholder rendering cost would make the skeleton slower; no such cost appeared at any delay, including under CPU 4x. Prefetch overhead is visible only at delays where the residual wait is zero, as a rendering cost of about 28 ms. Frame alignment is the explanation the data favour for the 50 ms skeleton effect (X2). Rollback cost would make failure strata positive; the largest failure estimate was 2.7 ms with an interval reaching 5.4 ms. Error messages caused no layout shift (0 in every write cell). Hover-lead jitter and arm order do not change any verdict (X3, X5). Machine load and time drift were controlled only by a quiet window and are discussed in Section 7.

**Practical significance.** In this setting, the size of an optimistic or prefetch benefit is set by the delay or the lead, not by the strategy's implementation, and a skeleton is not a way to deliver content sooner. These are statements about one page in one browser; they suggest which quantities a practitioner should measure, not how users will experience them.

# 7. Limitations and threats to validity

The full list is maintained in `research/limitations.md`. The most important are:

1. **No perception claims.** All results are objective timings. Nothing here measures how fast an interface feels; a perceived-speed claim would need a human study under an owner-approved protocol.
2. **One page, one browser version, one machine.** Chrome 158.0.8127.38 on an Apple M1 Pro, mostly headless. Other engines, devices, frameworks and DOM sizes are not covered.
3. **Synthetic latency and scripted input.** Delays come from a seeded transport with uniform 10% jitter; there are no retries, timeouts or network effects. The hover is scripted with a fixed lead, so the prefetch benefit is bounded by design and says nothing about how often real users hover.
4. **Paint-time construct.** The main method measures the second animation frame after the commit; the alternatives move some estimates by up to about 10 ms (PREFETCH at L = 100 ms: -84.9 ms main, -95.2 ms Element Timing). Frame-scale effects are method-dependent (Section 5.4), the headless frame interval of 18.0 to 18.9 ms exceeds the 17 ms margin, and the display refresh rate was not recorded in headed runs.
5. **Two test readings.** DEC-011 fixes which test decides H0 and which alternative paint methods form S1; the owner chose neither reading (2026-11-26). Both readings are shown where they differ (one contrast in Table 1; the robustness counts in Section 5.4, 19 of 23 robust against 11 robust and 9 not assessed).
6. **Sensitivity coverage.** S2 to S4 use 10 seeds and a reduced matrix (L in {300, 1000} ms, p in {0, 0.3}); TTFF sensitivity was not computable.
7. **Run conditions.** Runs executed under `nice -n 10` in a coordinator-arranged quiet window, with load averages of 1.4 to 2.4 at the starts; background services and an editor were still running. The frozen generator's fixed sentence that other agents were running is inaccurate for these runs (DEC-012).
8. **Failure strata.** They have 12 or 18 seeds and 26 or 57 trial pairs per cell, and no equivalence test was registered for them.
9. **Exploratory analyses.** Section 5.5 is post hoc. It can suggest, not confirm.

# 8. Ethics and responsible research

The study uses only a synthetic mock page and a seeded schedule; no personal data, no external dataset and no human participants were involved, so no ethics approval was sought or needed, and none is claimed. Results concern no real or proprietary product. Because the findings are about timing, not experience, they should not be used to argue that a strategy improves or harms user perception.

# 9. Conclusion and future work

In one mock interface in one browser, intent prefetching and optimistic updates reduced time to usable content by amounts set by the hover lead and the delay, and both results were robust to the sensitivity factors tested. On failed saves no difference in time to the final state was detected, but the optimistic arm displayed a false state for about the whole delay. A skeleton placeholder changed first feedback but not time to usable content at delays of 100 ms and more; at 50 ms a frame-scale difference appeared whose size depends on the paint-time method, and it is not robust.

Feasible extensions, each needing a new owner-approved protocol: record alternative paint times for the first-feedback frame so that TTFF sensitivity can be computed; use a robustness rule with a tolerance band or intervals; set the equivalence margin from the measured frame interval; record the display refresh rate in headed runs; treat renderer frame-loop state as an explicit factor below 100 ms; add retries and timeouts to the failure model; and register an equivalence test for the failure strata.

# Data and code availability

All code, configurations, frozen protocols, raw results with SHA-256 manifests, generated tables and figures are in the project repository: https://github.com/mohamedbechirkefi/scroll-perceived-performance. Clean-run commands are in each experiment report (`research/experiments/EXP-00N/report.md`, section 12). Raw results: `results/raw/EXP-002/`, `results/raw/EXP-003/`, `results/raw/EXP-004/`; exploratory results: `results/exploratory/`. The code is released under the SCROLL Source-Available Non-Commercial Research License v1.0 (`LICENSE`).

# Funding, competing interests and AI assistance

**Funding.** No funding was received.

**Competing interests.** The author declares no competing interests.

**AI assistance.** An AI system (Claude, Anthropic) was used as a research and development assistant: it drafted the protocols for the owner's approval, wrote the code and tests, ran the experiments under the frozen protocol, computed the analyses and drafted this manuscript. It is not an author. Human verification: the owner approved the protocol freeze, the amendments and the decisions recorded in `research/decision_log.md`; the owner approved this AI-use statement, the title, the author line and the statements above on 2026-11-26 and chose neither DEC-011 reading; the owner's full-text review of this manuscript is pending. An internal AI review pass (`research/publication/review_pass_2.md`) is quality control, not peer review.

# References

::: {#refs}
:::

The reference list is generated from `research/paper/references.bib`. Nine entries were read as full text on 2026-11-25 and the cited passages checked (`research/publication/evidence_audit.md`, section 8); mejtoft2018 is metadata only (no free full text) and is not used for any finding.

# Supplementary appendix

See `research/paper/supplementary.md`: complete experimental matrix, configurations and hashes, extended tables, robustness results, report links and deviations.
