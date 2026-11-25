// SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
// Parity of the sandbox port with the Python engine. Tolerance: delays, outcomes and the failure
// count must be identical; every time value must agree within 1e-9 ms (all values are integers or
// half-integers in practice, so any real disagreement is at least 0.5 ms).
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { ARMS, delayMs, simulate, succeeds, type Arm, type SandboxInput } from "./engine";

const fixture = JSON.parse(readFileSync("src/fixtures/sandbox_fixture.json", "utf8"));
const TOL = 1e-9;

describe("sandbox engine parity with the Python engine", () => {
  it("uses the fixture's jitter and trial count", () => {
    expect(fixture.jitter).toBe(0.1);
    expect(fixture.k).toBe(10);
    expect(fixture.cases.length).toBeGreaterThanOrEqual(7);
  });

  for (const c of fixture.cases) {
    const inp = c.input as SandboxInput;
    it(`matches the Python schedule and reference model: ${inp.path} seed ${inp.seed} L ${inp.L} p ${inp.p} h ${inp.h}`, () => {
      const out = simulate(inp);
      expect(out.failures).toBe(c.output.failures);
      expect(out.trials.length).toBe(c.output.trials.length);
      out.trials.forEach((t, i) => {
        const want = c.output.trials[i];
        expect(t.delay_ms).toBe(want.delay_ms);
        expect(t.ok).toBe(want.ok);
        for (const arm of ARMS[inp.path] as Arm[]) {
          for (const key of ["ttuc_lb_ms", "ttff_lb_ms", "false_state_lb_ms"] as const) {
            expect(Math.abs(t.arms[arm]![key] - want.arms[arm][key])).toBeLessThanOrEqual(TOL);
          }
        }
      });
      for (const arm of ARMS[inp.path] as Arm[]) {
        expect(Math.abs(out.summary[arm]!.median_ttuc_lb_ms - c.output.summary[arm].median_ttuc_lb_ms)).toBeLessThanOrEqual(TOL);
        expect(Math.abs(out.summary[arm]!.median_diff_vs_blank_ms - c.output.summary[arm].median_diff_vs_blank_ms)).toBeLessThanOrEqual(TOL);
      }
    });
  }

  it("agrees with the page's own schedule.js on 2,000 draws", () => {
    const require = createRequire(import.meta.url);
    const S = require("../../src/web/schedule.js");
    for (let i = 0; i < 1000; i++) {
      const seed = (i * 2654435761) >>> 0;
      const L = (i * 37) % 2000;
      expect(delayMs(seed, "read", i % 50, L, 0.1)).toBe(S.delayMs(seed, "read", i % 50, L, 0.1));
      expect(succeeds(seed, "write", i % 50, 0.3)).toBe(S.succeeds(seed, "write", i % 50, 0.3));
    }
  });

  it("rejects out-of-range inputs", () => {
    expect(() => simulate({ seed: -1, path: "read", L: 100, p: 0, h: 150 })).toThrow(RangeError);
    expect(() => simulate({ seed: 1, path: "read", L: 99999, p: 0, h: 150 })).toThrow(RangeError);
    expect(() => simulate({ seed: 1, path: "write", L: 100, p: 2, h: 0 })).toThrow(RangeError);
  });
});
