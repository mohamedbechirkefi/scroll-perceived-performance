# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Differential test: the JavaScript schedule (run in Node) equals the Python schedule bit for bit."""
import json
import random
import shutil
import subprocess
from pathlib import Path

import pytest

from scroll import schedule as S

ROOT = Path(__file__).resolve().parents[1]
NODE = ROOT.parents[1] / "helix" / ".tools" / "node" / "bin" / "node"  # shared read-only Node (CLAUDE.md), found relative to the repository


def _node() -> str:
    if NODE.is_file():
        return str(NODE)
    found = shutil.which("node")
    if not found:
        pytest.skip("no Node.js available for the differential test")
    return found


def _cases(n=2000):
    rng = random.Random(20261124)
    out = [(0, "read", 0, 0, 0.0, 0.0), (2**32 - 1, "write", 2**32 - 2, 60000, 0.99, 1.0)]
    for _ in range(n):
        out.append((rng.randrange(2**32), rng.choice(list(S.STREAMS)), rng.randrange(100_000),
                    rng.choice([0, 50, 100, 300, 1000, rng.uniform(0, 5000)]), rng.choice([0.0, 0.1, rng.uniform(0, 0.99)]),
                    rng.choice([0.0, 0.1, 0.3, 0.5, 1.0, rng.random()])))
    return out


def test_js_equals_python():
    cases = _cases()
    script = (
        "const S = require(process.argv[1]); const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));"
        "process.stdout.write(JSON.stringify(cases.map(c => { const r = S.schedule(c[0], c[1], c[2], c[3], c[4], c[5]);"
        " return [S.hash32(c[0], S.STREAMS[c[1]], c[2], 0), r.delayMs, r.ok]; })));"
    )
    proc = subprocess.run([_node(), "-e", script, str(ROOT / "src" / "web" / "schedule.js")], input=json.dumps(cases),
                          capture_output=True, text=True, check=True)
    js = json.loads(proc.stdout)
    py = []
    for c in cases:
        r = S.schedule(*c)
        py.append([S.hash32(c[0], S.STREAMS[c[1]], c[2], 0), r.delay_ms, r.ok])
    mismatches = [(c, a, b) for c, a, b in zip(cases, js, py) if a != b]
    assert not mismatches, mismatches[:5]
    assert len(js) == len(cases)


def test_js_rejects_invalid_inputs():
    script = (
        "const S = require(process.argv[1]); const bad = [[-1,'read',0,1,0,0],[1.5,'read',0,1,0,0],[1,'x',0,1,0,0],"
        "[1,'read',-1,1,0,0],[1,'read',0,-1,0,0],[1,'read',0,1,1,0],[1,'write',0,1,0,2],[1,'read',0,NaN,0,0]];"
        "let n = 0; for (const b of bad) { try { S.schedule(...b); } catch (e) { if (e instanceof RangeError) n++; } }"
        "process.stdout.write(String(n));"
    )
    proc = subprocess.run([_node(), "-e", script, str(ROOT / "src" / "web" / "schedule.js")], capture_output=True, text=True, check=True)
    assert proc.stdout == "8"
