<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Claims audit checklist (M4)

Status: completed for M4 on 2026-11-25. Details in `evidence_audit.md`; mechanical output in `number_audit_m4.json`.

- [x] Every row of `research/claims_register.csv` has an evidence path that exists, or a source actually opened (54 rows: C-001 to C-046, E-001 to E-008), with result id, configuration hash, figure or table, manuscript section and limit.
- [x] Every number in the manuscript, supplement and experiment reports EXP-002 to EXP-004 was checked against committed outputs (value, units, precision, denominator, sample size); 8 prose mismatches were corrected, none affecting a verdict or a claim value. The EXP-001 report was composed in M4 and checked by hand. README, demo and articles do not yet carry results (M5).
- [x] Observed, exploratory, descriptive, check and external claims are typed in the `type` column.
- [x] No perception claim (claims boundary).
- [x] Non-significant results are not described as equivalence (review pass 2, R-8, removed two such phrasings).
- [x] Failed, null and excluded runs are reported (no failed run or cell; 13 + 4 hover-lead exclusions; 9 null failure-stratum or SKELETON contrasts).
- [x] A second review pass challenged the preferred hypothesis (`review_pass_2.md`).
- [ ] External sources read in full: not done; all are summary-only or metadata-only. Scheduled for M6 (owner, 2026-11-25, "Approve all" (post-M4), item 7).
- [ ] Owner review of DEC-011 and of the placeholders: pending.
