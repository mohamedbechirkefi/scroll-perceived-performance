// SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
// Port of two pure parts of the SCROLL engine: the seeded latency and failure schedule
// (src/scroll/schedule.py, src/web/schedule.js) and the zero-overhead reference model
// (src/scroll/reference.py). engine.test.ts compares it to a fixture written by the Python
// originals (scripts/export_sandbox_fixture.py). The browser harness that produced the measured
// results is not ported: nothing here measures time.

export type Path = "read" | "write";
export type Arm = "BLANK" | "SKELETON" | "PREFETCH" | "OPTIMISTIC";
export const ARMS: Record<Path, Arm[]> = { read: ["BLANK", "SKELETON", "PREFETCH"], write: ["BLANK", "OPTIMISTIC"] };
export const JITTER = 0.1;
export const K = 10;

const STREAMS: Record<string, number> = { read: 0, write: 1, decoy: 2 };
const TWO_32 = 4294967296;

export function fmix32(h: number): number {
  h = h >>> 0;
  h ^= h >>> 16;
  h = Math.imul(h, 0x85ebca6b);
  h ^= h >>> 13;
  h = Math.imul(h, 0xc2b2ae35);
  h ^= h >>> 16;
  return h >>> 0;
}

const isUint32 = (x: number) => Number.isInteger(x) && x >= 0 && x < TWO_32;

export function hash32(seed: number, stream: number, index: number, field: number): number {
  if (!isUint32(seed)) throw new RangeError("seed must be an integer in [0, 2^32)");
  if (!isUint32(stream)) throw new RangeError("stream must be an integer in [0, 2^32)");
  if (!isUint32(index) || index >= TWO_32 - 1) throw new RangeError("index must be an integer in [0, 2^32 - 1)");
  if (!isUint32(field)) throw new RangeError("field must be an integer in [0, 2^32)");
  let h = fmix32(seed);
  h = fmix32((h ^ Math.imul(stream + 1, 0x9e3779b1)) >>> 0);
  h = fmix32((h ^ Math.imul(index + 1, 0x85ebca77)) >>> 0);
  h = fmix32((h ^ Math.imul(field + 1, 0xc2b2ae3d)) >>> 0);
  return h;
}

const uniform = (seed: number, stream: string, index: number, field: number) =>
  hash32(seed, STREAMS[stream], index, field) / TWO_32;

export function delayMs(seed: number, stream: string, index: number, latencyMs: number, jitter: number): number {
  if (!Number.isFinite(latencyMs) || latencyMs < 0) throw new RangeError("latencyMs must be a finite number >= 0");
  if (!(jitter >= 0 && jitter < 1)) throw new RangeError("jitter must be in [0, 1)");
  const u = uniform(seed, stream, index, 0);
  return Math.floor(latencyMs * (1 + jitter * (2 * u - 1)) + 0.5);
}

export function succeeds(seed: number, stream: string, index: number, p: number): boolean {
  if (!(p >= 0 && p <= 1)) throw new RangeError("failure probability must be in [0, 1]");
  return !(uniform(seed, stream, index, 1) < p);
}

export interface ArmTiming {
  ttuc_lb_ms: number;
  ttff_lb_ms: number;
  false_state_lb_ms: number;
}

/** Reference model: ideal, zero-overhead timings (src/scroll/reference.py). */
export function expected(path: Path, arm: Arm, d: number, ok: boolean, leadMs: number): ArmTiming {
  if (path === "read") {
    if (arm === "BLANK") return { ttuc_lb_ms: d, ttff_lb_ms: d, false_state_lb_ms: 0 };
    if (arm === "SKELETON") return { ttuc_lb_ms: d, ttff_lb_ms: 0, false_state_lb_ms: 0 };
    if (arm === "PREFETCH") {
      const w = Math.max(0, d - leadMs);
      return { ttuc_lb_ms: w, ttff_lb_ms: w, false_state_lb_ms: 0 };
    }
  } else {
    if (arm === "BLANK") return { ttuc_lb_ms: d, ttff_lb_ms: d, false_state_lb_ms: 0 };
    if (arm === "OPTIMISTIC") return { ttuc_lb_ms: ok ? 0 : d, ttff_lb_ms: 0, false_state_lb_ms: ok ? 0 : d };
  }
  throw new RangeError(`arm ${arm} undefined for ${path} path`);
}

export interface SandboxInput {
  seed: number;
  path: Path;
  L: number;
  p: number;
  h: number;
}

export interface Trial {
  k: number;
  delay_ms: number;
  ok: boolean;
  arms: Partial<Record<Arm, ArmTiming>>;
}

export interface SandboxOutput {
  trials: Trial[];
  summary: Partial<Record<Arm, { median_ttuc_lb_ms: number; median_diff_vs_blank_ms: number }>>;
  failures: number;
}

export function median(xs: number[]): number {
  const s = [...xs].sort((a, b) => a - b);
  const n = s.length;
  if (n === 0) throw new RangeError("median of an empty list");
  return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2;
}

export function validateInput(x: SandboxInput): void {
  if (!isUint32(x.seed)) throw new RangeError("seed must be an integer from 0 to 4294967295");
  if (x.path !== "read" && x.path !== "write") throw new RangeError("path must be read or write");
  if (!Number.isFinite(x.L) || x.L < 0 || x.L > 5000) throw new RangeError("latency must be from 0 to 5000 ms");
  if (!(x.p >= 0 && x.p <= 1)) throw new RangeError("failure probability must be from 0 to 1");
  if (!Number.isFinite(x.h) || x.h < 0 || x.h > 5000) throw new RangeError("hover lead must be from 0 to 5000 ms");
}

export function simulate(x: SandboxInput): SandboxOutput {
  validateInput(x);
  const trials: Trial[] = [];
  for (let k = 0; k < K; k++) {
    const d = delayMs(x.seed, x.path, k, x.L, JITTER);
    const ok = succeeds(x.seed, x.path, k, x.path === "write" ? x.p : 0);
    const arms: Partial<Record<Arm, ArmTiming>> = {};
    for (const arm of ARMS[x.path]) arms[arm] = expected(x.path, arm, d, ok, arm === "PREFETCH" ? x.h : 0);
    trials.push({ k, delay_ms: d, ok, arms });
  }
  const summary: SandboxOutput["summary"] = {};
  for (const arm of ARMS[x.path]) {
    summary[arm] = {
      median_ttuc_lb_ms: median(trials.map((t) => t.arms[arm]!.ttuc_lb_ms)),
      median_diff_vs_blank_ms: median(trials.map((t) => t.arms[arm]!.ttuc_lb_ms - t.arms.BLANK!.ttuc_lb_ms)),
    };
  }
  return { trials, summary, failures: trials.filter((t) => !t.ok).length };
}
