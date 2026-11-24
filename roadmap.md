<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# SCROLL roadmap

Target: five focused development days (planning estimate, never a reason to weaken evidence). Effort in days. Status values: done, in progress, planned, blocked. Updated 2026-11-24 (session M2).

| ID | Milestone | Depends on | Acceptance criteria (gate) | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|---|---|
| M0 | Bootstrap and feasibility | none | Control files exist; feasibility audit recorded with commands; sources and licences audited; scope, cost (zero) and exclusions stated; registry, manuscript skeleton and draft experiment protocols exist; zero-cost toolchain confirmed (11.6). Gate: the owner can understand the question, cost and exclusions. | P0 | 0.5 | done (pending owner reading) | none |
| M1 | Research and preregistration | M0 | Literature search extended and documented; formal model; baselines; protocol and EXP-001..004 protocols reviewed; fixture manifest; EXP-001 exploratory smoke run informs seed count; owner freezes confirmatory protocols with recorded hashes (11.6). Gate: protocol frozen before confirmatory runs; exploratory results visibly separated. | P0 | 0.75 | in progress (drafts written; EXP-001 exploratory run done, amendments proposed in DEC-008) | owner freeze (G-FREEZE); DEC-004, DEC-005, DEC-007, DEC-008 decisions |
| M2 | Core implementation | M1 draft (implementation may proceed before the freeze) | Seeded schedule module, mock interface with BLANK first, then SKELETON, PREFETCH, OPTIMISTIC; browser harness; versioned JSON result schema with validation; run manifests; report generator (11.6); unit, property, golden and integration tests run and recorded. Gate: correctness before UI polish. | P0 | 1.25 | done for exploratory use (2026-11-24): all components exist and 137 tests pass; EXP-001 run exploratorily. Open: owner review of DEC-005, DEC-007 and DEC-008 before the freeze | DEC-005 unresolved (installed Chrome used, DEC-006) |
| M3 | Experiments | M1 freeze, M2 | EXP-001 smoke, then frozen EXP-002, EXP-003, EXP-004 matrices complete or failures documented; raw machine-readable results retained; individual reports written as each experiment finishes, with failures and deviations (11.6). Gate: complete matrix or documented failure; no silently dropped runs. | P0 | 1.0 | planned | M1 freeze |
| M4 | Interpretation | M3 | Confounders and sensitivity examined; expected versus observed; claims register filled and audited; experiment reports finished; manuscript synthesised with contradictory results (11.6). Gate: every number maps to result ID, config and figure; every external claim to a verified source. | P0 | 0.75 | planned | M3 |
| M5 | Interactive experience | M4 (results), M2 (engine) | Static offline side-by-side benchmark with latency slider and traces; accessibility checks; demo, paper, reports and articles use identical verified results (11.6). Gate: offline after load, responsive, keyboard usable, no fabricated data, no runtime service. | P1 (cut first if time is short) | 0.5 | planned | Node tooling via `PATH` prefix |
| M6 | Release candidate | M4, M5 | Clean clone, locked install, tests and smoke reproduction; demo build; manifests and links verified; secret and licence scan; PDFs compiled through Typst and visually inspected; owner review checklist (11.6). Gate: verified facts only; owner approves any publication. | P0 | 0.25 | planned | owner approval (G-PUBLIC) |

## Fallbacks and cuts (in order)

1. Drop the headed-browser factor (S4) and the h = 600 ms level of EXP-004.
2. Reduce the demo to a single precomputed-trace viewer.
3. Reduce latency levels in EXP-002 to {100, 300, 1000} ms.
Never cut: the baseline, the primary metric, seeds below 10, exclusions reporting, experiment reports or the claims audit.

## Explicit exclusions

No human participants, no perception claims, no network or cloud services, no paid tools, no real or proprietary sites measured, no publication without the owner.

## M2 acceptance check (2026-11-24)

| Criterion | State |
|---|---|
| Seeded schedule module | done: `src/web/schedule.js` and `src/scroll/schedule.py`, bit-identical (Node differential test, 2,002 cases) |
| Mock interface, BLANK first, then SKELETON, PREFETCH, OPTIMISTIC | done: `src/web/` |
| Browser harness | done: `src/scroll/harness.py`, installed Chrome 158 (DEC-006) |
| Versioned JSON result schema, validated at export and import | done: `result-1.0.0`, `config-1.0.0` |
| Run manifests | done: config hash, seeds, git revision and dirty flag, versions, OS, CPU, load average, runtime, peak RSS (Python process only) |
| Report generator (tables, figures, PDF through pandoc and Typst) | done: `python -m scroll report --pdf` |
| CLI smoke, run (refuses confirmatory while unfrozen), report, test | done |
| Unit, property, golden, differential, integration and browser tests run | done: 137 passed, 0 failed (`progress.md`) |
| Experiment reports (11.3) | not done: M3 work; EXP-001 has a generated run report only |
