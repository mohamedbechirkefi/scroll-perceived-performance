// SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
// Side-by-side traces of the measured cell medians, with a latency slider. Hand-written SVG.
import { useEffect, useId, useRef, useState } from "react";
import type { Estimate, Results, TracePoint } from "./results";
import { useSeenOnce, useSlidingIndicator } from "./motion";

type View = "read" | "write_success" | "write_failure";

const VIEWS: { key: View; label: string }[] = [
  { key: "read", label: "Read path (open an item)" },
  { key: "write_success", label: "Write path, successful saves (p = 0)" },
  { key: "write_failure", label: "Write path, failed saves" },
];

const ROW = 60;
const RIGHT = 16;
const TOP = 42;

function contrastsFor(r: Results, view: View, L: number): Estimate[] {
  const by = (id: string) => r.experiments.find((e) => e.id === id)?.estimates ?? [];
  if (view === "read") return by("EXP-002").filter((x) => x.label.startsWith(`L = ${L} ms:`));
  if (view === "write_success") return by("EXP-003").filter((x) => x.label.startsWith(`L = ${L} ms, p = 0, success`));
  return by("EXP-003").filter((x) => x.label.startsWith(`L = ${L} ms,`) && x.group === "failure");
}

export function Traces({ r }: { r: Results }) {
  const [view, setView] = useState<View>("read");
  // The SVG is drawn at the figure's own pixel width so that its text stays legible on phones.
  const fig = useRef<HTMLElement | null>(null);
  const [W, setW] = useState(720);
  useEffect(() => {
    const el = fig.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver((es) => setW(Math.max(300, Math.round(es[0].contentRect.width))));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  const LEFT = W < 500 ? 88 : 112;
  const points = r.traces.series[view];
  const levels = [...new Set(points.map((p) => p.L))].sort((a, b) => a - b);
  const [idx, setIdx] = useState(2);
  const i = Math.min(idx, levels.length - 1);
  const L = levels[i];
  const rows = points.filter((p) => p.L === L);
  const sliderId = useId();
  const max = Math.max(L * 1.12, ...rows.map((p) => (p.ttuc_q3_ms ?? p.ttuc_median_ms) * 1.08));
  const x = (ms: number) => LEFT + (ms / max) * (W - LEFT - RIGHT);
  const H = TOP + rows.length * ROW + 50;
  const ticks = niceTicks(max, W < 500 ? 3 : 5);
  const contrasts = contrastsFor(r, view, L);
  const seg = useSlidingIndicator(view);
  const [seenRef, seen] = useSeenOnce<HTMLDivElement>();

  return (
    <section id="traces" aria-labelledby="h-traces">
      <h2 id="h-traces">Side-by-side traces</h2>
      <p className="note">
        <span className="tag tag-measured">Measured</span> {r.traces.note}
      </p>
      <div className="controls" role="group" aria-label="Trace view">
        <fieldset className="seg">
          <legend>Scenario</legend>
          <div className="seg-track" ref={seg.group}>
            <span className="seg-bar" ref={seg.bar} aria-hidden="true" />
          {VIEWS.map((v) => (
            <button key={v.key} type="button" id={`trace-view-${v.key}`} className="toggle" aria-pressed={view === v.key} onClick={() => setView(v.key)}>
              {v.label}
            </button>
          ))}
          </div>
        </fieldset>
        <label htmlFor={sliderId} className="slider">
          Injected latency L: <strong>{L} ms</strong>
          <input
            id={sliderId}
            type="range"
            min={0}
            max={levels.length - 1}
            step={1}
            value={i}
            aria-valuetext={`${L} ms`}
            onChange={(e) => setIdx(Number(e.target.value))}
          />
          <span className="meta">measured levels: {levels.join(", ")} ms</span>
        </label>
      </div>

      <div ref={seenRef} className={`reveal reveal-${seen}`}>
      <figure className="chart film-chart" ref={fig}>
        <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-labelledby={`${sliderId}-t ${sliderId}-d`}>
          <title id={`${sliderId}-t`}>Measured trace at L = {L} ms</title>
          <desc id={`${sliderId}-d`}>{describe(view, rows)}</desc>
          {ticks.map((t) => (
            <g key={t}>
              <line x1={x(t)} x2={x(t)} y1={TOP - 6} y2={H - 44} className="grid" />
              <text x={x(t)} y={H - 26} textAnchor="middle" className="axis">{t}</text>
            </g>
          ))}
          <text x={W - RIGHT} y={H - 6} textAnchor="end" className="axis">time after the click (ms)</text>
          <line x1={x(L)} x2={x(L)} y1={TOP - 16} y2={H - 44} className="delay" />
          <text x={x(L) > W * 0.6 ? x(L) - 4 : x(L) + 4} y={TOP - 20} textAnchor={x(L) > W * 0.6 ? "end" : "start"} className="axis">L = {L} ms (nominal delay)</text>
          {rows.map((p, k) => (
            <Row key={p.arm} k={k} p={p} y={TOP + k * ROW} x={x} failure={view === "write_failure"} left={LEFT} full={W - RIGHT} />
          ))}
        </svg>
        <figcaption>
          {view === "write_failure" ? (
            <>
              Each track ends at the median time to the final state on a failed save (old state restored with an error
              message), marked by the dark sweep line; the bright segment after it is the final state. The red band shows how long OPTIMISTIC displayed a false state (median duration); it is drawn
              ending at the final state, so its start is approximate. BLANK displayed no false state.
            </>
          ) : (
            <>
              Each track is drawn as a strip of film. Dark segment: nothing new shown yet. Amber segment: feedback
              or a placeholder is shown, or the old state is kept, but the content is not usable; its start (the amber
              split mark) is the TTFF median. Bright segment: usable content, from the TTUC median (the red sweep mark).
              The thin bar under each track is the interquartile range of TTUC over trials. The dashed line marks the
              nominal injected delay. The sprocket holes are decoration, not a time scale.
            </>
          )}
        </figcaption>
      </figure>
      </div>

      <div className="table-scroll" role="region" aria-label="Trace values" tabIndex={0}>
        <table>
          <caption className="sr-only">Cell medians at L = {L} ms</caption>
          <thead>
            <tr>
              <th scope="col">Arm</th>
              <th scope="col">Trials</th>
              {view !== "write_failure" && <th scope="col">TTFF median (ms)</th>}
              <th scope="col">{view === "write_failure" ? "Time to final state, median (ms)" : "TTUC median (ms)"}</th>
              {view !== "write_failure" && <th scope="col">TTUC interquartile range (ms)</th>}
              {view === "write_failure" && <th scope="col">False state shown, median (ms)</th>}
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.arm}>
                <th scope="row">{p.arm}</th>
                <td>{p.trials}</td>
                {view !== "write_failure" && <td className="num">{p.display.ttff}</td>}
                <td className="num">{p.display.ttuc}</td>
                {view !== "write_failure" && <td className="num">{p.display.iqr}</td>}
                {view === "write_failure" && <td className="num">{p.display.false_state}</td>}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {contrasts.length > 0 && (
        <div className="panel contrast">
          <p><strong>Published contrasts at L = {L} ms</strong> (median over seeds, 95% CI, from the results below):</p>
          <ul>
            {contrasts.map((c) => (
              <li key={c.label}>
                {c.label}: <span className="num">{c.display}</span> ms, 95% CI <span className="num">{c.interval_display}</span> ms;
                reading A {c.reading_a}, reading B {c.reading_b}
                {c.tost_display ? <>; TOST 90% CI {c.tost_display}</> : null}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

// Film-strip chrome around a measured track: the strip and its sprocket holes are decoration
// and carry no time scale; only the segments and the markers encode the measured medians.
function Strip({ y, h, left, full }: { y: number; h: number; left: number; full: number }) {
  const holes: number[] = [];
  for (let hx = left + 4; hx < full - 6; hx += 14) holes.push(hx);
  return (
    <g aria-hidden="true">
      <rect x={left} y={y - 8} width={full - left} height={h + 16} className="strip" />
      {holes.map((hx) => (
        <g key={hx}>
          <rect x={hx} y={y - 6} width={6} height={4} rx={1} className="sprocket" />
          <rect x={hx} y={y + h + 2} width={6} height={4} rx={1} className="sprocket" />
        </g>
      ))}
    </g>
  );
}

function Row({ p, y, x, failure, left, full, k }: { p: TracePoint; y: number; x: (ms: number) => number; failure: boolean; left: number; full: number; k: number }) {
  const h = 20;
  const end = x(0);
  if (failure) {
    const fsStart = Math.max(0, p.ttuc_median_ms - (p.false_state_median_ms ?? 0));
    return (
      <g className="track" style={{ animationDelay: `${k * 60}ms` }}>
        <text x={left - 10} y={y + h / 2 + 5} textAnchor="end" className="armlabel">{p.arm}</text>
        <Strip y={y} h={h} left={end} full={full} />
        <rect x={end} y={y} width={x(p.ttuc_median_ms) - end} height={h} className="seg-wait" />
        {(p.false_state_median_ms ?? 0) > 0 && (
          <rect x={x(fsStart)} y={y} width={x(p.ttuc_median_ms) - x(fsStart)} height={h} className="seg-false" />
        )}
        <rect x={x(p.ttuc_median_ms)} y={y} width={Math.max(0, full - x(p.ttuc_median_ms))} height={h} className="seg-final" />
        <line x1={x(p.ttuc_median_ms)} x2={x(p.ttuc_median_ms)} y1={y - 13} y2={y + h + 13} className="marker marker-final" />
      </g>
    );
  }
  const ttff = p.ttff_median_ms ?? 0;
  return (
    <g className="track" style={{ animationDelay: `${k * 60}ms` }}>
      <text x={left - 10} y={y + h / 2 + 5} textAnchor="end" className="armlabel">{p.arm}</text>
      <Strip y={y} h={h} left={end} full={full} />
      <rect x={end} y={y} width={Math.max(0, x(Math.min(ttff, p.ttuc_median_ms)) - end)} height={h} className="seg-none" />
      {ttff < p.ttuc_median_ms && (
        <rect x={x(ttff)} y={y} width={x(p.ttuc_median_ms) - x(ttff)} height={h} className="seg-wait" />
      )}
      <rect x={x(p.ttuc_median_ms)} y={y} width={Math.max(0, full - x(p.ttuc_median_ms))} height={h} className="seg-final" />
      {ttff < p.ttuc_median_ms && <line x1={x(ttff)} x2={x(ttff)} y1={y - 3} y2={y + h + 3} className="marker-split" />}
      <line x1={x(p.ttuc_q1_ms ?? 0)} x2={x(p.ttuc_q3_ms ?? 0)} y1={y + h + 14} y2={y + h + 14} className="iqr" />
      <line x1={x(p.ttuc_median_ms)} x2={x(p.ttuc_median_ms)} y1={y - 8} y2={y + h + 18} className="marker" />
    </g>
  );
}

function niceTicks(max: number, n: number): number[] {
  const raw = max / n;
  const pow = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 5, 10].map((m) => m * pow).find((s) => s >= raw) ?? raw;
  const out: number[] = [];
  for (let t = 0; t <= max; t += step) out.push(Math.round(t));
  return out;
}

function describe(view: View, rows: TracePoint[]): string {
  if (view === "write_failure") {
    return rows
      .map((p) => `${p.arm}: final state at a median of ${p.display.ttuc} ms; false state shown for a median of ${p.display.false_state} ms.`)
      .join(" ");
  }
  return rows
    .map((p) => `${p.arm}: first feedback at a median of ${p.display.ttff} ms; usable content at a median of ${p.display.ttuc} ms (interquartile range ${p.display.iqr} ms).`)
    .join(" ");
}
