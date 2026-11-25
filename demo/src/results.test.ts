// SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { ResultsError, validateResults } from "./results";

const good = () => JSON.parse(readFileSync("public/data/results.json", "utf8"));

describe("validateResults", () => {
  it("accepts the exported results file", () => {
    const r = validateResults(good());
    expect(r.experiments.map((e) => e.id)).toEqual(["EXP-001", "EXP-002", "EXP-003", "EXP-004"]);
    expect(r.robustness.length).toBe(23);
  });
  it("rejects a wrong schema name", () => {
    expect(() => validateResults({ ...good(), schema: "other" })).toThrow(ResultsError);
  });
  it("rejects an unsupported major version", () => {
    expect(() => validateResults({ ...good(), schema_version: "2.0.0" })).toThrow(ResultsError);
  });
  it("rejects a missing estimate", () => {
    const r = good();
    delete r.experiments[1].estimates[0].estimate;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a non-finite number", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: "NaN", ci_low: null, ci_high: null, ci_level: null, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a half-open interval", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: 1, ci_low: 0, ci_high: null, ci_level: 0.95, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a malformed source hash", () => {
    expect(() => validateResults({ ...good(), sources: [{ path: "a", sha256: "zz" }] })).toThrow(ResultsError);
  });
  it("rejects an unknown test reading", () => {
    const r = good();
    r.experiments[1].estimates[0].reading_a = "significant";
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects missing traces", () => {
    const r = good();
    delete r.traces;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a trace median outside its interquartile range", () => {
    const r = good();
    r.traces.series.read[0].ttuc_q1_ms = r.traces.series.read[0].ttuc_median_ms + 1;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a failure trace without its false-state value", () => {
    const r = good();
    r.traces.series.write_failure[1].false_state_median_ms = null;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an unknown robustness verdict", () => {
    const r = good();
    r.robustness[0].verdict_narrow = "fine";
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a pending decision shown one way only or marked decided", () => {
    const one = good();
    one.pending_decisions[0].readings = one.pending_decisions[0].readings.slice(0, 1);
    expect(() => validateResults(one)).toThrow(ResultsError);
    const decided = good();
    decided.pending_decisions[0].state = "decided";
    expect(() => validateResults(decided)).toThrow(ResultsError);
  });
  it("rejects missing placeholders", () => {
    const r = good();
    delete r.placeholders;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
});
