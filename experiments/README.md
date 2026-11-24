<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# experiments/

Run configurations (schema `src/scroll/schemas/config-1.0.0.json`). The per-experiment protocols and reports live in `research/experiments/EXP-NNN/`.

| File | Label | Runnable now |
|---|---|---|
| `smoke.json` | exploratory | yes (`python -m scroll smoke`) |
| `EXP-001.json` | exploratory | yes (seeds 1001-1005, never confirmatory) |
| `EXP-002.json`, `EXP-003.json` | confirmatory | no: the runner refuses until the owner freezes the protocol (G-FREEZE) |
| `EXP-004-S2.json`, `EXP-004-S3.json`, `EXP-004-S4.json` | confirmatory | no (as above). S1 (frame-time method) is computed from the EXP-002 and EXP-003 data; no separate run. |

Confirmatory configs are drafts that mirror `research/protocol.md` v0.1 and will be revised with any amendment the owner accepts before the freeze.
