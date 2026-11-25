<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Literature and source review (M0, not systematic)

Status: initial scoping review from session M0 (2026-11-24). It is not a systematic review: no documented search protocol, a handful of web searches only. Every source marked "opened" was fetched on 2026-11-24 through a web fetch tool that returns a model-written summary of the page, not the raw text. Claims below are therefore limited to what those summaries stated, and must be re-checked against the full text before they enter the manuscript.

## 1. Sources opened (2026-11-24)

| Key | Source | URL / DOI | What it supports here |
|---|---|---|---|
| W3C-ET | W3C, *Event Timing API*, Working Draft dated 13 Nov 2026, editor M. Mocny (former editors N. Peña Moreno, T. Dresser) | https://www.w3.org/TR/event-timing/ | Event duration runs from the event timestamp to the next rendering update after dispatch; rounded to 8 ms; default exposure threshold 104 ms; observer `durationThreshold` minimum 16 ms; first input always reported. |
| WICG-LI | WICG, *Layout Instability API*, Draft Community Group Report dated 8 Nov 2026, editor M. Mocny | https://wicg.github.io/layout-instability/ | Layout shift value = impact fraction x distance fraction; `hadRecentInput` true when an excluding input (mousedown, keydown, pointerdown, change) occurred under 500 ms earlier; `sources` attribution. Not a W3C standard. |
| WEBDEV-INP | J. Wagner, B. Pollard, "Interaction to Next Paint (INP)", web.dev, published 6 May 2022, updated 2 Sep 2025 | https://web.dev/articles/inp | Interaction latency phases (input delay, processing, presentation delay); thresholds 200 ms / 500 ms at the 75th percentile; one worst interaction ignored per 50. |
| WEBDEV-CLS | M. Mihajlija, P. Walton, "Cumulative Layout Shift (CLS)", web.dev (no update date in the fetched text) | https://web.dev/articles/cls | Session windows (gap under 1 s, window at most 5 s); thresholds 0.1 / 0.25; shifts within 500 ms of discrete input can be excluded. |
| WEBDEV-OCLS | A. Osmani, B. Pollard, "Optimize Cumulative Layout Shift", web.dev, published 5 May 2020, updated 7 Feb 2025 | https://web.dev/articles/optimize-cls | Reserving space with a placeholder or skeleton UI to avoid shifts from late content; content arriving more than 500 ms after input counts toward CLS. This is the mechanism that EXP-002 tests for skeletons. |
| MDN-LCP | MDN, "Largest Contentful Paint API" | https://developer.mozilla.org/en-US/docs/Web/API/Largest_Contentful_Paint_API | LCP entries (`renderTime`, `loadTime`, `element`); reporting stops at the first scroll or input, so LCP cannot measure post-interaction content. Motivates a custom "time to usable content" marker. |
| NIELSEN-93 | J. Nielsen, "Response Times: The 3 Important Limits", Nielsen Norman Group, 1 Jan 1993 (excerpt of *Usability Engineering*, ch. 5), web section added 2014 | https://www.nngroup.com/articles/response-times-3-important-limits/ | 0.1 s, 1 s and 10 s limits. Used only to choose latency levels, not as evidence about perception in this study. |
| NNG-SKEL | S. Tankala, "Skeleton Screens 101", Nielsen Norman Group, 4 Jun 2023, reviewed 2 Sep 2026 | https://www.nngroup.com/articles/skeleton-screens/ | Practitioner guidance: skeletons for full-page loads under about 10 s, no indicator under 1 s. Practitioner source, not empirical evidence. |
| MEJTOFT-18 (metadata only) | T. Mejtoft, A. Långström, U. Söderström, "The effect of skeleton screens: Users' perception of speed and ease of navigation", *Proc. 36th European Conference on Cognitive Ergonomics (ECCE 2018)*, ACM, pp. 1-4, 5 Sep 2018 | https://doi.org/10.1145/3232078.3232086 (metadata opened via https://api.crossref.org/works/10.1145%2F3232078.3232086) | Bibliographic metadata verified. **Full text not opened: findings unverified.** Secondary summaries say skeletons scored higher on perceived speed than spinners; one secondary source says the differences were not significant. Neither claim may be cited as read. |
| REACT-OPT | React documentation, `useOptimistic` | https://react.dev/reference/react/useOptimistic | Optimistic state renders only while an action is pending; on failure the UI falls back to the committed value. Defines the rollback semantics the OPTIMISTIC arm imitates. The page did not state the introducing React version (unverified: React 19). |
| WEB-VITALS | GoogleChrome/web-vitals repository | https://github.com/GoogleChrome/web-vitals | Apache-2.0; `onINP` default `durationThreshold` 40 ms; attribution build. Candidate reference implementation for a differential check of our INP-like measurement. |
| PW-NET, PW-CTX, PW-REL | Playwright docs, "Network" and "BrowserContext"; GitHub releases page | https://playwright.dev/docs/network ; https://playwright.dev/docs/api/class-browsercontext ; https://github.com/microsoft/playwright/releases | `page.route`/`route.fulfill`; `browserContext.setOffline(offline)`; `newCDPSession` (Chromium only). Releases page listed v1.65.0 (5 Nov) and v1.65.1 (13 Nov). The licence was not shown on the fetched pages (unverified: Apache-2.0). |
| CRUX-METH | Chrome UX Report methodology | https://developer.chrome.com/docs/crux/methodology | CrUX datasets are licensed CC BY 4.0; aggregated field histograms per origin and page. |

## 2. Sources not opened (unverified, do not cite as read)

- Chrome DevTools Protocol `Emulation.setCPUThrottlingRate`: two fetches returned only a redirect notice. Its parameters and status are unverified.
- Viget, "A Bone to Pick with Skeleton Screens" (https://viget.com/articles/a-bone-to-pick-with-skeleton-screens): seen only as a search result. Informal test, unverified.
- Any peer-reviewed study comparing optimistic updates, prefetching and skeletons on objective timing. None was found in this short search; this is not evidence that none exists.
- Classic statistics references for the bootstrap (Efron and Tibshirani) and for TOST equivalence testing (Schuirmann; Lakens): not opened in M0. Required before the manuscript cites them.

## 3. Known work and the narrow contribution (draft)

What is known (from opened sources): browser standards define how input-to-next-paint latency and layout shifts are measured (W3C-ET, WICG-LI, WEBDEV-INP, WEBDEV-CLS). Practitioner guidance recommends skeletons and reserved space to reduce layout shift (WEBDEV-OCLS, NNG-SKEL). Perception studies exist (MEJTOFT-18, metadata only) but measure subjective ratings.

Gap this project can address within five days: a controlled, reproducible, open-protocol benchmark that holds the interface, data and latency schedule fixed and varies only the loading strategy, then reports objective timings (time to usable content, time to first feedback, layout shift, rollback behaviour) with paired uncertainty. The contribution is methodological and descriptive about one mock interface in one browser. It does not measure perception (claims boundary, `master_prompt.md` section 10). No novelty claim is made until the literature search is extended in M1.

## 4. M1 to-do

1. Open the full text of MEJTOFT-18 through a lawful free route, or keep it as metadata-only.
2. Search ACM DL, arXiv and Google Scholar for objective benchmarks of loading strategies and optimistic UI; document the search strings and dates.
3. Open and cite statistics references for paired bootstrap and equivalence testing.
4. Re-open CDP `Emulation` documentation for CPU throttling.

## 5. M6 full-text check (2026-11-25)

The nine web sources were downloaded as raw HTML with `curl` (free, no login) and converted to plain text locally; the text, not a summary, was searched and the passages behind each claim were read. Every claim in sections 1 and 2 of this review that enters the manuscript (claims register E-001 to E-007) was confirmed; the section checked for each is recorded in the claims register and in `research/publication/evidence_audit.md`, section 8. One manuscript sentence was narrowed: it had cited the NN/g skeleton article for reducing layout shift, which that article does not discuss (it discusses when skeleton screens are appropriate). MEJTOFT-18: the Semantic Scholar record reports the paper as closed access with no open PDF; no free full text was found, so it stays metadata only. Items 2 to 4 of section 4 remain open.
