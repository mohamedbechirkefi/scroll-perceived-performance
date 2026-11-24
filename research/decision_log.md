<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Decision log

Append-only. Each entry: id, date, decision, decided by, rationale, alternatives, consequences. Entries marked "proposed" await the owner and are not in force until the owner confirms them.

## DEC-001: Repository licence (owner decision)

- Date: 2026-11-24
- Decided by: the owner
- Status: in force
- Decision: all original material in this repository is licensed under the "SCROLL Source-Available Non-Commercial Research License v1.0" (SPDX id `LicenseRef-SCROLL-NC-Research-1.0`), with a contributor licence agreement (CLA v1.0). The licence package (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `CONTRIBUTING.md`, `.github/CODEOWNERS`, `.github/workflows/cla.yml`) was committed at the first commit.
- Rationale: the owner chose this protective licence for their own protection.
- Deviation from the master prompt: section 2 of `master_prompt.md` asks for an "owner-approved permissive code license". The owner instead chose this custom, source-available, non-commercial licence. It is not an OSI-approved open-source licence. Sessions must not change the licence files.
- Consequences: the project is "source-available", not "open source", in every public text. Third-party data and dependencies keep their own licences (recorded in `data/manifest.json` and `uv.lock`).

## DEC-002: Zero-cost publication toolchain

- Date: 2026-11-24
- Decided by: the AI assistant within the brief; confirmable by the owner
- Status: in force (tooling choice, no scientific consequence)
- Decision: there is no TeX distribution on the machine. Markdown stays the canonical source. PDFs are produced by pandoc 3.6.3 (Markdown to Typst), compiled with the `typst` Python package 0.15.0 from `/Users/bechir/research/labs/.tools/py/bin/`. `research/paper/manuscript.tex` is generated from Markdown by pandoc (`-t latex -s`) as a source artifact only; it is not compiled locally.
- Alternatives considered: installing TeX Live or Tectonic (large download, outside the tools allowed in this session); a paid typesetting service (forbidden).
- Consequences: every PDF claim in the repository must name the Typst route. A LaTeX PDF is not claimed until a TeX engine exists.

## DEC-003: Dependency lock policy

- Date: 2026-11-24
- Decided by: the AI assistant within the brief
- Status: in force
- Decision: Python dependencies are locked with uv 0.9.5 in `uv.lock`. `pyproject.toml` sets `[tool.uv] exclude-newer = "2026-11-10T00:00:00Z"` so that only distributions uploaded at least two weeks before 2026-11-24 are resolved. No `package.json` yet: the demo is not set up in M0.
- Consequences: adding or upgrading a dependency is a recorded decision.

## DEC-004 (proposed): Deterministic in-page mock transport for latency and failure injection

- Date: 2026-11-24
- Decided by: proposal, awaiting the owner
- Decision: latency and failures are injected by a seeded in-page mock transport (a pure function from `(seed, request index)` to `(delay_ms, outcome)`), not by network throttling or Playwright route handlers. The same schedule module will drive the browser harness and the demo.
- Rationale: identical schedules across arms (common random numbers), no network, offline by construction, reusable by the static demo.
- Alternatives: Playwright `page.route` with an async pause before `route.fulfill` (not documented as a delay feature on the page read on 2026-11-24); Chrome DevTools network throttling (shapes bandwidth, not per-request latency).
- Consequences: timer resolution and main-thread scheduling of the mock become a threat to construct validity, checked in EXP-001.

## DEC-005 (proposed): Browser binary for the harness

- Date: 2026-11-24
- Decided by: proposal, awaiting the owner
- Decision options: (a) download Playwright's pinned Chromium build with `playwright install chromium` (free, about 150 MB order of magnitude, unverified size), giving a version pinned with the lockfile; (b) use the installed Google Chrome 158.0.8127.38 through `channel="chrome"`, which auto-updates and can change between runs.
- Recommendation: option (a), with the browser version recorded in every run manifest.

## DEC-006: Browser for M2 exploratory runs

- Date: 2026-11-24
- Decided by: the AI assistant within the M2 brief (no downloads allowed); does not settle DEC-005
- Status: in force for exploratory runs only
- Decision: the harness drives the installed Google Chrome 158.0.8127.38 through Playwright 1.65.0 with `channel="chrome"` (DEC-005 option b). No Playwright browser build was downloaded.
- Consequences: Chrome auto-updates, so exploratory numbers are tied to the version recorded in each run manifest. DEC-005 (pinned Chromium versus installed Chrome) remains the owner's decision before the freeze. The harness reads the version from `browser.version` and records it; the protocol's stop rules do not depend on the choice.

## DEC-007 (proposed): Implementation choices that operationalise the draft protocol

- Date: 2026-11-24
- Decided by: proposal, awaiting the owner (each item changes what the confirmatory runs measure, so the owner confirms or amends before the freeze)
- Items:
  1. **Schedule function.** 32-bit MurmurHash3-finaliser chain over (seed, stream, index, field), `u = h / 2^32`; streams `read`, `write`, `decoy`. Implemented twice (JavaScript and Python), bit-identical by test.
  2. **Identical input script in every arm.** Every interaction is: pointer to a neutral point, `prepare(k)`, two frames, 50 ms pause (`pre_input_ms`), pointer over the target, wait the hover lead `h` (150 ms), press and release. Only `PREFETCH` reacts to the hover. This keeps the arms matched on input timing.
  3. **BLANK detail region collapses while empty** (`reserve_space_blank = false`), so content arrival moves the content below it; SKELETON shows a placeholder of the final box size at input. Layout-shift differences between these arms are a consequence of this design choice, not a discovery. `reserve_space_blank = true` is implemented as an alternative.
  4. **Write-path exposure split.** The literal protocol definition (time the displayed state differs from the final server state) counts BLANK's wait for confirmation on success. The implementation reports it as `wrong_state_ms` and splits it into `stale_state_ms` (showing the pre-input server state) and `false_state_ms` (showing a state the server never held, which only an optimistic rollback produces).
  5. **Primary paint time** is `performance.now()` in the second `requestAnimationFrame` callback after the DOM commit; alternatives recorded per trial: the first rAF frame timestamp (`raf1`) and Element Timing `renderTime` (read path). S1 can therefore be computed from the same runs.
  6. **Trial end.** A trial finalises `settle_ms` after both the response and the last painted frame; the layout-shift window is `[t_in, t_final + settle_ms]`.
- Consequences: recorded in `progress.md` (M2) with the EXP-001 exploratory measurements that bear on each item.

## DEC-008 (proposed): Protocol amendments suggested by the EXP-001 exploratory run

- Date: 2026-11-24
- Decided by: proposal, awaiting the owner. The draft protocol was not changed; the owner decides before the freeze (G-FREEZE).
- Evidence: exploratory run `EXP-001-20261124T161058Z` (journal J-0003; `results/exploratory/EXP-001/EXP-001-20261124T161058Z/report/report.md`). Exploratory, five seeds, noisy machine; these are planning observations, not findings.
- Proposals:
  - **A1. Pair at the trial level inside each seed.** The draft estimand differences per-seed medians (`median_k TTUC_s - median_k TTUC_BLANK`). Because trial k has the same scheduled delay in every arm, the per-seed median of trial-matched differences (`median_k [TTUC_s,k - TTUC_BLANK,k]`) removes the delay jitter. In the exploratory run, SKELETON minus BLANK at L = 1000 ms gave per-seed values with SD 9.3 ms and a median of -10.3 ms under the draft estimand, against SD 0.5 ms and values between -0.9 and 0.4 ms with trial-level pairing (computed ad hoc in the M2 session, not by the report generator). The draft estimand can therefore manufacture an apparent effect near the 17 ms margin. The seed stays the independent unit.
  - **A2. Stratify the write path by outcome when p > 0.** With K = 5 and p = 0.5, failures per session were 4, 4, 2, 3 and 0 across seeds, so per-seed medians switch between the success and the failure regime (sigma_d 498 ms at L = 1000 ms). Proposal: primary write-path contrasts at p > 0 are computed separately for success and failure trials (trial-matched, A1), and the mixed median becomes secondary; alternatively raise K. The failure schedule was identical across arms (common random numbers verified).
  - **A3. Hover lead jitter in the harness.** The scripted hover-to-click lead was 153 to 375 ms (target 150 ms; median 154.4 ms) because the Python-side wait overshoots under machine load; this moved one PREFETCH seed median by about 50 ms. Proposal: record the actual lead (already done) and either drive the click from an in-page timer or exclude trials whose actual lead deviates from h by more than 25 ms (a pre-specified exclusion rule).
  - **A4. Event Timing duration is mostly unobservable.** 72 to 88% of trials per cell fell under the 16 ms observer threshold. Proposal: keep it as a descriptive secondary, add `input_to_handler_ms` (already recorded) and do not base any contrast on it.
  - **A5. Seed count.** With A1, sigma_d was at most 7.2 ms for the read-path contrasts and 3.7 to 47 ms for p = 0 write contrasts (the OPTIMISTIC contrast inherits BLANK's delay jitter, about 50 ms at L = 1000 ms, against an effect near -950 ms). Twenty seeds exceed the protocol 5.1 requirement for every contrast whose relevant margin is 17 ms (the SKELETON equivalence test). Under the draft estimand, PREFETCH at L = 1000 ms had sigma_d 22.5 ms (95% bootstrap upper bound 28.0 ms, n required 14 to 22), right at the protocol's 28 ms trigger. Recommendation: keep 20 seeds and adopt A1; if A1 is rejected, raise to 25 seeds.
  - **A6. Runtime budget.** EXP-001 took 651.6 s for 350 interactions (planning estimate about 15 min). Projected from this run: EXP-002 65 min, EXP-003 104 min, EXP-004 about 117 min (S2 and S4 projections ignore throttling and headed-mode cost). All within the protocol's per-experiment budgets; no matrix cut needed.
  - **A7. Degenerate cell.** PREFETCH at L = 100 ms with h = 150 ms has residual wait 0 by construction (h exceeds the maximum delay), so it tests only rendering overhead. In EXP-002 this also holds at L = 50 ms. This is expected but should be stated in the frozen protocol.
- Also for the owner: DEC-005 (browser binary) and DEC-007 (implementation choices) remain open.
