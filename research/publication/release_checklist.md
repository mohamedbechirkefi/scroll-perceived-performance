<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Release checklist

Status, 2026-11-25 (M6): release candidate 0.1.0-rc1 prepared. Every ticked item below was verified in the M6 session of 2026-11-25, with the evidence named. The two owner items stay unticked.

Update, 2026-11-26: the repository was pushed and is public at https://github.com/mohamedbechirkefi/scroll-perceived-performance since 2026-11-25, together with everything committed in it. The owner's answers of 2026-11-26 (owner, 2026-11-26, decision sheet) were applied as wording and configuration only (DEC-016). No tag, GitHub release, DOI or preprint exists; the release (B18) follows the owner's full-text review and sign-off (B16).

- [x] Every registered experiment has a truthful standalone report (including failed or null ones). Evidence: `research/experiment_registry.csv` lists 4 experiments; `research/experiments/EXP-001/report.md` to `EXP-004/report.md` exist (EXP-001 labelled exploratory), were built to PDF and their pages inspected; claims audit and evidence audit sections 2 to 8.
- [x] Integrated manuscript complete; PDF generated through the Typst route and visually inspected. Evidence: `scripts/build_pdfs.py` wrote `research/paper/manuscript.pdf` (15 pages) and `supplementary.pdf` (6 pages); every page was rendered to PNG and read; PDF title set, 0 e-mail addresses, 0 local paths (pypdf). Owner placeholders were filled on 2026-11-26 (DEC-016) and the PDFs rebuilt.
- [x] `manuscript.tex` regenerated from Markdown. Evidence: `scripts/build_pdfs.py --tex` (pandoc 3.6.3, `--citeproc`), header comments kept.
- [x] Claims audit and reproducibility report complete. Evidence: `claims_audit.md` (M4), `evidence_audit.md` section 8 (M6 full-text check, 9 sources, 1 metadata only), `reproducibility_report.md` (M6 clean clone).
- [x] Demo, paper, reports and articles use identical verified numbers. Evidence: full suite `196 passed` including `tests/test_demo_export.py` (every demo contrast verbatim in the manuscript; every decimal number of README, both articles and the demo README printed in the manuscript); `export_demo_data.py --check` -> `EXPORT-CHECK PASS`.
- [x] README experiment table and status up to date. Evidence: README status line set to M6 release candidate; table lists EXP-001 to EXP-004 with report and PDF links; `scripts/check_links.py` -> 60 relative links, 0 failures.
- [x] Clean-clone reproduction. Evidence: `reproducibility_report.md`: `193 passed` in the clone at `4f9e017`; 55 regenerated outputs byte-identical, 20 identical after normalising timestamps and SVG ids, 0 other differences; `A11Y-CHECK PASS`; export left `git status` clean.
- [x] Manifests verified. Evidence: 110 of 110 raw-result checksums match, 0 unlisted files; artifact manifest 43 paths present, 36 hashes match; `data/manifest.json` has no downloaded data.
- [x] Secret, identifier and licence scan. Evidence: `reproducibility_report.md` section 6 (0 tokens, 0 keys, 0 `.env`; 1 generic no-reply address and 22 home-path lines listed for the owner); `dependency_licences.md` (no licence outside the permissive list).
- [x] `CITATION.cff` valid against CFF 1.2.0 structure (keys and types), no `date-released`, version `0.1.0-rc1`. Evidence: parsed with a YAML parser; title set on 2026-11-26 to the owner-approved manuscript title, with `repository-code` and the author's affiliation (DEC-016).
- [ ] Owner review checklist complete (owner sign-off of `author_review.md`).
- [ ] Owner approval for push or release recorded in `research/decision_log.md` (G-PUBLIC).

## At the release (owner-approved default, B8, 2026-11-26)

- `CITATION.cff` `version` becomes `0.1.0` (from `0.1.0-rc1`) and `date-released` is set to the release day. Until then there is no `date-released`.
- `pyproject.toml` stays at `0.0.0`: changing it would change the lockfile and the recorded environments.

## Release notes (draft)

- Figures: no SCROLL figure was listed with small, crowded or clipped labels (decision sheet B11), so none is named here; committed figures are kept as checksummed results.
- Build and check tools: external tools are used but not redistributed by this repository: pandoc (GPL-2.0-or-later) to build the PDFs, Google Chrome for the measurements and the accessibility check, and MPL-2.0 lightningcss as a CSS build tool, as listed in `research/publication/dependency_licences.md`.
- Source labels: the reading level stated for each source (Mejtoft et al. (2018) metadata only; the others full text) is accepted by the owner (B14, 2026-11-26) and stated in the manuscript.
- Run report PDFs: the generator's own PDFs under `results/` are released without visual inspection (owner, 2026-11-26, R-SCROLL-2).
