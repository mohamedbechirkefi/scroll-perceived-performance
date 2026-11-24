<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# EXP-003: Write path, BLANK (pessimistic) versus OPTIMISTIC with failure injection

- Status: frozen (owner-approved 2026-11-24), not yet run. Confirmatory.
- Version: v1.0, 2026-11-24 (draft v0.1 plus the owner-approved amendments listed in section "Amendments before freeze"). Protocol hash: SHA-256 recorded in `research/freeze.json` and `research/experiment_registry.csv` (a file cannot contain its own hash).
- Parent protocol: `research/protocol.md` v1.0 (frozen).
- Depends on: EXP-001 completed and check C3 (rollback correctness) passed.

## 1. Precise question

When a user saves an item and the mutation can fail with probability p after a delay L, how does an optimistic update change the time to the final correct state, and how much wrong-state exposure does it create, relative to waiting for confirmation?

## 2. Mechanism and rationale

An optimistic update shows the expected state immediately and rolls back on failure (REACT-OPT semantics). On success it reaches the final state in about one frame; on failure it reaches it only after the failure is known, having displayed a wrong state for about d. The expected benefit therefore falls with p.

## 3. Competing explanations

Rollback re-rendering cost; error-message insertion causing layout shift; scheduling of the confirmation callback.

## 4. Hypotheses and estimand

- Estimand (amendments A1 and A2): `Delta(L, p, o)` = median over seeds of the per-seed median of trial-paired differences `TTUC_OPTIMISTIC,k - TTUC_BLANK,k`, where trial k has the same scheduled delay and outcome in both arms, computed within the outcome stratum o. At p = 0 every trial succeeds, so o = success. At p in {0.1, 0.3} the success and failure strata are separate primary contrasts. Primary contrasts: 3 (p = 0) + 3 x 2 x 2 (p > 0, two strata) = 15.
- A seed contributes to a stratum only if it has at least one paired trial in that stratum. With seeds 1..20 and K = 10 the schedule fixes this in advance: the failure stratum has 12 seeds at p = 0.1 and 18 seeds at p = 0.3; the success stratum has 20 seeds at every p.
- H0: `Delta(L, p, o) = 0`. H1: `Delta(L, p, o) != 0` (two-sided). Holm correction over the 15 primary contrasts.
- Secondary: the mixed estimand over all trials of a cell (`Delta(L, p)`, the trial-paired version of the draft estimand) and the draft seed-median estimand, both descriptive; wrong-state exposure is the key secondary metric.
- Contradiction of the expected pattern: the mixed (secondary) estimand not decreasing in magnitude as p rises, or rollback correctness below 1.0.

## 5. Operational definitions

`research/protocol.md`, section 3 (Event Timing duration descriptive only, amendment A4). Wrong-state exposure: total ms after input during which the displayed toggle state differs from the final server-consistent state.

## 6. Design

- Unit: session of K = 10 save interactions in a fresh context.
- Independent: arm, L, p. Fixed: jitter plus or minus 10%, CPU 1x, headless, installed Google Chrome with its version recorded (amendment A5).
- Seeds 1..20, identical failure and delay schedules across arms.
- Sample: 2 x 3 x 3 x 20 = 360 sessions, 3,600 interactions.
- Budget: at most 3 hours wall-clock.

## 7. Uncertainty, exclusions, stopping

As in the parent protocol, sections 6 and 7. Rollback correctness below 1.0 triggers the stop rule.

## 8. Accessibility checks (project-specific verification)

Error messages are announced through an ARIA live region; focus stays on the toggle after rollback. Checked by automated assertions, reported as pass or fail per arm (not a statistical outcome).

## 9. Reproduction (planned)

`.venv/bin/python -m scroll run --config experiments/EXP-003.json` (frozen configuration; its hash is in `research/freeze.json`). Editorial correction at freeze: the draft named a command that was never implemented.

## Amendments before freeze (owner-approved 2026-11-24)

- A1 (trial-level pairing within seed) and A2 (outcome strata at p > 0, Holm family of 15): section 4.
- A3 (hover-lead control): not applicable on the write path (no arm reacts to the hover; the lead is not recorded).
- A4 (Event Timing descriptive only): section 5.
- A5 (installed Google Chrome, version recorded): section 6.
- A6 (20 seeds): section 6 unchanged, seeds 1..20 confirmed.
- Details and quotes: `research/protocol.md`, section 11; `research/decision_log.md`, DEC-009.
