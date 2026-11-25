<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
<!-- Draft for LinkedIn (master prompt 11.7). Not published; publication is the owner's decision (G-PUBLIC). Every number is printed in research/paper/manuscript.md. -->

**Draft, not published.**

Does a skeleton screen deliver content sooner, or only feedback?

I built one mock page with four loading strategies (blank, skeleton, prefetch, optimistic update) and measured them in one browser under the same seeded delays, with a protocol frozen before any confirmatory run.

One defensible finding: at delays of 100 ms and more, the skeleton reached usable content at the same time as the blank page, within 17 ms (estimates -1.0 to 0.0 ms), while it showed first feedback after about 28 ms. Prefetching and optimistic updates did move usable content earlier, and on failed saves the optimistic arm showed a false state for about the whole delay.

Caveat: these are objective timings in one synthetic page, one browser and one machine, not a measure of how fast an interface feels. A 50 ms skeleton difference was not robust, and one analysis decision is still pending. The manuscript is a preprint draft, not peer-reviewed.

Manuscript, reports and an offline interactive page: [OWNER PLACEHOLDER: repository URL, not yet published]. Demo: [OWNER PLACEHOLDER: demo URL, not yet published].
