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

## DEC-009: Owner-approved amendments and protocol freeze v1.0 (G-FREEZE)

- Date: 2026-11-24
- Decided by: the owner (approval); applied by the AI assistant under the freeze brief of the same day
- Status: in force
- Owner's words (approvals file of 2026-11-24, labs coordination folder): for SCROLL, "Pair trials one to one within each seed.", "Split the p > 0 write path by outcome.", "Control the hover-to-click lead.", "Event Timing is descriptive only.", "Use the installed Google Chrome, with its version recorded.", "20 seeds." Common decisions: C1 synthetic data only; C2 PDFs through pandoc and Typst; C3 authorship "Mohamed Bechir Kefi", no affiliation, the AI disclosed as a research and development assistant, not as an author; C4 disclosure of exploratory primary values seen before the freeze.
- Decision: research/protocol.md becomes v1.0 (frozen) with amendments A1 to A6 (protocol section 11); EXP-002, EXP-003 and EXP-004 protocols become v1.0 (frozen); EXP-001 stays exploratory and is not frozen. The freeze record `research/freeze.json` holds the SHA-256 of the parent protocol, of each confirmatory protocol and of each confirmatory configuration (file hash and canonical config hash), the code revision, the owner's quoted approval, C1 to C4 and the C4 disclosure.
- Resolves: DEC-005 (option b, installed Chrome); DEC-008 A1 to A5 (A5 of DEC-008 is the seed count, A6 of the protocol).
- Implementation choices made in applying the approval:
  - A3: of the two options in DEC-008 A3, the pre-specified exclusion rule (25 ms tolerance, the value stated in DEC-008) was applied. The in-page timer option would replace the trusted Playwright click by a script-dispatched one, which changes `t_in` and removes the Event Timing entry. The rule applies to read-path trials in every arm; the write path records no hover lead and no write arm reacts to it.
  - A2: the Holm family of EXP-003 grows from 9 to 15 primary contrasts (3 at p = 0, 12 for the two strata at p > 0). The failure-stratum seed counts are fixed by the schedule (12 at p = 0.1, 18 at p = 0.3, for seeds 1..20 and K = 10).
  - Editorial at freeze: the reproduction commands in the EXP protocols now name the implemented CLI; the EXP-004 interaction counts, left "fixed at freeze" in the draft, are stated from the configurations (3,600 interactions).
- Not in this approval: DEC-007 (implementation choices) stays as implemented in the frozen code revision but was not separately listed; DEC-008 A6 (budget) and A7 (degenerate PREFETCH cells at L below h) were not listed and were not applied as protocol changes.
- Freeze guard: the runner accepts a confirmatory config only if the parent protocol hash, the experiment protocol hash (freeze record and registry) and the config hash all match the freeze record; tests cover acceptance and refusal.
- Consequences: any later change to a frozen protocol or config is refused by the runner and requires a new owner decision and a dated deviation. Confirmatory runs (M3) are scheduled by the coordinator on a quiet machine.

## DEC-010: Owner ratification of the hover-lead control implementation (A3)

- Date: 2026-11-24
- Decided by: the owner ("Approve all", 2026-11-24, second-round approvals file, section 3); recorded by the AI assistant
- Status: in force
- Owner's words: "Approve all", applied to the coordinator's item for SCROLL: "The lead control is implemented as excluding read trials whose hover-to-click lead is more than 25 ms off target."
- Decision: the implementation choice made under DEC-009 for amendment A3 (pre-specified exclusion of read-path trials, every arm, when the measured hover-to-click lead deviates from h by more than 25 ms or no hover was recorded; the in-page timer option not adopted) is ratified by the owner.
- Consequences: no change to the frozen protocol, configurations or code; no frozen hash changes. The ratification is listed under `ratified_follow_on_choices` in `research/freeze.json`.

## DEC-011: Confirmatory inference wiring and quiet-machine rule, fixed before any confirmatory output (M3)

- Date: 2026-11-25
- Decided by: the AI assistant under the M3 brief (owner's "Start next", 2026-11-25); recorded and committed before the first confirmatory run. Not a protocol change: no frozen file or hash changes.
- Finding: the frozen code computes the primary estimand and its 95% bootstrap interval (`analysis.trial_paired_contrasts`) and contains the Wilcoxon, Holm and TOST primitives (`stats.py`), but no code applied the Holm correction, the TOST or the verdicts of the frozen protocols. Without new code the frozen decision rules could not be applied.
- Decision: new module `src/scroll/inference.py` (tests `tests/test_inference.py`) composes only frozen pieces, with the following readings of the frozen text, fixed before data:
  1. The hypothesis test is the two-sided Wilcoxon signed-rank test on the per-seed values, the only test the protocol names; Holm is applied to its p-values over the experiment's primary family (EXP-002: 8; EXP-003: 15). H0 is rejected when the Holm-adjusted p is below 0.05. Whether the unadjusted 95% bootstrap interval excludes 0 is reported beside it; where the two readings disagree, the disagreement is reported and not resolved in favour of either. This reading is flagged to the owner.
  2. SKELETON: TOST with margin 17 ms through the 90% bootstrap interval (`stats.tost_bootstrap`), unadjusted, as protocol section 6 states.
  3. Failed cell (protocol section 7): a (cell, arm) group with more than 5% of its trials excluded or lost. A contrast touching a failed group receives no verdict and enters the Holm family with p = 1, so the family size stays the frozen one. This is at least as strict as pooling the arms of a cell.
  4. PREFETCH contradiction: the point estimate differs from `-min(h, L)` by more than 17 ms. EXP-003 contradiction: the mixed (secondary) estimand does not strictly decrease in magnitude from p = 0 to 0.1 to 0.3 at a given L, or rollback correctness below 1.0.
  5. EXP-004: a verdict is robust only if the sign of the point estimate (SKELETON: the equivalence verdict; its sign is also shown) is the same at every available factor level. S1 uses both alternative paint methods the frozen code records (`raf1` on both paths, Element Timing on the read path); neither is selected over the other. The alternative TTFF method is not recorded by the frozen code, so S1 for TTFF cannot be computed (gap). The main level is the frozen EXP-002 or EXP-003 estimate (20 seeds).
- Quiet-machine rule (protocol section 10, risk 3: mains power, other heavy jobs stopped, load average recorded; no numeric threshold is frozen): before each confirmatory run, mains power and a 1-minute and 5-minute load average both below 3.0 on this 10-core machine, with no other lab agent running (coordinator's exclusive window). Otherwise wait and recheck every 5 minutes, logged; stop after about 2 hours. Runs execute under `nice -n 10` (M3 brief). Readings are recorded per run.
- Consequences: these choices cannot depend on confirmatory data, which did not exist when they were committed. The frozen protocols, configurations and hashes are unchanged.

## DEC-012: M3 execution record, deviations and gaps

- Date: 2026-11-25
- Decided by: the AI assistant under the M3 brief; recorded for the owner. No frozen file, configuration, seed, exclusion rule or analysis code was changed after confirmatory output existed.
- Execution: EXP-002, EXP-003 and the EXP-004 configurations S2, S3 and S4 ran in full through the run guard at code revision `b5a72c3` (clean tree; the run path is identical to the freeze revision `b4bd25b`, the only code difference being the new `src/scroll/inference.py` of DEC-011). Chrome 158.0.8127.38 throughout (no version change within or between experiments). The quiet rule of DEC-011 held at every run start; no waiting was needed.
- Deviations and gaps:
  1. Runs executed under `nice -n 10` (M3 brief). The protocol does not mention process priority; EXP-001 of 2026-11-24 ran without it. Recorded as a run condition.
  2. The frozen report generator and run manifest contain fixed text stating that other agents were running ("Other processes (including other agents) were running during the run"; manifest `notes`). For these runs it is inaccurate: the coordinator's window was exclusive and the measured load averages are recorded. The text was not edited (frozen code); the experiment reports state the actual conditions.
  3. EXP-004 S1 for TTFF: the frozen code records alternative paint times only for the usable-content frame (`ttuc_raf1_ms`, `ttuc_element_ms`), not for the first-feedback frame, so TTFF under the alternative method cannot be computed. Not run; gap reported.
  4. EXP-004 S1 alternative: the protocol says the alternative was to be "chosen in EXP-001"; no choice was recorded. Both recorded alternatives are reported and both count in the robustness rule (DEC-011 item 5), so no alternative was selected after the data.
  5. The `inference.json` files written inside the three EXP-004 run folders apply Holm over those runs' own contrasts. EXP-004 has no frozen Holm family; those values are not part of the frozen analysis and are not reported as verdicts.
  6. Two campaign log files were written to a scratch folder shared with other agents; the first two (`exp001.log`, `campaign.sh`) were created with overwrite semantics before the sharing was noticed. Nothing inside this repository was affected. Reported to the coordinator.
- For the owner: the Holm reading of DEC-011 item 1 (Wilcoxon p-values) disagrees with the unadjusted 95% bootstrap interval for one contrast, EXP-002 SKELETON at L = 300 ms (interval excludes 0; Holm-adjusted p 0.27). Both are reported; the TOST equivalence verdict for that contrast is unaffected.

## DEC-013: M4 interpretation, evidence audit and manuscript

- Date: 2026-11-25
- Decided by: the AI assistant under the M4 brief. Authority for starting M4: owner, 2026-11-25, "Next" (`labs/_shared/owner-approvals-2026-11-25d.md`, item 2). No frozen protocol, configuration, seed, estimator or verdict was changed; nothing was pushed.
- No new measurement. Other lab agents were running, so the machine was not quiet. No browser timing run was made, exploratory or otherwise. Sensitivity and confounder work used committed raw results only: `scripts/m4_reanalysis.py` (X1 to X7), outputs in `results/exploratory/M4-REANALYSIS/` with a manifest of input and output SHA-256, labelled exploratory and post hoc (journal J-0009).
- DEC-011 is not decided here. It awaits the owner's review (owner, 2026-11-25, "Next": "SCROLL: DEC-011" stays open). Both test readings are shown in the manuscript tables (they differ for 1 of 23 contrasts). The S1 composition, which is also part of DEC-011, is shown under both readings: 19 of 23 robust (DEC-011 item 5), or 11 robust, 1 method-dependent, 2 condition-dependent and 9 not assessed (Element Timing only, X6).
- The 50 ms SKELETON effect is presented as not robust, as the M3 report concluded. Review pass 2 (R-2) removed the M3 wording that called it an artefact, because its direction is the same under all three paint methods; no benefit is claimed.
- The frozen contradiction criterion (protocol section 4) is reported as literally met for four contrasts; the qualified reading is labelled post hoc (review pass 2, R-3).
- Report corrections: eight prose statements in the EXP-002, EXP-003 and EXP-004 reports did not match committed outputs and were corrected in place with the M3 text noted (`research/publication/evidence_audit.md`, section 3). No verdict or claim value changed. The EXP-004 correction used the Edit tool; the EXP-002 and EXP-003 corrections were applied with a short Python replacement after the Edit tool had accepted the EXP-004 edit (no tool refused them).
- EXP-001 report: composed in M4 from committed outputs. The Write tool refused it (subagents cannot write report files), so it was returned to the coordinator as text.
- Claims register: restructured with the columns result id, configuration hash, figure or table, and manuscript section; C-030 to C-046 and external claims E-001 to E-008 added. Three bibliography entries added from the M0 source list.
- Owner-only facts (repository URL, funding, competing interests, author line) stay visible placeholders in the manuscript; listed in `progress.md`.
- Manuscript title proposed: "Skeletons, prefetching and optimistic updates under controlled delays: time to usable content in a single-browser benchmark". Awaits the owner's approval.

## DEC-014: M5 interactive results page, sandbox scope and text consistency

- Date: 2026-11-25
- Decided by: the AI assistant under the M5 brief and its timing addendum. Authority: owner, 2026-11-25, "Next" (second) (`labs/_shared/owner-approvals-2026-11-25e.md`), which starts "M5 (interactive experience) in SCALE, SCROLL and TOKEN, under the same brief and stack as the first \"Next\"". The stack is the one `labs/_shared/owner-approvals-2026-11-25d.md` names: "The master prompt's default stack is used: TypeScript, React and Vite. Versions are pinned and come from the shared template, `labs/_shared/demo-template/`, which was verified on 2026-11-25." No pinned version was changed and no dependency was added.
- No measurement. M5 ran no benchmark, no browser timing run and no model. The full test suite launches Chrome for its functional browser tests, which record no timing result.
- Exported data: `scripts/export_demo_data.py` writes `demo/public/data/results.json` (schema `lab-demo-results` 1.0.0) from committed files only: the frozen inference outputs of EXP-002 and EXP-003, the EXP-004 sensitivity outputs, two committed cell summaries, the committed exploratory tables X6 and X7, the registry, the claims register, the artifact manifest and the limitations. `code_revision` is `b5a72c32202cb66a17341a5022ad29e9344506b6`, the code revision of every confirmatory artifact in the manifest. One entry per registered experiment (EXP-001 exploratory, EXP-002 to EXP-004 confirmatory); every one of the 23 primary contrasts is shown, nulls included, with both test readings. Project keys `traces`, `robustness`, `pending_decisions` and `placeholders` are validated fail-closed by `demo/src/results.ts`.
- Documented exception to the verbatim rule: the trace medians (per-arm cell medians of TTFF and TTUC with their interquartile range, and the X7 failure-trial medians) are printed by the manuscript only as ranges. `tests/test_demo_export.py` checks them against the committed source files instead; every contrast, interval, Holm p and TOST string is checked verbatim against `research/paper/manuscript.md`.
- Pending owner decision: DEC-011 is shown on the page and in the README as "pending owner decision", with both test readings and both S1 readings (19 of 23 robust, or 11 robust and 9 not assessed). None is chosen.
- Sandbox: faithful for what it ports. The seeded schedule (`src/scroll/schedule.py`, `src/web/schedule.js`) and the zero-overhead reference model (`src/scroll/reference.py`) are ported to `demo/src/engine.ts` and run in a Web Worker with seed, path, latency, hover lead, failure probability and reset. `demo/src/engine.test.ts` compares the port to a fixture written by the Python engine (`scripts/export_sandbox_fixture.py`, 7 configurations, well under a second): delays, outcomes and failure counts must be identical and every time value must agree within 1e-9 ms; it also compares 2,000 draws with `src/web/schedule.js`. The browser harness that produced the measured results is not and cannot be ported, so the sandbox outputs lower bounds, never timings, and the page says it is not the research engine's measurement. The side-by-side replay animates one scheduled trial with browser timers; under the timing addendum it is labelled "illustrative, not a measurement" and records nothing.
- Accessibility check: the template's `tools/a11y_check.mjs` is used unchanged. To satisfy its rule that Tab reaches every focusable element, the two radio groups were built as toggle buttons with `aria-pressed`.
- Text consistency: README rewritten from the M2 status; `CITATION.cff` message updated (no `date-released`, no release made); `articles/medium.md` and `articles/linkedin.md` written for the first time (they did not exist), with every decimal number printed in the manuscript (tested); `demo/README.md` rewritten. No sentence claiming the owner had not reviewed something was found. The post-M4 approvals of titles and statements (`owner-approvals-2026-11-25c.md`) name other repositories, so the SCROLL title stays "proposed, awaiting the owner's approval" and the manuscript was not changed. No `author_review.md` box was ticked by an agent; none needed unticking.
- Placeholders kept: repository URL, demo URL, funding, competing interests, author line and affiliation, manuscript title approval.

## DEC-015: M6 release candidate prepared (local), awaiting the owner's review

- Date: 2026-11-25
- Decided by: the AI assistant under the M6 brief and its timing addendum. Authority: owner, 2026-11-25, "Push and next" (`labs/_shared/owner-approvals-2026-11-25f.md`), which starts "M6 (release candidate) in SCALE, SCROLL and TOKEN" and does not decide "any of the pending SCALE, SCROLL or TOKEN decisions", "no manuscript title not yet approved, and no owner-only fact". Nothing was pushed, tagged, released or frozen; no paid service was used; no frozen protocol, configuration, seed, result or code was changed.
- Clean clone and reproduction: the clone of `4f9e017` installed from `uv.lock`, passed 193 tests, regenerated every committed analysis output from the committed raw results (byte-identical, or identical apart from generation timestamps and SVG ids), built and checked the demo (`A11Y-CHECK PASS`) and re-exported the demo data without changing the tree. No timing measurement was compared with the frozen results; a 5-session harness smoke run was made only to show that the harness executes and is labelled exploratory (`research/publication/reproducibility_report.md`).
- PDFs: new `scripts/build_pdfs.py` builds the manuscript, the supplement and the four experiment reports through the DEC-002 route (pandoc to Typst). Fixes made after visual inspection, all in the builder or the Markdown source: citations rendered by citeproc (`typst-citations`); a PDF title set for every document; tables sized to their content, allowed to break across pages and set slightly smaller (equal-width columns had split words and left a near-blank page); line breaks allowed inside code in table cells (paths and hashes overlapped the next column); one install command in the EXP-002 report put in a code span (its double hyphens had become dashes). The PDFs are committed; `.gitignore` does not exclude them.
- References: the nine free web sources were read in full text and every external claim confirmed (`research/publication/evidence_audit.md`, section 8). The Introduction's citation of the NN/g skeleton article for layout shift was narrowed, because that article does not discuss layout shift. Years were added to five bibliography entries that state a publication date. Mejtoft et al. (2018) stays metadata only (closed access, no free copy found).
- Checks added: `scripts/check_links.py` with `tests/test_links.py` (relative links and anchors in tracked Markdown).
- Scan outcome: no token, key or `.env` file. Absolute home-directory paths remain in frozen (`research/protocol.md`, `src/scroll/report.py`) and append-only files and in `CLAUDE.md`; they were not edited and are listed for the owner. The differential test now finds the shared Node relative to the repository.
- `CITATION.cff`: `date-released` was already absent (owner-approvals-2026-11-25e, coordinator default); version set to `0.1.0-rc1` and the message states that it is a release candidate, not a release. The title was kept: it is the software's project title rather than a copy of the unapproved manuscript title, and both titles are listed as pending the owner's approval. `pyproject.toml` keeps 0.0.0.
- Not decided here and listed on `research/publication/author_review.md`: DEC-011, the manuscript and `CITATION.cff` titles, the funding, competing-interest and AI-use statements, the author line and affiliation (the EXP-002 to EXP-004 reports print the freeze-record name while the manuscript and the EXP-001 report hold a placeholder), the repository and demo URLs, and publication (G-PUBLIC). No `author_review.md` box was ticked.
