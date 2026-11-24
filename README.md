<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# SCROLL

**Question:** how do loading strategies (blank, skeleton, optimistic update, prefetch) affect measurable interface responsiveness under controlled, injected delays?

**Status: M0 (bootstrap and feasibility), 2026-11-24.** No experiment has run. There are no findings. The protocol is a draft awaiting the owner's freeze.

## Why it matters

Loading strategies are often chosen because they look faster. This project measures, in a controlled local benchmark, what they change objectively: time to usable content, time to first feedback, layout shift and rollback behaviour. It makes no claim about how fast an interface feels to people.

## What exists now

- Draft protocol: [`research/protocol.md`](research/protocol.md)
- Experiment registry: [`research/experiment_registry.csv`](research/experiment_registry.csv)

| ID | Experiment | Status |
|---|---|---|
| EXP-001 | Smoke run and instrumentation validation (exploratory) | planned (protocol draft, awaiting owner freeze) |
| EXP-002 | Read path: blank vs skeleton vs prefetch | planned (protocol draft, awaiting owner freeze) |
| EXP-003 | Write path: blank vs optimistic, with failures | planned (protocol draft, awaiting owner freeze) |
| EXP-004 | Sensitivity analyses | planned (protocol draft, awaiting owner freeze) |

- Roadmap: [`roadmap.md`](roadmap.md); session journal: [`progress.md`](progress.md).
- Literature and sources: [`research/literature_review.md`](research/literature_review.md); limitations: [`research/limitations.md`](research/limitations.md).

Not yet implemented: the mock interface, the harness, tests, results, demo and reports.

## Data

All experimental data will be synthetic and generated locally from seeds. See [`data/manifest.json`](data/manifest.json).

## Licence

Source-available, non-commercial research licence: SCROLL Source-Available Non-Commercial Research License v1.0 ([LICENSE](LICENSE), [NOTICE.md](NOTICE.md)). It is not an OSI-approved open-source licence. Third-party material keeps its own terms.

## Citation

See [`CITATION.cff`](CITATION.cff).
