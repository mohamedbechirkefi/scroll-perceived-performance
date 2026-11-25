<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Evidence audit (master prompt 11.5), M4, 2026-11-25

Scope: `research/paper/manuscript.md`, `research/paper/supplementary.md`, the experiment reports EXP-001 to EXP-004 and `research/claims_register.csv`. No new browser measurement was made: the machine was not quiet (other lab agents were running), so every check below uses committed files only.

## 1. Method

1. **Integrity.** Every file listed in `results/raw/EXP-002/manifest_sha256.json`, `results/raw/EXP-003/manifest_sha256.json` and `results/raw/EXP-004/manifest_sha256.json` was hashed and compared; the raw folders were also searched for unlisted files.
2. **Claims against raw output.** `scripts/m4_number_audit.py` compares the median, 95% interval and Holm p written in claims C-001 to C-023 with the contrast of the same result id in the committed `inference.json`.
3. **Numbers in prose and tables.** The same script extracts every decimal number and every integer of three or more digits from the manuscript, the supplement and the EXP-002 to EXP-004 reports (hashes, dates, paths and identifiers removed), and checks that each equals, at its written precision, a value present in a committed aggregate output, a frozen configuration or record, or the journal. Output: `research/publication/number_audit_m4.json`. This check is necessary, not sufficient: a token can match an unrelated value. The tables were therefore also checked row by row against their source file (step 4).
4. **Manual review.** Every table in the manuscript and supplement was compared with its source file named in `research/publication/artifact_manifest.json`; denominators, units, precision, uncertainty definitions and sample counts were checked against the run manifests and cell summaries; selected report statements were recomputed from the committed aggregate files.
5. **External claims.** Every citation was compared with `research/literature_review.md` (what was actually opened, and how).
6. **Generated text in run folders.** The frozen generator's fixed sentences were compared with the recorded run conditions.

## 2. Results

| Check | Result |
|---|---|
| Raw-result checksums | 110 of 110 listed files match; no unlisted file in any raw folder |
| Claims C-001 to C-023 against `inference.json` | 23 of 23 match (median, interval, Holm p) |
| Token check, manuscript | 387 tokens; 2 unmatched, both derived sums verified by hand (2,387 = 2,400 - 13 exclusions; 3,596 = 3,600 - 4) |
| Token check, supplement | 217 tokens; 1 unmatched (2,387, as above) |
| Token check, EXP-002 report | 258 tokens; 1 unmatched (2,387, as above) |
| Token check, EXP-003 report | 235 tokens; 0 unmatched after X7 (below) |
| Token check, EXP-004 report | 347 tokens; 1 unmatched (115.6 min = (2,677.9 + 1,584.4 + 2,676.1) s / 60, verified) |
| EXP-001 report (composed in M4) | Checked by hand against the journal entries J-0003 and J-0005, the run manifests and the EXP-001 cell and contrast summaries |
| Denominators and sample counts | Sessions, trials analysed and exclusions match the run manifests and cell summaries for all five confirmatory runs; failure-stratum seed counts (12, 18; 9 in EXP-004) match the schedule fixed before data |
| Units and precision | All timings in ms (runtimes in s); estimates to 0.1 ms; Holm p to two significant figures; shares as percentages |
| Uncertainty definitions | 95% percentile bootstrap over seeds, 10,000 resamples, fixed seed; TOST through the 90% interval; stated in every table caption |

## 3. Mismatches found and fixed

No verdict or claim value was wrong. The following prose statements did not match the committed outputs and were corrected, with the old text recorded in place:

| Location | M3 text | Committed value | Fix |
|---|---|---|---|
| EXP-004 report, section 9 | CPU 4x: optimistic benefit grew "by 7 to 14 ms"; prefetch shrank "by 5 to 8 ms" | 5.9 to 13.7 ms; 5.9 to 7.6 ms (`sensitivity_long.csv`, level minus main) | corrected to the exact ranges |
| EXP-004 report, section 9 | Headed: optimistic benefit enlarged "by 17 to 27 ms" | 15.3 to 27.0 ms | corrected |
| EXP-003 report, section 8 | BLANK wrong-state cell medians "111.6 to 1024.5 ms" | 110.1 to 1024.5 ms (`cell_summary.csv`, `wrong_state_median_ms`; the 111.6 was the TTUC median) | corrected |
| EXP-003 report, section 8 | Event Timing below threshold "in 62 to 76%" | 62.5 to 75.5% | written at the stored precision |
| EXP-003 report, section 10 | "26 and 57 pairs in total" | 26 and 57 trial pairs per cell (p = 0.1 and 0.3), 78 and 171 over the three delays | wording clarified |
| EXP-002 report, section 6 | "minimum excess ... was 3.1 ms in every cell" | at least 3.1 ms in every cell; BLANK minima 3.9 to 6.4 ms | wording corrected |
| EXP-003 report, failure-trial exposure table | values produced by an uncommitted one-off command in M3 | reproduced exactly by `scripts/m4_reanalysis.py` (X7), now committed in `results/exploratory/M4-REANALYSIS/x7_exp003_failure_exposure.csv` | provenance gap closed |
| EXP-002 report, section 9 | the 50 ms skeleton effect called "an artefact" and "not evidence that skeletons deliver content sooner" | the direction is the same under all three paint methods (-16.7, -15.3, -9.1 ms) | revised in review pass 2 (`review_pass_2.md`, R-2) |

The manuscript draft contained two errors that the audit caught before commit of the final version: a narrow-S1 robustness count first written as "20 of 23", which the generated X6 output showed to be 11 robust and 9 not assessed, and a frame interval written as "about 18.4 ms", replaced by the generated range 18.0 to 18.9 ms.

## 4. Findings that remain open

1. **Generated run reports and manifests** contain the frozen generator's fixed sentence that other agents were running. It is inaccurate for the confirmatory runs (DEC-012). The frozen files were not edited; the experiment reports and the manuscript state the actual conditions.
2. **Run-folder Holm values in EXP-004** (`inference.json` inside each EXP-004 run) are over non-frozen families and are not used anywhere (DEC-012).
3. **TTFF sensitivity** is not computable (DEC-012); no TTFF claim depends on it.
4. **Generated run report PDFs** exist but were not visually inspected (M6).
5. **Token check limits.** Integers below 100 (design constants, counts, section numbers) and anything inside code spans are not checked mechanically.

## 5. External claims

Every source in `research/paper/references.bib` was opened on 2026-11-24 through a web tool that returns a model-written summary of the page, not its full text (`research/literature_review.md`). No source was read in full. Each external claim (E-001 to E-008 in the claims register) is limited to what the summary stated and is marked "summary-only". Mejtoft et al. (2018) is metadata only: it is cited for existence and no finding of it is used. The statistics references for the bootstrap and TOST were never opened and are not cited. Full-text reading of the sources a claim depends on is scheduled for M6 (owner, 2026-11-25, "Approve all" (post-M4), item 7). Three entries were added to the bibliography in M4 (`tankala_skeleton`, `mdn_lcp`, `react_useoptimistic`); all three were among the sources opened in M0.

## 6. Strength and scope of evidence per conclusion

| Conclusion | Evidence | Strength | Scope |
|---|---|---|---|
| PREFETCH reduces TTUC by about min(h, L) | 4 confirmatory contrasts; robust under S1 to S4; scales with h | strong, partly mechanical | scripted hover lead, one page, one browser |
| OPTIMISTIC reaches the final state about one delay earlier on success | 9 confirmatory contrasts; robust under S1, S2, S4 | strong, partly mechanical | one toggle, uniform failures |
| No detectable TTUC difference on failure | 6 non-rejections; intervals include 0 at every level (exploratory X4) | moderate: no equivalence test, 12 or 18 seeds | as above |
| SKELETON equivalent at L of 100 ms and more | 3 TOST equivalences; robust under every level | strong for this page | one placeholder design |
| SKELETON at L = 50 ms | H0 rejected, equivalence not shown, method-dependent | not robust; no benefit claimed | frame-scale |
| False-state exposure of about the delay on failed saves | descriptive, 83 failure trials per delay | strong, mechanical | by design of the arm |

## 7. Gate assessment

Every numerical claim in the manuscript and reports maps to a result id, a configuration hash and a table or figure (claims register and `artifact_manifest.json`); every external claim maps to a source that was actually opened, marked summary-only or metadata-only. The M4 gate holds on that basis, with the open findings of section 4 disclosed.
