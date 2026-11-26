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

Updated 2026-11-26 after the owner's answers (next section). Still open:

- **Full-text review and sign-off (B16).** The owner reads the manuscript, the supplement and the four reports in full, then decides on each box above.
- **Article drafts (B15).** `articles/medium.md` and `articles/linkedin.md`, with their titles, are drafts; the owner reads and approves them before any posting.
- **Release (B18).** No tag, GitHub release, DOI or preprint exists. At the release, `CITATION.cff` `version` becomes `0.1.0` and `date-released` is set to the release day (`research/publication/release_checklist.md`).
- **Freezes.** None is pending in this repository: protocol v1.0 and every registered experiment protocol are frozen or exploratory as recorded in `research/freeze.json`.

### Remaining owner placeholders (file and line)

None. Every placeholder listed on 2026-11-25 (manuscript author line, repository URL, funding and competing-interest statements; `manuscript.tex`; EXP-001 report author line; README; `CITATION.cff`; both articles; `demo/README.md`; `demo/public/data/results.json`) was filled on 2026-11-26 from the owner's answers (DEC-016). `git grep -n "OWNER PLACEHOLDER"` returns nothing.

## Owner answers recorded (2026-11-26)

Source: owner, 2026-11-26, decision sheet (`labs/_shared/owner-decision-sheet-2026-11-26.md`, answers in `labs/_shared/owner-approvals-2026-11-26.md`). Applied in DEC-016 as wording and configuration only; no result, analysis, figure, configuration, seed, frozen protocol, hash or checksummed output changed. No box above was ticked by an agent.

| Id | Answer | Applied here |
|---|---|---|
| A1 | Correct the "not pushed / no remote" sentences | the repository is public since 2026-11-25; README, `release_checklist.md` and `reproducibility_report.md` say so; append-only records unchanged |
| B1 | Repository URL `https://github.com/mohamedbechirkefi/scroll-perceived-performance` | manuscript, README, both articles, `demo/README.md`, demo data, `CITATION.cff` `repository-code` |
| B2 | Demo hosted on Cloudflare Workers, free plan, `https://scroll-perceived-performance.kefimohamedbechir.workers.dev` | demo URL filled; `demo/wrangler.jsonc` added (static assets from `./dist`, no Worker script); deployment is the coordinator's |
| B3 | Author "Mohamed Bechir Kefi, independent researcher" | manuscript, supplement, the four reports, README, articles, demo footer and data; `CITATION.cff` `affiliation: "Independent researcher"` |
| B4 | No funding; no competing interests | manuscript, README, demo data |
| B5 | AI-use statement approved as drafted | "not approved" marks removed; wording unchanged |
| B6, B7 | Manuscript title approved; `CITATION.cff` carries it | "awaiting approval" marks removed; `CITATION.cff` title replaced |
| B8 | `0.1.0-rc1` kept, no `date-released`; `0.1.0` and the release day at the release; `pyproject.toml` stays `0.0.0` | recorded in `release_checklist.md` |
| B9 | Scrub home paths from editable files, no history rewrite | `CLAUDE.md` scrubbed; what remains and why: `reproducibility_report.md` section 8 |
| B10 | PDFs kept and attached to a release | PDFs rebuilt from the changed sources |
| B11, B13 | Release-note lines | `release_checklist.md`, "Release notes (draft)" (no SCROLL figure was listed for B11) |
| B14 | Source labels accepted | recorded; Mejtoft et al. (2018) stays metadata only, as the manuscript states |
| B17 | Push the local M6 commits | granted; pushing is the coordinator's step, not done here |
| R-SCROLL-1 | DEC-011: owner chose none | both readings stay shown; "pending owner decision" wording replaced by "the owner chose neither reading" in the manuscript, supplement, README, articles and demo |
| R-SCROLL-2 | Noreply address in `CLAUDE.md` kept; run PDFs under `results/` released without visual inspection | recorded; nothing changed |

Still open: B15 (article drafts), B16 (full-text review and sign-off of every box above), B18 (release, tag, DOI or preprint). No freeze is pending in this repository.
