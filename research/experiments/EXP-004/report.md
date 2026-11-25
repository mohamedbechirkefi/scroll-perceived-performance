<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# EXP-004 report: Sensitivity analyses for EXP-002 and EXP-003

## 1. Identification

| Field | Value |
|---|---|
| Experiment | EXP-004 (confirmatory sensitivity) |
| Date of execution | 2026-11-25, 09:54:34Z to 11:50:14Z |
| Protocol | `research/experiments/EXP-004/protocol.md` v1.0, SHA-256 `9d67a8e91d965456c9fddaf372db1d21156840f311478d8647509aa46e5ae54d`; parent `research/protocol.md` v1.0, SHA-256 `a87ae45e049c16ed42abef0ab853a0e3fcf28daec9d5482d11bbb1dfb365f004` |
| Configurations | S2 `experiments/EXP-004-S2.json` (hash `200f25f294f699d3128b815bd130deeab7829e0121d82e4a3a78ac355ee9339e`), S3 `EXP-004-S3.json` (`5a8b8a7d9e8b4f2c091f6ceaa69a874ce5b9f45b424334b5749a1d90de7d62a5`), S4 `EXP-004-S4.json` (`7c7b667ce8baebb24379af137c3d2f5f66c5f0df8ccba720f461f639f189fc50`); S1 reuses the EXP-002 and EXP-003 runs |
| Code revision | `b5a72c32202cb66a17341a5022ad29e9344506b6` (clean) |
| Runs | `EXP-004-20261125T095434Z` (S2), `EXP-004-20261125T103912Z` (S3), `EXP-004-20261125T110537Z` (S4) |
| Status | Complete. All three configurations in full; S1 computed; the TTFF part of S1 not computable (gap) |
| Authorship | Mohamed Bechir Kefi (no affiliation). An AI system was used as a research and development assistant; it is not an author |

## 2. Executive summary

- **Question.** Do the verdicts of EXP-002 and EXP-003 survive four factors?
  - S1: the alternative paint-time methods.
  - S2: CPU throttling 4x.
  - S3: prefetch lead h of 0 and 600 ms.
  - S4: a headed browser.
- **Method.** The frozen trial-paired estimand on seeds 1 to 10 (S2 to S4) over L {300, 1000} ms and p {0, 0.3}. S1 is recomputed on all EXP-002 and EXP-003 data. The frozen rule calls a verdict robust only if:
  - its sign is the same at every level, or
  - for SKELETON, its equivalence verdict is the same at every level.
- **Robust:** 19 of 23 primary contrasts, including every PREFETCH and OPTIMISTIC success contrast and SKELETON at L = 100 to 1000 ms.
- **Not robust:**
  - SKELETON at L = 50 ms is method-dependent: equivalence holds under both alternative paint methods but not under the main one.
  - Three write-path failure strata (L = 300 ms p = 0.1; L = 300 ms p = 0.3; L = 1000 ms p = 0.3) change sign. Their main estimates lie within 2 ms of zero and are not significant.
- **Principal caveat.** The sign rule applied to null estimates carries no directional information. S2 to S4 use 10 seeds.

## 3. Rationale and literature

- **Why sensitivity matters.** Differences of a few frames can come from how frames are timed rather than from the strategy.
- **Hidden costs.** Skeleton or rollback costs may appear only under CPU load.
- **Rendering mode.** Headless frame scheduling may differ from headed (protocol section 8; feasibility risks 1 and 2).
- **References:** as in EXP-002 and EXP-003. The CDP CPU-throttling documentation could not be read in M0, so the throttling mechanism is used as Playwright and Chrome provide it, unverified beyond the recorded setting `cpu_throttle = 4`.

## 4. Hypotheses and operational definitions

- **Estimand.** For each primary contrast, the frozen estimand (A1, A2) is computed at each factor level and set beside the main estimate. The main estimate is the frozen EXP-002 or EXP-003 value with 20 seeds.
- **Robustness rule.** A verdict is robust only if the sign of the point estimate is the same at every available level. For SKELETON the rule uses the TOST equivalence verdict, and its sign is also shown (DEC-011 item 5).
- **Labels.** A change under S1 is labelled method-dependent; a change under S2, S3 or S4 is labelled condition-dependent.
- **S1 levels.** Two alternative paint methods are recorded by the frozen code: rAF1, the first frame timestamp, on both paths; and Element Timing `renderTime`, on the read path only. The protocol said the alternative would be "chosen in EXP-001", but no choice was recorded, so both count and neither is selected (DEC-012).
- **S3.** Applies to PREFETCH only, at h = 0 and h = 600 ms against the main h = 150 ms.

## 5. Methodology

- **S2:** EXP-002 and EXP-003 arms at L {300, 1000} ms, p {0, 0.3} (write), CPU 4x, headless. 140 sessions.
- **S3:** BLANK and PREFETCH at L {300, 1000} ms and h {0, 600} ms, CPU 1x, headless. 80 sessions.
- **S4:** as S2 but CPU 1x and headed. Chrome windows were visible on the display. 140 sessions.
- **Common settings:** seeds 1 to 10, K = 10, Chrome 158.0.8127.38, same machine.
- **Machine conditions:**
  - Exclusive window, mains power, `nice -n 10`.
  - Load at the starts: 1.37/1.41/1.51 (S2), 2.29/2.12/1.74 (S3) and 2.19/2.42/2.28 (S4).
  - Load at the end of S4: 1.64/1.54/1.70.
- **Budget:** about 117 minutes were projected; 115.6 minutes were used.

## 6. Implementation verification

- **Tests:** 178 passed before the runs. Sensitivity wiring was tested on the fake harness (`tests/test_inference.py`), including the S3 levels and the sign change at h = 0.
- **In every S2 to S4 run:**
  - No defect flag.
  - Rollback correctness 1.0 (800 of 800 write trials in S2 and in S4).
  - No BLANK trial below the injected delay.
  - Prefetch used in every analysed PREFETCH trial.
- **Exclusions.** The A3 hover-lead rule applied to S3 at h = 0 and 600 ms; 4 of 800 trials were excluded, at most 1 per session. No cell failed.

## 7. Execution record

- **Commands:** `PYTHONPATH=src nice -n 10 .venv/bin/python -m scroll run --config experiments/EXP-004-S2.json` (then `-S3`, `-S4`), each after a quiet check (quiet at 09:54:34Z, 10:39:12Z and 11:05:37Z).
- **Per-run reports:** `scroll report --pdf`.
- **Sensitivity table:** `PYTHONPATH=src .venv/bin/python -m scroll.inference sensitivity --exp002 results/raw/EXP-002/EXP-002-20261125T070315Z --exp003 results/raw/EXP-003/EXP-003-20261125T080838Z --s2 results/raw/EXP-004/EXP-004-20261125T095434Z --s3 results/raw/EXP-004/EXP-004-20261125T103912Z --s4 results/raw/EXP-004/EXP-004-20261125T110537Z --out results/raw/EXP-004/sensitivity`.
- **Samples:**
  - S2: 140 of 140 sessions, 1,400 of 1,400 trials.
  - S3: 80 of 80 sessions, 796 of 800 trials.
  - S4: 140 of 140 sessions, 1,400 of 1,400 trials.
- **Runtimes:** 2,677.9 s, 1,584.4 s and 2,676.1 s.
- **Deviations and gaps:**
  - The TTFF part of S1 is not computable, because the alternative method is not recorded for the first-feedback frame.
  - The `inference.json` files inside the EXP-004 run folders contain Holm values over non-frozen families; they are not used.
  - Run conditions are as in DEC-012.

## 8. Results

Side-by-side estimates. Each cell gives the median trial-paired TTUC difference in ms, then the 95% percentile bootstrap interval over seeds, then the number of seeds n. For SKELETON, "eq" is the TOST verdict at 17 ms.

| Contrast | Main (double rAF) | S1 rAF1 | S1 Element | S2 CPU 4x | S3 h = 0 | S3 h = 600 | S4 headed | Frozen verdict |
|---|---|---|---|---|---|---|---|---|
| read L=50 PREFETCH | -50.0 [-51.2, -48.9] n=20 | -48.8 [-50.2, -48.3] | -52.5 [-54.2, -50.8] | | | | | robust |
| read L=50 SKELETON | -16.7 [-17.1, -16.0] eq no | -15.3 [-16.0, -14.8] eq yes | -9.1 [-9.8, -8.3] eq yes | | | | | method-dependent |
| read L=100 PREFETCH | -84.9 [-86.3, -84.1] | -84.3 [-85.2, -83.0] | -95.2 [-96.3, -92.0] | | | | | robust |
| read L=100 SKELETON | -0.6 [-1.9, 0.1] eq yes | 0.1 [-0.3, 0.9] eq yes | -0.9 [-1.1, -0.6] eq yes | | | | | robust |
| read L=300 PREFETCH | -160.5 [-163.5, -157.1] | -162.0 [-163.1, -158.1] | -159.5 [-159.9, -158.7] | -152.9 [-158.0, -151.2] n=10 | -1.9 [-5.1, 0.6] n=10 | -293.9 [-299.8, -282.9] n=10 | -164.8 [-166.3, -163.5] n=10 | robust |
| read L=300 SKELETON | -1.0 [-1.1, -0.4] eq yes | 0.4 [-0.0, 0.7] eq yes | -1.1 [-1.6, -0.6] eq yes | -0.5 [-2.3, 1.0] eq yes | | | -0.1 [-0.6, 0.6] eq yes | robust |
| read L=1000 PREFETCH | -157.8 [-159.1, -155.4] | -155.7 [-159.4, -154.1] | -160.1 [-160.5, -158.9] | -151.9 [-153.1, -151.4] | -1.7 [-3.5, -1.1] | -609.6 [-613.7, -603.9] | -159.6 [-161.1, -158.5] | robust |
| read L=1000 SKELETON | 0.0 [-0.9, 0.9] eq yes | 0.4 [0.1, 1.2] eq yes | -1.1 [-2.3, 0.0] eq yes | -0.4 [-1.3, 0.5] eq yes | | | 0.4 [-0.7, 1.5] eq yes | robust |
| write L=100 p=0 success | -85.2 [-88.0, -84.3] | -84.7 [-85.9, -83.7] | | | | | | robust |
| write L=100 p=0.1 success | -85.3 [-86.6, -84.8] | -85.0 [-85.8, -84.5] | | | | | | robust |
| write L=100 p=0.1 failure | 0.5 [-1.5, 1.7] n=12 | 0.5 [-0.5, 1.7] | | | | | | robust |
| write L=100 p=0.3 success | -85.3 [-88.0, -83.9] | -84.1 [-85.1, -83.5] | | | | | | robust |
| write L=100 p=0.3 failure | 2.7 [-1.0, 5.4] n=18 | 1.0 [-2.5, 2.3] | | | | | | robust |
| write L=300 p=0 success | -288.5 [-297.7, -282.3] | -285.0 [-296.5, -281.7] | | -295.7 [-299.3, -288.8] | | | -310.2 [-316.9, -299.2] | robust |
| write L=300 p=0.1 success | -289.3 [-297.6, -283.5] | -289.2 [-296.8, -283.9] | | | | | | robust |
| write L=300 p=0.1 failure | -0.8 [-3.0, 4.3] n=12 | 0.7 [-1.9, 4.3] | | | | | | method-dependent |
| write L=300 p=0.3 success | -290.4 [-297.4, -284.1] | -288.1 [-293.2, -280.7] | | -296.3 [-307.4, -289.2] | | | -305.7 [-316.1, -297.4] | robust |
| write L=300 p=0.3 failure | -0.1 [-2.6, 1.5] n=18 | 0.4 [-1.4, 1.7] | | -0.3 [-0.9, 2.0] n=9 | | | 0.4 [-2.7, 0.9] n=9 | method- and condition-dependent |
| write L=1000 p=0 success | -998.6 [-1012.2, -972.6] | -999.4 [-1013.4, -973.0] | | -1007.2 [-1029.1, -974.2] | | | -1025.6 [-1045.3, -989.9] | robust |
| write L=1000 p=0.1 success | -995.9 [-1015.8, -967.3] | -996.8 [-1016.3, -967.9] | | | | | | robust |
| write L=1000 p=0.1 failure | -1.6 [-7.1, 0.1] n=12 | -1.2 [-5.3, 0.3] | | | | | | robust |
| write L=1000 p=0.3 success | -990.7 [-1016.6, -961.7] | -991.2 [-1011.7, -962.6] | | -1004.4 [-1034.2, -968.7] | | | -1017.0 [-1046.4, -981.4] | robust |
| write L=1000 p=0.3 failure | 0.6 [-1.4, 3.4] n=18 | 1.2 [-0.8, 2.1] | | -1.3 [-4.2, 0.9] n=9 | | | 0.0 [-1.3, 2.8] n=9 | condition-dependent |

- **Seed counts.** Where n is not shown, it equals the main seed count (20) for S1 and 10 for S2 to S4.
- **Signs within robust SKELETON contrasts.** The rule for SKELETON uses the equivalence verdict. Within the robust SKELETON contrasts, the sign changes under rAF1 at L = 100 and 300 ms, and under Element Timing and S2 at L = 1000 ms; all these estimates lie within 1.2 ms of zero.
- **S3 mechanical check** (descriptive):
  - At h = 600 ms, PREFETCH minus BLANK is -293.9 ms at L = 300 ms (expected -300) and -609.6 ms at L = 1000 ms (expected -600).
  - At h = 0 the benefit nearly disappears (-1.9 and -1.7 ms), but the estimates stay negative, so the sign is unchanged.
- **Figure.** `results/raw/EXP-004/sensitivity/figures/fig-sensitivity.png`: for each reduced-matrix contrast, the estimate and 95% interval at every level, with the verdict in the panel title, generated from the run files.
- **Machine-readable outputs:**
  - `results/raw/EXP-004/sensitivity/sensitivity.json` (all levels per contrast);
  - `sensitivity_long.csv`;
  - `sensitivity_verdicts.csv`.

## 9. Interpretation

- **Robust findings.**
  - The prefetch benefit and the optimistic benefit on success keep their sign and approximate size under every method, CPU throttling and headed rendering.
  - Under CPU 4x the prefetch benefit shrank by 5 to 8 ms and the optimistic benefit grew by 7 to 14 ms, a measured shift with 10 seeds.
  - Headed rendering enlarged the optimistic benefit by 17 to 27 ms at L = 300 and 1000 ms.
  - The skeleton's equivalence with blank at L of 100 ms and above holds at every level.
- **Method-dependent: SKELETON at L = 50 ms.** The only non-null verdict that changes is the -16.7 ms SKELETON effect at L = 50 ms. It becomes equivalent under both alternative paint methods, shrinking to -9.1 ms under Element Timing. The main interpretation ("strategies that change first feedback do not necessarily change time to usable content") is therefore qualified at the shortest delay: the frame-scale difference observed there depends on how paint time is measured.
- **Failure strata.**
  - Main estimates lie between -1.6 and 2.7 ms, and none rejects H0.
  - Under the frozen rule, three of them are labelled method- or condition-dependent because the sign of a near-zero estimate flips. This is what noise around zero produces; it is not evidence of a direction.
  - These verdicts are reported as the frozen rule outputs them, with that caveat.
- **Not tested.** Whether TTFF verdicts (SKELETON lowers first feedback) depend on the paint method; see the gap.

## 10. Threats to validity

- **Statistical:**
  - S2 to S4 use 10 seeds, and failure strata 9 seeds at p = 0.3, so intervals are wider.
  - The sign rule has no tolerance band, so it flags null contrasts by construction.
  - The rule compares point estimates, not intervals.
- **Construct:**
  - The CPU-throttling mechanism was not verified against documentation.
  - Element Timing exists only on the read path.
  - In headed mode, frame timing depends on the physical display (possibly 120 Hz), which was not recorded.
- **External:** one machine, one Chrome version, one page.
- **Internal:**
  - The three configurations ran sequentially with load averages of 1.4 to 2.4.
  - The main estimates come from runs about one to three hours earlier on the same machine and browser.

## 11. Conclusion and next experiment

- **Robust within the tested factors:** the strategy effects that matter (prefetch and optimistic update on success) and the skeleton's equivalence with blank at delays of at least 100 ms.
- **Method-dependent:** the one-frame skeleton advantage at 50 ms.
- **No reliable direction:** failure-stratum signs.
- **Follow-up** (requires an owner-approved protocol):
  - Record alternative paint times for the first-feedback frame, so TTFF sensitivity becomes computable.
  - Add a tolerance band or interval-based criterion to the robustness rule for null contrasts.
  - Record the display refresh rate in headed runs.

## 12. Reproduction appendix

- **Dependencies:** as in EXP-002.
- **Commands:** listed in section 7.
- **Raw results and SHA-256 of `results.json`:**
  - S2: `results/raw/EXP-004/EXP-004-20261125T095434Z/results.json`, `173a3b82f003f467dc89859821ff14d1d5061af8c70b4ea37aa63a687d4b81bf`
  - S3: `results/raw/EXP-004/EXP-004-20261125T103912Z/results.json`, `0e3ea2a6f3d4ae6da95de027b0d3bcf228a3c24600462ea84782387a6576041c`
  - S4: `results/raw/EXP-004/EXP-004-20261125T110537Z/results.json`, `0df4a90fa1a334fae11450917b7d02cd39b7a98d874652c6c382ca187343d317`
- **Main inputs:** the EXP-002 and EXP-003 `results.json` files, hashes in their reports.
- **Checksums of every output:** `results/raw/EXP-004/manifest_sha256.json`.
- **Regenerate table and figure:** the `scroll.inference sensitivity` command in section 7.
- **Records:** journal J-0008; DEC-011, DEC-012; claims C-024 to C-028.
