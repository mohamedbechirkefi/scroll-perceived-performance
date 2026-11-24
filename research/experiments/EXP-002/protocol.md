<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# EXP-002: Read path, BLANK versus SKELETON versus PREFETCH

- Status: frozen (owner-approved 2026-11-24), not yet run. Confirmatory.
- Version: v1.0, 2026-11-24 (draft v0.1 plus the owner-approved amendments listed in section "Amendments before freeze"). Protocol hash: SHA-256 recorded in `research/freeze.json` and `research/experiment_registry.csv` (a file cannot contain its own hash).
- Parent protocol: `research/protocol.md` v1.0 (frozen).
- Depends on: EXP-001 completed and its checks C1, C2 and C4 passed; seed count confirmed from `sigma_d`.

## 1. Precise question

When a user opens an item whose detail arrives after an injected delay L, does a skeleton placeholder or intent-based prefetching change the time to usable content relative to a blank region?

## 2. Mechanism and rationale

A skeleton renders a placeholder of the final size immediately; it changes first feedback and, if correctly sized, avoids layout shift (WEBDEV-OCLS), but it cannot make data arrive earlier. Prefetching starts the request before the click, so the remaining wait is `max(0, d - h)`. Gap: practitioner guidance and perception studies exist (NNG-SKEL; MEJTOFT-18, metadata only), but no controlled objective comparison was found in the M0 search (not a systematic search).

## 3. Competing explanations

Placeholder rendering cost could delay content (positive Delta for SKELETON); prefetch cache lookup could add overhead; frame alignment could create artificial 8 to 17 ms steps.

## 4. Hypotheses and estimand

- Estimand (amendment A1): `Delta_s(L)` = median over seeds of the per-seed median of trial-paired differences `TTUC_s,k - TTUC_BLANK,k` (trial k shares its scheduled delay across arms), for s in {SKELETON, PREFETCH} and L in {50, 100, 300, 1000} ms: 8 primary contrasts. The draft estimand (difference of per-seed session medians) is reported as a secondary, descriptive analysis.
- H0: `Delta_s(L) = 0`. H1: `Delta_s(L) != 0` (two-sided). Holm correction over the 8 contrasts, alpha 0.05.
- SKELETON equivalence: TOST with margin 17 ms.
- Contradiction of the expected pattern: SKELETON outside the equivalence margin, or PREFETCH Delta differing from `-min(h, L)` by more than 17 ms.

## 5. Operational definitions

TTUC, TTFF, Event Timing duration and layout shift as in `research/protocol.md`, section 3. Event Timing duration is descriptive only (amendment A4). Units: ms, layout shift is unitless. Layout shift is reported for all entries and for `hadRecentInput = false` entries.

## 6. Design

- Unit: session of K = 10 read interactions in a fresh browser context.
- Independent: arm, L. Fixed: h = 150 ms, jitter plus or minus 10%, p = 0, CPU 1x, headless, installed Google Chrome with its version recorded (amendment A5).
- Seeds 1..20, same schedule across arms; arm order randomised per seed with meta-seed 20261124.
- Sample: 3 x 4 x 20 sessions = 240 sessions, 2,400 interactions.
- Budget: at most 2 hours wall-clock.

## 7. Uncertainty

95% percentile bootstrap over seeds (10,000 resamples), Wilcoxon signed-rank as secondary, raw distributions plotted.

## 8. Exclusions and stopping

Parent protocol, section 7, including the hover-lead control (amendment A3): a trial whose measured hover-to-click lead deviates from h = 150 ms by more than 25 ms is excluded in every arm.

## 9. Sensitivity

See EXP-004 (measurement method, CPU 4x, h in {0, 600}, headed).

## 10. Reproduction (planned)

`.venv/bin/python -m scroll run --config experiments/EXP-002.json` (frozen configuration; its hash is in `research/freeze.json`). Editorial correction at freeze: the draft named a command that was never implemented.

## Amendments before freeze (owner-approved 2026-11-24)

- A1 (trial-level pairing within seed): section 4.
- A3 (hover-lead control, 25 ms tolerance): section 8.
- A4 (Event Timing descriptive only): section 5.
- A5 (installed Google Chrome, version recorded): section 6.
- A6 (20 seeds): section 6 unchanged, seeds 1..20 confirmed.
- Details and quotes: `research/protocol.md`, section 11; `research/decision_log.md`, DEC-009.
