<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# SCROLL

**Question:** how do loading strategies (blank, skeleton, optimistic update, prefetch) affect measurable interface responsiveness under controlled, injected delays?

**Status: M2 (core implementation), 2026-11-24.** The benchmark engine, harness, tests and report generator exist. Only exploratory pre-freeze runs have been made; there are no findings. The protocol is a draft awaiting the owner's freeze.

## Why it matters

Loading strategies are often chosen because they look faster. This project measures, in a controlled local benchmark, what they change objectively: time to usable content, time to first feedback, layout shift and rollback behaviour. It makes no claim about how fast an interface feels to people.

## What exists now

- Draft protocol: [`research/protocol.md`](research/protocol.md)
- Experiment registry: [`research/experiment_registry.csv`](research/experiment_registry.csv)

| ID | Experiment | Status |
|---|---|---|
| EXP-001 | Smoke run and instrumentation validation (exploratory) | exploratory run made pre-freeze (2026-11-24); see `progress.md` |
| EXP-002 | Read path: blank vs skeleton vs prefetch | frozen (owner-approved 2026-11-24), not yet run |
| EXP-003 | Write path: blank vs optimistic, with failures | frozen (owner-approved 2026-11-24), not yet run |
| EXP-004 | Sensitivity analyses | frozen (owner-approved 2026-11-24), not yet run |

- Roadmap: [`roadmap.md`](roadmap.md); session journal: [`progress.md`](progress.md).
- Literature and sources: [`research/literature_review.md`](research/literature_review.md); limitations: [`research/limitations.md`](research/limitations.md).

Implemented (M2): the mock interface (`src/web/`), the seeded schedule, the Playwright harness on the installed Chrome, metrics, statistics, versioned result schema, run manifests, the report generator and a CLI. See [`src/README.md`](src/README.md) and [`tests/README.md`](tests/README.md).

Quick start (after `uv sync --frozen`):

```
PYTHONPATH=src .venv/bin/python -m scroll test              # test suite
PYTHONPATH=src .venv/bin/python -m scroll smoke --report    # exploratory toolchain smoke run
PYTHONPATH=src .venv/bin/python -m scroll run --config experiments/EXP-001.json
PYTHONPATH=src .venv/bin/python -m scroll report --run results/exploratory/EXP-001/<run-id> --pdf
```

Confirmatory configs (`experiments/EXP-002.json` and later) are accepted only if they match the frozen configurations recorded in `research/freeze.json` (protocol frozen by the owner on 2026-11-24); any changed config or protocol is refused.

Not yet implemented: confirmatory results, the demo (M5) and the experiment reports.

## Data

All experimental data are synthetic and generated locally from seeds. See [`data/manifest.json`](data/manifest.json).

## Licence

Source-available, non-commercial research licence: SCROLL Source-Available Non-Commercial Research License v1.0 ([LICENSE](LICENSE), [NOTICE.md](NOTICE.md)). It is not an OSI-approved open-source licence. Third-party material keeps its own terms.

## Citation

See [`CITATION.cff`](CITATION.cff).
