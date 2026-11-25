<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Owner review checklist

Status: not started. Only the owner can tick these.

- [ ] Authorship metadata approved (no affiliation unless the owner provides one).
- [ ] Protocol freeze approved and hash recorded (G-FREEZE).
- [ ] Claims register reviewed.
- [ ] AI-assistance disclosure reviewed and accurate.
- [ ] Licence wording in README, CITATION.cff and manuscript checked.
- [ ] Publication, push or release approved explicitly (G-PUBLIC).

## Prepared for the owner (M6, 2026-11-25)

No box above was ticked by an agent, and none was found ticked, so none was unticked. Only the owner ticks them.

### What to read for each box

1. **Authorship metadata.** Read the manuscript front matter (`research/paper/manuscript.md`, lines 1 to 6), the Authorship row of each experiment report (`research/experiments/EXP-00N/report.md`, section 1) and `CITATION.cff` (`authors`). The freeze record C3 (`research/freeze.json`) holds the name with no affiliation.
2. **Protocol freeze.** Read `research/freeze.json` and DEC-009 and DEC-010 in `research/decision_log.md`; the frozen protocol is `research/protocol.md` v1.0 with the per-experiment protocols.
3. **Claims register.** Read `research/claims_register.csv` (54 rows, C-001 to C-046 and E-001 to E-008), `research/publication/claims_audit.md` and `research/publication/evidence_audit.md`, sections 2 to 8.
4. **AI-assistance disclosure.** Read the manuscript section "Funding, competing interests and AI assistance", the README "Citation" section and the `CITATION.cff` message.
5. **Licence wording.** Read the README "Licence" section, the manuscript "Data and code availability" section and the header comments of `CITATION.cff`, against `LICENSE` and `NOTICE.md`.
6. **Publication approval (G-PUBLIC).** Read `research/publication/release_checklist.md`, `research/publication/reproducibility_report.md` and `research/publication/dependency_licences.md`; then read the PDFs `research/paper/manuscript.pdf`, `research/paper/supplementary.pdf` and `research/experiments/EXP-00N/report.pdf`.

### Open decisions for this repository

- **DEC-011 (pending, `owner-approvals-2026-11-25e.md`).** The owner decides which test decides H0 and which paint methods form sensitivity level S1; the manuscript reports both: reading A (Holm-adjusted Wilcoxon) and reading B (unadjusted 95% interval) disagree only for EXP-002 SKELETON at L = 300 ms, and S1 with rAF1 and Element Timing gives 19 of 23 contrasts robust, against 11 robust, 1 method-dependent, 2 condition-dependent and 9 not assessed with Element Timing only.
- **Manuscript title (not approved).** The proposed title is "Skeletons, prefetching and optimistic updates under controlled delays: time to usable content in a single-browser benchmark".
- **CITATION.cff title (not approved).** It reads "SCROLL: loading strategies and measurable interface responsiveness under controlled delays", a project title for the software that differs from the manuscript title; it was kept as it is and awaits the owner's choice.
- **CITATION.cff version.** It now reads "0.1.0-rc1" (release candidate, no `date-released`); `pyproject.toml` still says 0.0.0, and the owner chooses the release number and date at publication.
- **Funding statement (not approved).** The manuscript holds a placeholder.
- **Competing-interest statement (not approved).** The manuscript holds a placeholder.
- **AI-use statement (not approved).** The wording in the manuscript, README and `CITATION.cff` was written by the AI assistant and awaits the owner's review.
- **Author line and affiliation (owner-only fact).** The manuscript and the EXP-001 report hold a placeholder, while the EXP-002, EXP-003 and EXP-004 reports print the name recorded at the freeze with no affiliation; the owner confirms one form for all.
- **Repository URL and demo URL (owner-only facts).** They are placeholders everywhere.
- **Publication (G-PUBLIC).** No GitHub release, tag, DOI, preprint or article publication has been made; re-adding `date-released` belongs to that step.
- **Home-directory paths in published files.** `research/protocol.md` (frozen), `src/scroll/report.py` (frozen code), `CLAUDE.md`, `progress.md` and `research/decision_log.md` contain absolute local paths that show the local user name; the owner decides whether this is acceptable before publication, because the frozen and append-only files were not edited.
- **Generic e-mail address in `CLAUDE.md`.** The no-reply address of the commit trailer appears in the session rules; the owner decides whether to keep it.
- **Run report PDFs inside frozen run folders.** The generator's own PDFs under `results/raw/` and `results/exploratory/` were not visually inspected; the owner decides whether they are published as they are.

### Remaining owner placeholders (file and line)

| File | Line | Placeholder |
|---|---|---|
| `research/paper/manuscript.md` | 4 | author line |
| `research/paper/manuscript.md` | 250 | repository URL |
| `research/paper/manuscript.md` | 254 | funding statement |
| `research/paper/manuscript.md` | 256 | competing-interest statement |
| `research/paper/manuscript.tex` | 92, 98 | author line (generated from the manuscript) |
| `research/experiments/EXP-001/report.md` | 16 | author line |
| `README.md` | 86 | repository URL, demo URL, funding, competing interests, author line and affiliation |
| `CITATION.cff` | 5 | repository URL (in `message`) |
| `articles/medium.md` | 42 | repository URL |
| `articles/linkedin.md` | 14 | repository URL and demo URL |
| `demo/README.md` | 28 | demo URL |
| `demo/public/data/results.json` | 1401 to 1408 | repository URL, demo URL, funding, competing interests, author line and affiliation, manuscript title |
