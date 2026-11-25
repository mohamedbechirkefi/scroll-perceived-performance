<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# Reproducibility report (M6, 2026-11-25)

Status: clean-clone reproduction done on 2026-11-25 for the release candidate. Every command below was run, and its actual output is quoted. The machine was shared with other lab agents, so, under the M6 timing addendum, **no timing measurement made here is compared with the frozen results**; reproduction means regenerating the analysis and report outputs from the committed raw results.

Machine: Apple M1 Pro, macOS 15.3.1, Google Chrome 158.0.8127.38 (the version of every confirmatory run), Python 3.12.1 through uv, Node 22.23.3. Load average at the start of the clone work: 2.12 1.94 1.68.

## Checklist

- [x] Clean clone into a separate directory: `git clone -q <repository> <scratch>/clone` of `4f9e017` (local clone, no network).
- [x] `uv sync --frozen --all-groups --all-extras` with the committed `uv.lock`: 26 packages installed, no resolution.
- [x] Browser binary per DEC-005: the installed Google Chrome, version 158.0.8127.38 (`CFBundleShortVersionString`), the same version as in every confirmatory run.
- [x] Test suite run: `193 passed in 55.91s`.
- [x] Smoke reproduction from committed raw results: every regenerated table, inference file and sensitivity file is byte-identical; regenerated SVG figures and `report.md` differ only in embedded generation timestamps and random SVG element ids (identical after normalising those two fields).
- [x] Harness smoke (exploratory, toolchain only): executes; 5 of 5 sessions ok. Its timings are not compared with anything.
- [x] Demo: `npm ci`, `npm test`, `npm run build` and the accessibility and offline checker (`A11Y-CHECK PASS`, which includes "no request leaves the local origin" and "offline after first load").
- [x] Export determinism: re-running both export scripts in the clone left `git status` clean.
- [x] Data manifest, raw-result checksums and artifact-manifest paths verified; relative links checked (below).
- [x] Secret, personal-data and licence scan run (below and `dependency_licences.md`).

## 1. Clean clone, install and tests

```
$ git clone -q <labs>/scroll-perceived-performance <scratch>/clone
$ git log --oneline -1
4f9e017 M5: static offline results page with side-by-side measured traces, ...
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras
 + sortedcontainers==2.4.0
 + typing-extensions==4.16.0
 + tzdata==2026.6
$ nice -n 10 .venv/bin/python -m pytest -q
193 passed in 55.91s
```

The suite includes functional browser tests that launch Chrome; they record no timing result.

## 2. Smoke reproduction from committed results

The run folders of the five confirmatory runs (EXP-002, EXP-003, EXP-004 S2, S3, S4) were copied to scratch with only their inputs (`results.json`, `config.json`, `run_manifest.json`, `trials.csv`), and the frozen generators were re-run on them:

```
$ PYTHONPATH=src .venv/bin/python -m scroll report --run <copy>            (5 runs)
$ PYTHONPATH=src .venv/bin/python -m scroll.inference primary --run <copy> (5 runs)
```

Comparison with the committed `report/` folders (85 committed files; `--pdf` was not passed, so the 10 committed `report.pdf` and `report.typ` files were not regenerated):

| Outcome | Files |
|---|---|
| byte-identical | 55 (every CSV, `analysis.json`, `inference.json`, `inference.csv`, every PNG figure) |
| differ only in generation timestamp and random SVG ids | 20 (15 SVG figures, 5 `report.md` with the line "Report generated <time>") |
| not regenerated | 10 (`report.pdf`, `report.typ`) |
| other differences | 0 |

```
$ PYTHONPATH=src .venv/bin/python -m scroll.inference sensitivity --exp002 ... --s4 ... --out <scratch>/sens
  sensitivity.json, sensitivity_long.csv, sensitivity_verdicts.csv, fig-sensitivity.png: byte-identical
  fig-sensitivity.svg: identical after normalising the timestamp and SVG ids
$ PYTHONPATH=src .venv/bin/python scripts/m4_reanalysis.py --out <scratch>/m4re
  x1 to x7 (8 CSV files): byte-identical
  manifest.json: differs only in code_revision (4f9e017 against 4ba5732) and the --out path in the recorded command
```

Documented tolerance: the frozen analysis is deterministic (fixed bootstrap seed 20261124); a rerun of the browser runs would change timings, and was not done.

### Harness smoke (exploratory, not compared)

```
$ uptime   -> load averages: 2.32 2.15 1.81
$ PYTHONPATH=src nice -n 10 .venv/bin/python -m scroll smoke --report
  5/5 S0005 seed=1001 write/OPTIMISTIC L=100 p=0.5 h=150: ok, 2/2 ok, 1.3 s
  done in 7.2 s
$ uptime   -> load averages: 2.35 2.16 1.82
```

Label: exploratory, toolchain check only. The output folder was deleted with the clone; no timing from it is reported or compared.

## 3. Demo

```
$ export PATH=<helix>/.tools/node/bin:$PATH; cd demo
$ node --version                     -> v22.23.3
$ npm ci --prefer-offline            -> added 53 packages in 620ms
$ npm test                           -> Test Files 2 passed (2); Tests 24 passed (24)
$ npm run build                      -> dist/assets/index-*.js 252.23 kB, worker 2.89 kB, built in 290ms
$ node tools/a11y_check.mjs dist
PASS results render (no fail-closed panel): 4 experiment panels
PASS text contrast, light scheme (WCAG AA)
PASS text contrast, dark scheme (WCAG AA)
PASS keyboard reaches every focusable element: 24 reached of 24
PASS visible focus indicator
PASS no horizontal page scroll at 360 px: overflow 0px
PASS reduced motion: no running animations: 0 running
PASS no request leaves the local origin
PASS offline after first load: results stay, sandbox runs: Sandbox output ready: seed 1, read path, L = 300 ms, 10 trials.
A11Y-CHECK PASS
```

## 4. Export determinism

```
$ .venv/bin/python scripts/export_demo_data.py        -> wrote demo/public/data/results.json
$ .venv/bin/python scripts/export_sandbox_fixture.py  -> wrote demo/src/fixtures/sandbox_fixture.json
$ .venv/bin/python scripts/export_demo_data.py --check -> EXPORT-CHECK PASS
$ git status --short                                   -> (empty)
```

## 5. Manifests and links (working repository, after the M6 edits)

| Check | Result |
|---|---|
| `results/raw/*/manifest_sha256.json` | 110 of 110 listed files match; 0 unlisted files |
| `research/publication/artifact_manifest.json` | 22 artifacts; 43 repository paths named, 0 missing; 36 result SHA-256 values, 0 mismatches |
| `data/manifest.json` | no downloaded data (every external candidate has `downloaded: false`, `sha256: null`); the 3 generator paths exist |
| Relative Markdown links (`scripts/check_links.py`, test `tests/test_links.py`) | 50 relative links in the tracked Markdown files, 0 failures, `LINK-CHECK PASS` |
| Citations | 10 of 10 keys resolve in `references.bib`; 10 of 10 entries cited |

## 6. Secret, identifier and licence scan (tracked files)

| Pattern | Hits | Action |
|---|---|---|
| e-mail addresses | 1: `CLAUDE.md`, the generic no-reply address of the commit trailer | kept (not personal; the session rules need it); listed for the owner |
| tokens and keys (GitHub, OpenAI-style, AWS, Slack, Google API patterns; `key`/`secret`/`password`/`token` assignments) | 0 | none |
| private key headers | 0 | none |
| `.env` files | 0 | none |
| absolute home-directory paths | 22 lines in 6 files: `CLAUDE.md` 7 (tool paths of the session rules), `progress.md` 8 and `research/decision_log.md` 1 (append-only), `research/protocol.md` 3 (frozen, hashed), `src/scroll/report.py` 2 (frozen code revision), `tests/test_schedule_differential.py` 1 | the test now finds the shared Node relative to the repository; the frozen and append-only files were not edited (note appended to `progress.md`); the remaining paths are listed for the owner |
| SPDX header on files added since M0 | all text files that allow a comment carry it, except the 6 generated `report.typ` files inside frozen run folders (covered by `NOTICE.md`; not edited because their hashes are recorded) | none |

Dependency licences: `research/publication/dependency_licences.md` (26 Python distributions, 53 npm packages; no licence outside the permissive list; MPL-2.0 noted for two build and test tools).

## 7. PDFs

Built with `scripts/build_pdfs.py` (pandoc 3.6.3 to Typst, compiled with the `typst` Python package 0.15.0; DEC-002 route) and inspected page by page as PNG renders: manuscript 15 pages, supplement 6, EXP-001 4, EXP-002 8, EXP-003 6, EXP-004 8. Fixes and metadata checks are recorded in `progress.md` (M6 entry) and DEC-015.
