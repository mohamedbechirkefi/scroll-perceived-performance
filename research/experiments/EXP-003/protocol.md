<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# EXP-003: Write path, BLANK (pessimistic) versus OPTIMISTIC with failure injection

- Status: planned (protocol draft, awaiting owner freeze).
- Version: draft v0.1, 2026-11-24. Protocol hash: not yet recorded (computed at freeze).
- Depends on: EXP-001 completed and check C3 (rollback correctness) passed.

## 1. Precise question

When a user saves an item and the mutation can fail with probability p after a delay L, how does an optimistic update change the time to the final correct state, and how much wrong-state exposure does it create, relative to waiting for confirmation?

## 2. Mechanism and rationale

An optimistic update shows the expected state immediately and rolls back on failure (REACT-OPT semantics). On success it reaches the final state in about one frame; on failure it reaches it only after the failure is known, having displayed a wrong state for about d. The expected benefit therefore falls with p.

## 3. Competing explanations

Rollback re-rendering cost; error-message insertion causing layout shift; scheduling of the confirmation callback.

## 4. Hypotheses and estimand

- Estimand: `Delta(L, p)` = median over seeds of the per-seed difference in median TTUC between `OPTIMISTIC` and `BLANK`, for L in {100, 300, 1000} ms and p in {0, 0.1, 0.3}: 9 primary contrasts.
- H0: `Delta(L, p) = 0`. H1: `Delta(L, p) != 0` (two-sided). Holm correction over 9 contrasts.
- Note: the per-seed median over K = 10 interactions hides failures when p is low. Therefore TTUC is also analysed separately for success and failure trials (secondary), and wrong-state exposure is the key secondary metric.
- Contradiction of the expected pattern: Delta not decreasing in magnitude as p rises, or rollback correctness below 1.0.

## 5. Operational definitions

`research/protocol.md`, section 3. Wrong-state exposure: total ms after input during which the displayed toggle state differs from the final server-consistent state.

## 6. Design

- Unit: session of K = 10 save interactions in a fresh context.
- Independent: arm, L, p. Fixed: jitter plus or minus 10%, CPU 1x, headless.
- Seeds 1..20, identical failure and delay schedules across arms.
- Sample: 2 x 3 x 3 x 20 = 360 sessions, 3,600 interactions.
- Budget: at most 3 hours wall-clock.

## 7. Uncertainty, exclusions, stopping

As in the parent protocol, sections 6 and 7. Rollback correctness below 1.0 triggers the stop rule.

## 8. Accessibility checks (project-specific verification)

Error messages are announced through an ARIA live region; focus stays on the toggle after rollback. Checked by automated assertions, reported as pass or fail per arm (not a statistical outcome).

## 9. Reproduction (planned)

`uv run python -m scroll.run --experiment EXP-003` (not yet implemented).
