<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
<!-- Draft for Medium (master prompt 11.7). Not published; publication is the owner's decision (G-PUBLIC). Every number is printed in research/paper/manuscript.md. -->

**Draft, not published.**

# A skeleton screen changes what you see first, not when the content arrives

*What a frozen, single-browser benchmark measured about skeletons, prefetching and optimistic updates*

Mohamed Bechir Kefi, independent researcher.

When an interface has to wait for a server, it must decide what to show in the meantime. It can show nothing new, show a grey placeholder in the shape of the final layout (a skeleton), start the request earlier when the pointer hovers (prefetching), or show the expected result at once and correct it if the server disagrees (an optimistic update). These strategies are often recommended because they make an interface feel faster. Feeling faster and delivering usable content sooner are different quantities, and this project measured only the second.

## The question

How do loading strategies affect measurable interface responsiveness under controlled delays? The primary metric is time to usable content (TTUC): the time from a click to the first frame that shows the final, correct and usable state. Time to first feedback (TTFF) is a secondary metric. Nothing here measures how fast an interface feels to a person.

## The method

One mock page was built once, with the loading strategy as the only switch. Scripted input drove it in Google Chrome 158.0.8127.38 on one laptop. A seeded schedule injected the same delays, and on the write path the same failures, into every strategy, so each trial could be paired with its blank-baseline twin. The protocol, including the hypotheses, metrics, seeds and decision rules, was frozen by the owner before any confirmatory run. The confirmatory runs covered 6,000 interactions in the main experiments and 3,600 in a sensitivity experiment, and the seed was the independent unit.

*Figure 1 (demo page, `docs/demo.png`). Alt text: side-by-side measured traces for BLANK, SKELETON and PREFETCH at a 300 ms injected delay; SKELETON shows a placeholder after about 28 ms but reaches usable content at about the same time as BLANK, while PREFETCH reaches it earlier.*

## What was measured

**Prefetching moved the content earlier.** With a 150 ms hover lead, prefetching reduced TTUC at every delay, by 50.0 to 160.5 ms (Holm-adjusted p at most 0.00053), close to the mechanical expectation: the request simply started earlier. At L = 300 ms the median paired difference was -160.5 ms, 95% CI [-163.5, -157.1].

**An optimistic update removed the wait on success, and showed a false state on failure.** On every successful save the final state appeared about one delay earlier, for example -998.6 ms (95% CI -1012.2 to -972.6) at a 1000 ms delay. On failed saves no TTUC difference was detected, with estimates from -1.6 to 2.7 ms; no equivalence test was registered, so this is not a claim that the two are equal. The cost showed up elsewhere: on failed saves the optimistic arm displayed a state the server never held for a median of 83.4, 283.9 and 999.1 ms at L = 100, 300 and 1000 ms.

**A skeleton changed first feedback, not usable content.** At delays of 100 ms and more the skeleton was equivalent to the blank baseline within 17 ms, with estimates of -1.0 to 0.0 ms, while it lowered first feedback from about the full delay to about 28 ms. At 50 ms the skeleton was 16.7 ms faster under the main paint-time method, but this verdict changed under both alternative methods and is not robust. An exploratory decomposition places that difference in frame alignment rather than in rendering cost. No skeleton benefit is reported.

**The frozen contradiction rule was literally met.** The protocol said the main interpretation would be contradicted by a skeleton difference outside the equivalence margin or by any sign reversal under sensitivity conditions. Read literally, that criterion is met for four contrasts: the 50 ms skeleton result and three failure strata whose estimates lie within 1 ms of zero. The manuscript reports the interpretation as qualified rather than refuted, and labels that judgement as made after seeing the data.

## An open decision

One analysis choice, DEC-011, was left open: the owner chose neither reading. It fixes which test decides each hypothesis and which alternative paint methods count in the sensitivity analysis. Both readings are reported: the two test readings disagree for one of 23 contrasts, and the robustness count is 19 of 23 under one reading and 11 robust with 9 not assessed under the other.

## Limitations

These are timings in one synthetic page, one browser version and one machine, mostly headless, with synthetic delays and scripted input. The hover is scripted with a fixed lead, so the prefetch benefit says nothing about how often real users hover. Frame-scale effects depend on how a frame is timed. The manuscript is a preprint draft and has not been peer-reviewed. An AI system was used as a research and development assistant; it is not an author.

## Reproducibility

Code, frozen protocols, raw results with checksums, experiment reports and an offline interactive page are in the project repository: https://github.com/mohamedbechirkefi/scroll-perceived-performance. Interactive demo: https://scroll-perceived-performance.kefimohamedbechir.workers.dev.
