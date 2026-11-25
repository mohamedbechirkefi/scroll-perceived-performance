// SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
// Published results: loaded from public/data/results.json, which
// scripts/export_demo_data.py writes from committed results only.
// Validation fails closed: any missing or malformed field means no numbers are shown.

export const SCHEMA = "lab-demo-results";
export const SCHEMA_MAJOR = 1;

export interface Estimate {
  label: string;
  estimate: number;
  ci_low: number | null;
  ci_high: number | null;
  ci_level: number | null;
  unit: string;
  /** Exact text the manuscript prints for the estimate and interval; shown verbatim when present. */
  display: string | null;
  interval_display: string | null;
  /** SCROLL fields (optional in the schema; validated when present). */
  group: string | null;
  seeds: number | null;
  holm_p_display: string | null;
  reading_a: string | null;
  reading_b: string | null;
  tost_display: string | null;
  claim_id: string | null;
}

export interface Experiment {
  id: string;
  title: string;
  status: string;
  verdict: string;
  estimates: Estimate[];
  claim_ids: string[];
  report_path: string;
  notes: string[];
}

export interface Assumption {
  name: string;
  value: string;
  source: string;
}

export interface Source {
  path: string;
  sha256: string;
}

export interface Results {
  schema: string;
  schema_version: string;
  project: string;
  question: string;
  status_label: string;
  code_revision: string;
  sources: Source[];
  experiments: Experiment[];
  assumptions: Assumption[];
  limitations: string[];
  traces: Traces;
  robustness: Robustness[];
  pending_decisions: PendingDecision[];
  placeholders: string[];
}

export interface TracePoint {
  L: number;
  arm: string;
  trials: number;
  ttff_median_ms: number | null;
  ttuc_median_ms: number;
  ttuc_q1_ms: number | null;
  ttuc_q3_ms: number | null;
  false_state_median_ms: number | null;
  display: { ttff: string | null; ttuc: string; iqr: string | null; false_state: string | null };
}

export interface Traces {
  note: string;
  sources: string[];
  series: { read: TracePoint[]; write_success: TracePoint[]; write_failure: TracePoint[] };
}

export interface Robustness {
  contrast: string;
  verdict_dec011: string;
  verdict_narrow: string;
}

export interface PendingDecision {
  id: string;
  title: string;
  state: string;
  readings: { label: string; text: string }[];
}

export class ResultsError extends Error {}

type Obj = Record<string, unknown>;

function obj(v: unknown, where: string): Obj {
  if (typeof v !== "object" || v === null || Array.isArray(v)) {
    throw new ResultsError(`${where}: expected an object`);
  }
  return v as Obj;
}

function str(o: Obj, k: string, where: string): string {
  const v = o[k];
  if (typeof v !== "string" || v.length === 0) {
    throw new ResultsError(`${where}.${k}: expected a non-empty string`);
  }
  return v;
}

function num(o: Obj, k: string, where: string, nullable = false): number | null {
  const v = o[k];
  if (nullable && v === null) return null;
  if (typeof v !== "number" || !Number.isFinite(v)) {
    throw new ResultsError(`${where}.${k}: expected a finite number`);
  }
  return v;
}

function arr(o: Obj, k: string, where: string): unknown[] {
  const v = o[k];
  if (!Array.isArray(v)) throw new ResultsError(`${where}.${k}: expected an array`);
  return v;
}

function strArr(o: Obj, k: string, where: string): string[] {
  return arr(o, k, where).map((v, i) => {
    if (typeof v !== "string") throw new ResultsError(`${where}.${k}[${i}]: expected a string`);
    return v;
  });
}

function optStr(o: Obj, k: string, where: string): string | null {
  const v = o[k];
  if (v === undefined || v === null) return null;
  if (typeof v !== "string" || v.length === 0) throw new ResultsError(`${where}.${k}: expected a non-empty string or null`);
  return v;
}

function optNum(o: Obj, k: string, where: string): number | null {
  const v = o[k];
  if (v === undefined || v === null) return null;
  if (typeof v !== "number" || !Number.isFinite(v)) throw new ResultsError(`${where}.${k}: expected a finite number or null`);
  return v;
}

function optEnum(o: Obj, k: string, where: string, allowed: string[]): string | null {
  const v = optStr(o, k, where);
  if (v !== null && !allowed.includes(v)) throw new ResultsError(`${where}.${k}: unexpected value "${v}"`);
  return v;
}

function tracePoint(v: unknown, where: string, kind: "timeline" | "failure"): TracePoint {
  const o = obj(v, where);
  const d = obj(o.display, `${where}.display`);
  const p: TracePoint = {
    L: num(o, "L", where) as number,
    arm: str(o, "arm", where),
    trials: num(o, "trials", where) as number,
    ttff_median_ms: num(o, "ttff_median_ms", where, true),
    ttuc_median_ms: num(o, "ttuc_median_ms", where) as number,
    ttuc_q1_ms: num(o, "ttuc_q1_ms", where, true),
    ttuc_q3_ms: num(o, "ttuc_q3_ms", where, true),
    false_state_median_ms: num(o, "false_state_median_ms", where, true),
    display: {
      ttff: optStr(d, "ttff", `${where}.display`),
      ttuc: str(d, "ttuc", `${where}.display`),
      iqr: optStr(d, "iqr", `${where}.display`),
      false_state: optStr(d, "false_state", `${where}.display`),
    },
  };
  if (p.trials <= 0 || p.L <= 0) throw new ResultsError(`${where}: trials and L must be positive`);
  if (kind === "timeline") {
    if (p.ttff_median_ms === null || p.ttuc_q1_ms === null || p.ttuc_q3_ms === null || p.display.ttff === null || p.display.iqr === null) {
      throw new ResultsError(`${where}: a timeline point needs TTFF, the interquartile range and their display text`);
    }
    if (!(p.ttuc_q1_ms <= p.ttuc_median_ms && p.ttuc_median_ms <= p.ttuc_q3_ms)) {
      throw new ResultsError(`${where}: the median must lie inside the interquartile range`);
    }
  } else if (p.false_state_median_ms === null || p.display.false_state === null) {
    throw new ResultsError(`${where}: a failure point needs the false-state median and its display text`);
  }
  for (const x of [p.ttff_median_ms, p.ttuc_median_ms, p.ttuc_q1_ms, p.ttuc_q3_ms, p.false_state_median_ms]) {
    if (x !== null && x < 0) throw new ResultsError(`${where}: negative time`);
  }
  return p;
}

function series(o: Obj, k: string, where: string, kind: "timeline" | "failure"): TracePoint[] {
  const xs = arr(o, k, where).map((v, i) => tracePoint(v, `${where}.${k}[${i}]`, kind));
  if (xs.length === 0) throw new ResultsError(`${where}.${k}: empty`);
  return xs;
}

function traces(v: unknown): Traces {
  const o = obj(v, "traces");
  const s = obj(o.series, "traces.series");
  return {
    note: str(o, "note", "traces"),
    sources: strArr(o, "sources", "traces"),
    series: {
      read: series(s, "read", "traces.series", "timeline"),
      write_success: series(s, "write_success", "traces.series", "timeline"),
      write_failure: series(s, "write_failure", "traces.series", "failure"),
    },
  };
}

const VERDICTS = ["robust", "method-dependent", "condition-dependent", "method-dependent and condition-dependent", "no sensitivity level"];

function estimate(v: unknown, where: string): Estimate {
  const o = obj(v, where);
  const e: Estimate = {
    label: str(o, "label", where),
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where, true),
    ci_high: num(o, "ci_high", where, true),
    ci_level: num(o, "ci_level", where, true),
    unit: typeof o.unit === "string" ? o.unit : "",
    display: typeof o.display === "string" ? o.display : null,
    interval_display: typeof o.interval_display === "string" ? o.interval_display : null,
    group: optStr(o, "group", where),
    seeds: optNum(o, "seeds", where),
    holm_p_display: optStr(o, "holm_p_display", where),
    reading_a: optEnum(o, "reading_a", where, ["reject", "not rejected"]),
    reading_b: optEnum(o, "reading_b", where, ["excludes 0", "includes 0"]),
    tost_display: optStr(o, "tost_display", where),
    claim_id: optStr(o, "claim_id", where),
  };
  if ((e.ci_low === null) !== (e.ci_high === null)) {
    throw new ResultsError(`${where}: interval must have both bounds or neither`);
  }
  if (e.ci_low !== null && e.ci_high !== null && e.ci_low > e.ci_high) {
    throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  }
  return e;
}

export function validateResults(raw: unknown): Results {
  const o = obj(raw, "results");
  if (o.schema !== SCHEMA) throw new ResultsError(`results.schema: expected "${SCHEMA}"`);
  const version = str(o, "schema_version", "results");
  if (Number(version.split(".")[0]) !== SCHEMA_MAJOR) {
    throw new ResultsError(`results.schema_version: unsupported major version ${version}`);
  }
  const experiments = arr(o, "experiments", "results").map((v, i) => {
    const w = `experiments[${i}]`;
    const e = obj(v, w);
    return {
      id: str(e, "id", w),
      title: str(e, "title", w),
      status: str(e, "status", w),
      verdict: str(e, "verdict", w),
      estimates: arr(e, "estimates", w).map((x, j) => estimate(x, `${w}.estimates[${j}]`)),
      claim_ids: strArr(e, "claim_ids", w),
      report_path: str(e, "report_path", w),
      notes: strArr(e, "notes", w),
    };
  });
  if (experiments.length === 0) throw new ResultsError("results.experiments: empty");
  return {
    schema: SCHEMA,
    schema_version: version,
    project: str(o, "project", "results"),
    question: str(o, "question", "results"),
    status_label: str(o, "status_label", "results"),
    code_revision: str(o, "code_revision", "results"),
    sources: arr(o, "sources", "results").map((v, i) => {
      const s = obj(v, `sources[${i}]`);
      const sha = str(s, "sha256", `sources[${i}]`);
      if (!/^[0-9a-f]{64}$/.test(sha)) throw new ResultsError(`sources[${i}].sha256: not a sha256`);
      return { path: str(s, "path", `sources[${i}]`), sha256: sha };
    }),
    experiments,
    assumptions: arr(o, "assumptions", "results").map((v, i) => {
      const a = obj(v, `assumptions[${i}]`);
      return {
        name: str(a, "name", `assumptions[${i}]`),
        value: str(a, "value", `assumptions[${i}]`),
        source: str(a, "source", `assumptions[${i}]`),
      };
    }),
    limitations: strArr(o, "limitations", "results"),
    traces: traces(o.traces),
    robustness: arr(o, "robustness", "results").map((v, i) => {
      const w = `robustness[${i}]`;
      const r = obj(v, w);
      const out = { contrast: str(r, "contrast", w), verdict_dec011: str(r, "verdict_dec011", w), verdict_narrow: str(r, "verdict_narrow", w) };
      if (!VERDICTS.includes(out.verdict_dec011) || !VERDICTS.includes(out.verdict_narrow)) throw new ResultsError(`${w}: unknown verdict`);
      return out;
    }),
    pending_decisions: arr(o, "pending_decisions", "results").map((v, i) => {
      const w = `pending_decisions[${i}]`;
      const d = obj(v, w);
      const readings = arr(d, "readings", w).map((x, j) => {
        const r = obj(x, `${w}.readings[${j}]`);
        return { label: str(r, "label", `${w}.readings[${j}]`), text: str(r, "text", `${w}.readings[${j}]`) };
      });
      if (readings.length < 2) throw new ResultsError(`${w}: a pending decision must show at least two readings`);
      const state = str(d, "state", w);
      if (state !== "pending owner decision") throw new ResultsError(`${w}.state: expected "pending owner decision"`);
      return { id: str(d, "id", w), title: str(d, "title", w), state, readings };
    }),
    placeholders: strArr(o, "placeholders", "results"),
  };
}

export async function loadResults(url = "./data/results.json"): Promise<Results> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new ResultsError(`could not load ${url} (HTTP ${res.status})`);
  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw new ResultsError(`${url} is not valid JSON`);
  }
  return validateResults(raw);
}

/** Formats a number for display without inventing precision. */
export function fmt(x: number, digits = 3): string {
  if (Number.isInteger(x)) return x.toString();
  return Number(x.toPrecision(digits)).toString();
}

export function fmtEstimate(e: Estimate, digits = 3): string {
  return e.display ?? `${fmt(e.estimate, digits)}${e.unit ? " " + e.unit : ""}`;
}

export function fmtInterval(e: Estimate, digits = 3): string {
  if (e.interval_display !== null) return e.interval_display;
  if (e.ci_low === null || e.ci_high === null) return "no interval";
  const level = e.ci_level === null ? "" : `${Math.round(e.ci_level * 100)}% `;
  return `${level}[${fmt(e.ci_low, digits)}, ${fmt(e.ci_high, digits)}]`;
}
