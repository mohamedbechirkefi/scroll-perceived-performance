<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Review pass 2 (master prompt 11.5): arguing against the preferred hypothesis

Date: 2026-11-25 (M4). Reviewer: the AI assistant, as internal quality control; this is not peer review. The pass was made after the evidence audit (`evidence_audit.md`) and before the final manuscript commit.

**Preferred hypothesis under challenge.** "Strategies that change first feedback do not necessarily change time to usable content": skeletons change TTFF but not TTUC; prefetch and optimistic updates change TTUC by mechanical amounts; optimistic updates cost wrong-state exposure, not recovery time.

Each item states the challenge, whether it holds, and what changed.

## R-1. The main findings are mechanical, so the study confirms its own design

- **Challenge.** A skeleton cannot make data arrive sooner, prefetching removes a scripted lead and an optimistic update removes the whole wait by construction. Confirming these is closer to an instrumentation check than to a finding, and a title such as "faster-feeling interfaces are not always faster" overstates it and implies perception.
- **Holds?** Largely yes. The protocol itself said the PREFETCH test "checks the instrumentation as much as the strategy".
- **Change.** The working title was not used. The proposed title names the measured quantity, and the Discussion opens by saying that the prefetch and optimistic results check the benchmark as much as the strategies. The contribution list stresses the benchmark and the sensitivity design, not discoveries.

## R-2. The 50 ms skeleton effect was explained away

- **Challenge.** M3 called the -16.7 ms effect "a frame-scale artefact" and "not evidence that skeletons deliver content sooner". But the direction is the same under all three paint methods (-16.7, -15.3 and -9.1 ms; every interval excludes 0), and the trial-level distribution is concentrated (80.5% of 200 pairs between -25 and -8 ms; exploratory X2). Under the method closest to an actual paint time (Element Timing), the skeleton still shows content about 9 ms earlier.
- **Holds?** Yes, partly. What is method-dependent is the size and therefore the equivalence verdict, not the sign. Calling it an artefact goes beyond the evidence; so would calling it a benefit.
- **Change.** The manuscript presents the result as not robust, reports no skeleton benefit at 50 ms, and states that the data do not show the effect is absent. The EXP-002 report interpretation was revised in the same sense, with the M3 wording kept in a note. The exploratory decomposition (X2) is reported as locating the difference in frame alignment, with the mechanism untested.

## R-3. The frozen contradiction criterion was met and then softened

- **Challenge.** Protocol section 4: the main interpretation is contradicted by "a SKELETON TTUC difference outside the equivalence margin in either direction, or a reversal of any contrast under the sensitivity conditions". Equivalence failed at 50 ms and three failure strata reversed sign. The M3 reports call this "qualified". That is a post hoc softening of a pre-registered criterion.
- **Holds?** Yes, as a matter of the literal text. The argument that the three sign changes are uninformative (estimates within 1 ms of zero, intervals including 0 at every level) is sound, but it was made after the data.
- **Change.** The Discussion now has a paragraph "The frozen contradiction criterion" that says the literal criterion is met for four contrasts, explains the qualified reading, labels that judgement as post hoc, and tells the reader what the literal reading implies. Table 4's EXP-004 row says so.

## R-4. The equivalence margin is smaller than one measured frame

- **Challenge.** The 17 ms margin was justified as one 60 Hz frame, but the measured headless frame interval was 18.0 to 18.9 ms in every cell (X2). Any one-frame shift under the main method fails the TOST by construction, so the 50 ms "equivalence not shown" may say more about the margin than about skeletons. Conversely, equivalence at L of 100 ms and more is easy to show when estimates are about 1 ms.
- **Holds?** Yes. The margin was fixed before data and cannot be changed now.
- **Change.** Stated in Sections 5.5, 6 and 7 and in the limitations; future work proposes setting the margin from the measured frame interval.

## R-5. rAF1 should not have been an S1 level

- **Challenge.** The frozen EXP-004 protocol names the S1 alternative as "Element Timing or trace". DEC-011 added rAF1, which is the start of the frame and precedes the reference delay in most trials (X2), so it is not a paint time. Counting it made the write path testable under S1 and produced two of the four "not robust" flags.
- **Holds?** Partly. DEC-011 was fixed before data and is under the owner's review, so neither reading is chosen here.
- **Change.** The narrow reading is computed (X6) and shown beside the frozen verdicts: 11 robust, 1 method-dependent, 2 condition-dependent and 9 not assessed, against 19 robust. The 50 ms skeleton result is method-dependent under both. The rAF1 property is disclosed in Sections 3 and 5.5.

## R-6. The test reading was chosen by the AI

- **Challenge.** DEC-011 picked Holm over Wilcoxon p-values as the deciding test. A different reading could change verdicts.
- **Holds?** Weakly. The readings differ for 1 of 23 contrasts (EXP-002 SKELETON at L = 300 ms, about 1 ms), and the equivalence verdict is the same under both (X1).
- **Change.** Both readings are columns of Tables 1 and 2; DEC-011 is flagged as pending owner review in the Methods and Limitations.

## R-7. The headed-mode shift has another explanation

- **Challenge.** Headed rendering enlarged the optimistic benefit by 15.3 to 27.0 ms. In S4 the second-frame gap was 8.6 to 9.0 ms for OPTIMISTIC and 16.45 to 16.75 ms for BLANK on the write path (X2): the display may run a faster cadence right after input. S4 also ran one to three hours after the main runs.
- **Holds?** Yes, as an untested alternative. The refresh rate was not recorded.
- **Change.** Added to Section 5.4 and to the limitations; the robust verdicts (sign) are unaffected.

## R-8. Failure-strata nulls were written as "no later"

- **Challenge.** The draft said the optimistic update reached the final state "no later than" the baseline on failure and "did not slow recovery". With no equivalence test and intervals reaching 5.4 ms, non-significance was being read as equivalence.
- **Holds?** Yes.
- **Change.** The Discussion and Conclusion now say no difference was detected and a slower recovery of a few milliseconds cannot be excluded.

## R-9. Leakage

- **Challenge.** Were confirmatory data seen before the analysis choices?
- **Finding.** The pre-freeze EXP-001 run on seeds 1001 to 1005 was seen before amendments A1 to A3 and A6 (freeze record, C4 disclosure). Its seeds are disjoint from the confirmatory seeds. DEC-011 was committed at 07:03:09Z on 2026-11-25 (`b5a72c3`), six seconds before the first confirmatory run started at 07:03:15Z. The M4 exploratory analyses (X1 to X7) were chosen after the confirmatory data were seen and are labelled post hoc.
- **Change.** None needed beyond the existing disclosures; the timing of DEC-011 is now stated here.

## R-10. Missing failed runs

- **Challenge.** Are there runs that are not reported?
- **Finding.** The repository history contains no deleted result file. Every run in `results/` is reported: two EXP-001 runs, one smoke run, and the five confirmatory runs. DEC-012 records two scratch log files outside the repository; they held logs, not results. No confirmatory run was repeated.
- **Change.** None.

## R-11. Stale or partial figures

- **Challenge.** Figures could be out of date or omit what matters.
- **Finding.** All figures were generated by the frozen generators at run time and match their checksums. The sensitivity figure shows only the 10 reduced-matrix contrasts and so omits the 50 ms skeleton contrast, the one that is not robust. The generated run report PDFs were not visually inspected.
- **Change.** The manuscript says the figure omits that contrast and points to Table 3. PDF inspection stays an M6 task.

## R-12. Overgeneralisation

- **Challenge.** Rendering costs of about 27 to 30 ms, frame intervals and the 50 ms behaviour are properties of this page, this Chrome version and this laptop.
- **Holds?** Yes.
- **Change.** The Practical significance paragraph and the Conclusion are restricted to "in one mock interface in one browser"; no perception statement appears anywhere.

## Outcome

The preferred hypothesis survives for delays of 100 ms and more and for the mechanical strategies, with the scope stated. It does not survive unqualified at 50 ms, and the frozen contradiction criterion is reported as literally met there and on the failure strata. No frozen verdict was changed. The changes listed above are in commits of 2026-11-25 (M4); see `progress.md`.
