<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# SCROLL: how every session works

`master_prompt.md` is the authority. Never edit it. If this file and the master prompt conflict, the master prompt wins (except for the licence, which is the owner's decision DEC-001) and the conflict is recorded in `progress.md`.

## 1. Reading order (before modifying anything)

1. `master_prompt.md`
2. `roadmap.md`
3. `progress.md`
4. `research/protocol.md`
5. `research/claims_register.csv`

Then: run `git status`, inspect existing files, never overwrite owner changes. State the current milestone and the next bounded task before working.

## 2. Mandatory requirements from section 11 of the master prompt

- Maintain the publication tree of section 11.1: `research/experiment_registry.csv`, `research/protocol.md`, `research/claims_register.csv`, `research/paper/` (manuscript.md canonical, manuscript.tex and PDF generated), `research/experiments/EXP-NNN/` (protocol, report, config, run manifest, metrics, figures, reproduction), `research/publication/` (artifact manifest, claims audit, reproducibility report, author review, release checklist).
- Stable IDs: experiments `EXP-NNN`, runs, figures, claims. Register every experiment before confirmatory execution. A seed is a run, not a new experiment.
- Before each experiment, write `EXP-NNN/protocol.md` with every field of section 11.2. Confirmatory protocols are frozen by the owner, with version and hash, before execution.
- Every registered experiment gets a standalone report with the 12 sections of 11.3, including failed, null and exploratory ones, clearly labelled. Tables and figures come from actual outputs.
- One integrated manuscript (11.4), 3,000 to 6,000 words where justified, built from the reports.
- Evidence-to-publication pipeline (11.5): one generator for tables and figures, a manifest mapping each number to experiment, run, metric, result path, script, protocol hash and code revision; audit every number; a second review pass challenges the preferred hypothesis.
- Milestone additions (11.6): M0/M1 registry, manuscript skeleton, experiment protocols, zero-cost toolchain, freeze before confirmatory runs; M2 versioned schemas, manifests and report generators with the core; M3 reports as experiments finish, record failures and deviations; M4 finish reports and evidence audit, synthesise into the manuscript; M5 demo, paper, reports and articles use identical verified results; M6 compile and inspect PDFs, clean-clone reproduction, owner review checklist.
- Never fabricate a PDF, a result, a citation or a test count. If a tool is missing, document the blocker and deliver source plus build instructions.

## 3. Rules (all sessions)

### Gates
- Never push, add a remote, create a GitHub repository or publish anything (G-PUBLIC).
- No paid service of any kind.
- Never freeze a protocol yourself: freezing is the owner's decision (G-FREEZE). Until the freeze, every run is exploratory and labelled so.
- No confirmatory experiment before the owner freezes the protocol. A tiny exploratory smoke check of the toolchain is allowed, labelled exploratory.

### Scope
- Work only inside this repository. Paths below are relative to the repository root. Tools are used read-only: `/usr/local/bin/python3`, `../.tools/py/bin/` (uv, typst, pypdf, pillow), `../.tools/pandoc`, Node at `../../helix/.tools/node/bin` (never modify that folder), git.
- Do not touch any other folder under the research root (hive, helix, cogkt, trading, the other labs).
- Never kill processes you did not start. Never delete anything you did not create in the current session.

### Truthfulness
- Never fabricate results, citations, test counts or PDFs.
- Record commands and their actual outputs in `progress.md`.
- Unverified means labelled unverified.
- Claims boundary: objective timing is not perceived speed; no human perception claims.

### Files and style
- New text and code files start with `SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0` as a comment where the format allows; JSON and CSV are covered by `NOTICE.md`.
- Do not change the licence files (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `.github/`). Development commands may be appended to `CONTRIBUTING.md`.
- English. No em dashes. Plain, formal register.
- No e-mail address, personal identifier or secret in any committed file (git author metadata excepted).
- Refer to the owner as "the owner" (they/them).

### Commits
- Local commits only, with the owner's git identity passed through `git -c user.name=... -c user.email=... commit` exactly as given in `../_shared/M0-brief.md` (kept out of this file: no e-mail address in committed files), message ending with a blank line and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Run `git status` before and after.

## 4. Session end

Update `progress.md` (dated entry: decisions, commands, actual results, failures, changed files, risks, next action) and `roadmap.md` statuses. Never mark incomplete work done.

## 5. Useful commands

- Lock dependencies: `../.tools/py/bin/uv lock --python /usr/local/bin/python3`
- Manuscript PDF (Typst route): `../.tools/pandoc research/paper/manuscript.md -s -t typst -V mainfont="Libertinus Serif" -o <out>.typ`, then `../.tools/py/bin/python -c "import typst,sys; typst.compile(sys.argv[1], output=sys.argv[2])" <out>.typ research/paper/manuscript.pdf`
- LaTeX source: `../.tools/pandoc research/paper/manuscript.md -s -t latex -o research/paper/manuscript.tex` (then re-add the two header comment lines)
- npm, if needed: prefix `PATH=$PWD/../../helix/.tools/node/bin:$PATH` (run from the repository root) (an older Node is otherwise found first).
