<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# EXP-002: Read path, BLANK versus SKELETON versus PREFETCH

- Status: planned (protocol draft, awaiting owner freeze).
- Version: draft v0.1, 2026-11-24. Protocol hash: not yet recorded (computed at freeze).
- Depends on: EXP-001 completed and its checks C1, C2 and C4 passed; seed count confirmed from `sigma_d`.

## 1. Precise question

When a user opens an item whose detail arrives after an injected delay L, does a skeleton placeholder or intent-based prefetching change the time to usable content relative to a blank region?

## 2. Mechanism and rationale

A skeleton renders a placeholder of the final size immediately; it changes first feedback and, if correctly sized, avoids layout shift (WEBDEV-OCLS), but it cannot make data arrive earlier. Prefetching starts the request before the click, so the remaining wait is `max(0, d - h)`. Gap: practitioner guidance and perception studies exist (NNG-SKEL; MEJTOFT-18, metadata only), but no controlled objective comparison was found in the M0 search (not a systematic search).

## 3. Competing explanations

Placeholder rendering cost could delay content (positive Delta for SKELETON); prefetch cache lookup could add overhead; frame alignment could create artificial 8 to 17 ms steps.

## 4. Hypotheses and estimand

- Estimand: `Delta_s(L)` = median over seeds of the per-seed difference in median TTUC between arm s and `BLANK`, for s in {SKELETON, PREFETCH} and L in {50, 100, 300, 1000} ms: 8 primary contrasts.
- H0: `Delta_s(L) = 0`. H1: `Delta_s(L) != 0` (two-sided). Holm correction over the 8 contrasts, alpha 0.05.
- SKELETON equivalence: TOST with margin 17 ms.
- Contradiction of the expected pattern: SKELETON outside the equivalence margin, or PREFETCH Delta differing from `-min(h, L)` by more than 17 ms.

## 5. Operational definitions

TTUC, TTFF, Event Timing duration and layout shift as in `research/protocol.md`, section 3. Units: ms, layout shift is unitless. Layout shift is reported for all entries and for `hadRecentInput = false` entries.

## 6. Design

- Unit: session of K = 10 read interactions in a fresh browser context.
- Independent: arm, L. Fixed: h = 150 ms, jitter plus or minus 10%, p = 0, CPU 1x, headless.
- Seeds 1..20, same schedule across arms; arm order randomised per seed with meta-seed 20261124.
- Sample: 3 x 4 x 20 sessions = 240 sessions, 2,400 interactions.
- Budget: at most 2 hours wall-clock.

## 7. Uncertainty

95% percentile bootstrap over seeds (10,000 resamples), Wilcoxon signed-rank as secondary, raw distributions plotted.

## 8. Exclusions and stopping

Parent protocol, section 7.

## 9. Sensitivity

See EXP-004 (measurement method, CPU 4x, h in {0, 600}, headed).

## 10. Reproduction (planned)

`uv run python -m scroll.run --experiment EXP-002` (not yet implemented).
