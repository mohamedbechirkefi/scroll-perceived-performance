// SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
// Visitor sandbox. Two distinct outputs, each labelled:
//  1. Sandbox output: the seeded schedule and zero-overhead lower bounds of the reference model,
//     computed in a Web Worker by an exact port of the Python engine (engine.test.ts). No timing.
//  2. Illustrative replay: the four strategies animated side by side with the scheduled delay.
//     It uses browser timers, so it is illustrative, not a measurement, and nothing is recorded.
import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { ARMS, type Arm, type Path, type SandboxInput, type SandboxOutput } from "./engine";
import type { WorkerReply, WorkerRequest } from "./sandbox.worker";
import { useSlidingIndicator } from "./motion";

const DEFAULTS: SandboxInput = { seed: 1, path: "read", L: 300, p: 0.1, h: 150 };
const P_LEVELS = [0, 0.1, 0.3, 0.5];

const fmtMs = (x: number) => (Number.isInteger(x) ? String(x) : x.toFixed(1));

export function Sandbox() {
  const worker = useRef<Worker | null>(null);
  const [input, setInput] = useState<SandboxInput>(DEFAULTS);
  const [running, setRunning] = useState(false);
  const [status, setStatus] = useState("");
  const [result, setResult] = useState<{ input: SandboxInput; output: SandboxOutput } | null>(null);
  const ids = useId();
  const seg = useSlidingIndicator(input.path);
  const [runs, setRuns] = useState(0);

  useEffect(() => {
    const w = new Worker(new URL("./sandbox.worker.ts", import.meta.url), { type: "module" });
    w.onmessage = (ev: MessageEvent<WorkerReply>) => {
      const m = ev.data;
      setRunning(false);
      if (m.type === "done") {
        setResult({ input: m.input, output: m.output });
        setRuns((n) => n + 1);
        const extra = m.input.path === "write" ? `, ${m.output.failures} of 10 saves rejected by the mock server` : "";
        setStatus(`Sandbox output ready: seed ${m.input.seed}, ${m.input.path} path, L = ${m.input.L} ms, 10 trials${extra}.`);
      }
      if (m.type === "error") setStatus(`Sandbox input not accepted: ${m.message}`);
      if (m.type === "cancelled") setStatus("Sandbox run cancelled.");
    };
    worker.current = w;
    return () => w.terminate();
  }, []);

  const run = () => {
    setRunning(true);
    setStatus("");
    worker.current?.postMessage({ type: "run", input } satisfies WorkerRequest);
  };
  const reset = () => {
    setInput(DEFAULTS);
    setResult(null);
    setStatus("Sandbox reset to the defaults.");
  };
  const set = (patch: Partial<SandboxInput>) => setInput((s) => ({ ...s, ...patch }));

  return (
    <section id="sandbox" aria-labelledby="h-sandbox" className="sandbox">
      <h2 id="h-sandbox">Sandbox</h2>
      <p className="note">
        <span className="tag tag-sandbox">Sandbox output</span> Computed in your browser from your settings by an exact
        port of the project's seeded schedule and reference model (checked against the Python engine). It gives the
        scheduled delays and the ideal, zero-overhead lower bounds of each strategy. It is not the research engine's
        browser measurement, it is not a research result, and it is not comparable to the published numbers above.
      </p>
      <div className="controls bench">
        <fieldset className="seg">
          <legend>Path</legend>
          <div className="seg-track" ref={seg.group}>
            <span className="seg-bar" ref={seg.bar} aria-hidden="true" />
          {(["read", "write"] as Path[]).map((p) => (
            <button key={p} type="button" id={`sb-path-${p}`} className="toggle" aria-pressed={input.path === p} onClick={() => set({ path: p })}>
              {p === "read" ? "Read (open an item)" : "Write (save)"}
            </button>
          ))}
          </div>
        </fieldset>
        <label>
          Seed{" "}
          <input
            id="sb-seed"
            type="number"
            min={0}
            max={4294967295}
            value={input.seed}
            onChange={(e) => set({ seed: Math.max(0, Math.min(4294967295, Math.floor(Number(e.target.value) || 0))) })}
          />
        </label>
        <label className="slider" htmlFor={`${ids}-L`}>
          Latency L: <strong>{input.L} ms</strong>
          <input id={`${ids}-L`} type="range" min={0} max={2000} step={10} value={input.L} aria-valuetext={`${input.L} ms`}
            onChange={(e) => set({ L: Number(e.target.value) })} />
        </label>
        {input.path === "read" ? (
          <label className="slider" htmlFor={`${ids}-h`}>
            Hover lead h (PREFETCH): <strong>{input.h} ms</strong>
            <input id={`${ids}-h`} type="range" min={0} max={1000} step={10} value={input.h} aria-valuetext={`${input.h} ms`}
              onChange={(e) => set({ h: Number(e.target.value) })} />
          </label>
        ) : (
          <label>
            Failure probability p{" "}
            <select id="sb-p" value={input.p} onChange={(e) => set({ p: Number(e.target.value) })}>
              {P_LEVELS.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </label>
        )}
        <div className="actions">
          <button type="button" className="btn-primary" onClick={run} disabled={running} aria-busy={running}>Run</button>
          <button type="button" className="btn-quiet" onClick={reset}>Reset</button>
        </div>
      </div>
      <p aria-live="polite" className="sandbox-out">{status}</p>
      {result && <SandboxResult key={runs} input={result.input} output={result.output} />}
    </section>
  );
}

function SandboxResult({ input, output }: { input: SandboxInput; output: SandboxOutput }) {
  const arms = ARMS[input.path];
  return (
    <>
      <div className="table-scroll" role="region" aria-label="Sandbox lower bounds" tabIndex={0}>
        <table>
          <caption className="sr-only">Sandbox output: reference-model lower bounds per strategy</caption>
          <thead>
            <tr>
              <th scope="col">Strategy (sandbox output)</th>
              <th scope="col">Median ideal TTUC (ms)</th>
              <th scope="col">Median ideal difference from BLANK (ms)</th>
            </tr>
          </thead>
          <tbody>
            {arms.map((a, i) => (
              <tr key={a} className="row-enter" style={{ animationDelay: `${i * 40}ms` }}>
                <th scope="row">{a}</th>
                <td className="num">{fmtMs(output.summary[a]!.median_ttuc_lb_ms)}</td>
                <td className="num">{fmtMs(output.summary[a]!.median_diff_vs_blank_ms)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <details>
        <summary>Scheduled trials (sandbox output)</summary>
        <div className="table-scroll" role="region" aria-label="Scheduled trials" tabIndex={0}>
          <table>
            <thead>
              <tr>
                <th scope="col">Trial</th>
                <th scope="col">Scheduled delay (ms)</th>
                <th scope="col">Server outcome</th>
                {arms.map((a) => (
                  <th scope="col" key={a}>{a} ideal TTUC (ms)</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {output.trials.map((t) => (
                <tr key={t.k}>
                  <th scope="row">{t.k + 1}</th>
                  <td className="num">{t.delay_ms}</td>
                  <td>{t.ok ? "accepted" : "rejected"}</td>
                  {arms.map((a) => (
                    <td className="num" key={a}>{fmtMs(t.arms[a]!.ttuc_lb_ms)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
      <p className="note">
        A real browser adds rendering and scheduling overhead to these bounds: in the measured runs, about 27 to 30 ms
        when no wait remains (see the published results). The bounds are a model, not an observation.
      </p>
      <Replay input={input} output={output} />
    </>
  );
}

function Replay({ input, output }: { input: SandboxInput; output: SandboxOutput }) {
  const [k, setK] = useState(0);
  const [slow, setSlow] = useState(false);
  const [elapsed, setElapsed] = useState<number | null>(null);
  const raf = useRef<number | null>(null);
  const ids = useId();
  const t = output.trials[Math.min(k, output.trials.length - 1)];
  const arms = ARMS[input.path];
  const endAt = t.delay_ms + 400;

  useEffect(() => () => { if (raf.current !== null) cancelAnimationFrame(raf.current); }, []);

  const play = () => {
    if (raf.current !== null) cancelAnimationFrame(raf.current);
    const start = performance.now();
    const factor = slow ? 4 : 1;
    const tick = () => {
      const e = (performance.now() - start) / factor;
      setElapsed(Math.min(e, endAt));
      if (e < endAt) raf.current = requestAnimationFrame(tick);
      else raf.current = null;
    };
    setElapsed(0);
    raf.current = requestAnimationFrame(tick);
  };

  return (
    <div className="replay">
      <h3>
        <span className="tag tag-illustrative">Illustrative, not a measurement</span> Side-by-side replay
      </h3>
      <p className="note">
        Replays one scheduled trial with every strategy at once, using the scheduled delay and the reference model.
        Browser timers drive the animation, so its timing is approximate and nothing is recorded or reported.
      </p>
      <div className="controls">
        <label>
          Trial{" "}
          <select id="replay-trial" value={k} onChange={(e) => { setK(Number(e.target.value)); setElapsed(null); }}>
            {output.trials.map((x) => (
              <option key={x.k} value={x.k}>{x.k + 1} (delay {x.delay_ms} ms{input.path === "write" ? (x.ok ? ", accepted" : ", rejected") : ""})</option>
            ))}
          </select>
        </label>
        <label htmlFor={`${ids}-slow`}>
          <input id={`${ids}-slow`} type="checkbox" checked={slow} onChange={(e) => setSlow(e.target.checked)} /> Slow motion (4x)
        </label>
        <button type="button" className="btn-secondary" onClick={play}>Replay trial</button>
      </div>
      <p className="replay-clock">
        <span className="clock-label">Replay clock</span>
        <span className="readout">{elapsed === null ? "not started" : `${Math.round(elapsed)} ms`}</span>
        {elapsed !== null && <span className="clock-label">after the click</span>}
      </p>
      <div className="mini-grid">
        {arms.map((a) => (
          <MiniPanel key={a} arm={a} path={input.path} elapsed={elapsed} delay={t.delay_ms} ok={t.ok}
            ttuc={t.arms[a]!.ttuc_lb_ms} ttff={t.arms[a]!.ttff_lb_ms} h={input.h} />
        ))}
      </div>
    </div>
  );
}

function MiniPanel(props: { arm: Arm; path: Path; elapsed: number | null; delay: number; ok: boolean; ttuc: number; ttff: number; h: number }) {
  const { arm, path, elapsed, ok, ttuc, ttff } = props;
  const e = elapsed ?? -1;
  let body: ReactNode;
  let caption: string;
  if (path === "read") {
    if (e < 0) { body = <div className="mini-empty" />; caption = "before the click"; }
    else if (e >= ttuc) { body = <div className="mini-content"><strong>Item detail</strong><span>Usable content</span></div>; caption = `usable content (ideal ${fmtMs(ttuc)} ms)`; }
    else if (e >= ttff) { body = <div className="mini-skel" aria-hidden="true"><i /><i /><i /></div>; caption = "placeholder shown, content not usable"; }
    else { body = <div className="mini-empty" />; caption = arm === "PREFETCH" ? "waiting for the prefetched response" : "nothing new shown"; }
  } else {
    const before = <span className="mini-btn">Save</span>;
    const after = <span className="mini-btn on">Saved</span>;
    if (e < 0) { body = before; caption = "before the click"; }
    else if (arm === "OPTIMISTIC") {
      if (ok) { body = after; caption = "final state shown at once"; }
      else if (e < props.delay) { body = after; caption = "false state shown (server will reject)"; }
      else { body = <>{before}<span className="mini-err">Could not save</span></>; caption = "rolled back with an error message"; }
    } else if (e < props.delay) { body = before; caption = "old state kept while waiting"; }
    else if (ok) { body = after; caption = "final state after the server confirms"; }
    else { body = <>{before}<span className="mini-err">Could not save</span></>; caption = "old state with an error message"; }
  }
  return (
    <figure className="mini">
      <figcaption><strong>{arm}</strong></figcaption>
      <div className={`mini-box${path === "read" && e >= 0 && e >= ttff && e < ttuc ? " is-skel" : ""}`}>{body}</div>
      <p className="meta">{caption}</p>
    </figure>
  );
}
