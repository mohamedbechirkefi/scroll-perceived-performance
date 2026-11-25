<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Release checklist

Status, 2026-11-25 (M6): release candidate 0.1.0-rc1 prepared, awaiting the owner's review and G-PUBLIC. Every ticked item below was verified in the M6 session of 2026-11-25, with the evidence named. The two owner items stay unticked. Nothing is pushed, tagged or published without explicit owner approval.

- [x] Every registered experiment has a truthful standalone report (including failed or null ones). Evidence: `research/experiment_registry.csv` lists 4 experiments; `research/experiments/EXP-001/report.md` to `EXP-004/report.md` exist (EXP-001 labelled exploratory), were built to PDF and their pages inspected; claims audit and evidence audit sections 2 to 8.
- [x] Integrated manuscript complete; PDF generated through the Typst route and visually inspected. Evidence: `scripts/build_pdfs.py` wrote `research/paper/manuscript.pdf` (15 pages) and `supplementary.pdf` (6 pages); every page was rendered to PNG and read; PDF title set, 0 e-mail addresses, 0 local paths (pypdf). Owner placeholders remain (see `author_review.md`).
- [x] `manuscript.tex` regenerated from Markdown. Evidence: `scripts/build_pdfs.py --tex` (pandoc 3.6.3, `--citeproc`), header comments kept.
- [x] Claims audit and reproducibility report complete. Evidence: `claims_audit.md` (M4), `evidence_audit.md` section 8 (M6 full-text check, 9 sources, 1 metadata only), `reproducibility_report.md` (M6 clean clone).
- [x] Demo, paper, reports and articles use identical verified numbers. Evidence: full suite `196 passed` including `tests/test_demo_export.py` (every demo contrast verbatim in the manuscript; every decimal number of README, both articles and the demo README printed in the manuscript); `export_demo_data.py --check` -> `EXPORT-CHECK PASS`.
- [x] README experiment table and status up to date. Evidence: README status line set to M6 release candidate; table lists EXP-001 to EXP-004 with report and PDF links; `scripts/check_links.py` -> 60 relative links, 0 failures.
- [x] Clean-clone reproduction. Evidence: `reproducibility_report.md`: `193 passed` in the clone at `4f9e017`; 55 regenerated outputs byte-identical, 20 identical after normalising timestamps and SVG ids, 0 other differences; `A11Y-CHECK PASS`; export left `git status` clean.
- [x] Manifests verified. Evidence: 110 of 110 raw-result checksums match, 0 unlisted files; artifact manifest 43 paths present, 36 hashes match; `data/manifest.json` has no downloaded data.
- [x] Secret, identifier and licence scan. Evidence: `reproducibility_report.md` section 6 (0 tokens, 0 keys, 0 `.env`; 1 generic no-reply address and 22 home-path lines listed for the owner); `dependency_licences.md` (no licence outside the permissive list).
- [x] `CITATION.cff` valid against CFF 1.2.0 structure (keys and types), no `date-released`, version `0.1.0-rc1`. Evidence: parsed with a YAML parser; title kept and listed as pending owner approval.
- [ ] Owner review checklist complete (owner sign-off of `author_review.md`).
- [ ] Owner approval for push or release recorded in `research/decision_log.md` (G-PUBLIC).
