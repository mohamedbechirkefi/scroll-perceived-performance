// SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
import { useEffect, useState } from "react";
import { fmtEstimate, fmtInterval, loadResults, ResultsError, type Experiment, type Results } from "./results";
import { Traces } from "./Traces";
import { Sandbox } from "./Sandbox";
import { HeroIllustration } from "./Hero";

const REPO = "https://github.com/mohamedbechirkefi/scroll-perceived-performance";
const LABS = "https://labs.kefimohamedbechir.workers.dev";

type State = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; results: Results };

export function App() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    loadResults()
      .then((results) => setState({ kind: "ready", results }))
      .catch((e: unknown) =>
        setState({ kind: "error", message: e instanceof ResultsError ? e.message : "results could not be loaded" }),
      );
  }, []);

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <header className="site">
        <div className="bar">
          <a className="brand" href="#top" aria-label="SCROLL, back to the top">
            <img src="brand/scroll-lockup.svg" alt="" width="118" height="30" />
          </a>
          <nav aria-label="Sections">
            <a href="#traces">Traces</a>
            <a href="#overview">Overview</a>
            <a href="#results">Results</a>
            <a href="#assumptions">Assumptions</a>
            <a href="#method">Method and limitations</a>
            <a href="#sandbox">Sandbox</a>
          </nav>
        </div>
      </header>
      <div className="hero" id="top">
        <div className="hero-copy">
          <p className="hero-kicker">SCROLL, a single-browser timing benchmark</p>
          <h1>Do loading strategies deliver usable content sooner, or only feedback?</h1>
          <p className="hero-answer">
            Prefetching, and optimistic saves that succeed, delivered the usable state sooner. A skeleton changed what
            appeared first: its time to usable content stayed within the 17 ms equivalence margin of a blank page at
            delays of 100 ms and more, and at the shortest delay that verdict is not robust.
          </p>
          <p className="hero-by">Mohamed Bechir Kefi, independent researcher. Preprint draft, not peer-reviewed.</p>
          <p className="hero-actions">
            <a className="btn-primary" href="#traces">See the measured traces</a>
          </p>
        </div>
        <HeroIllustration />
      </div>
      <main id="main" className="wrap">
        {state.kind === "loading" && <p role="status">Loading the published results.</p>}
        {state.kind === "error" && (
          <div role="alert" className="panel error">
            <h2>Results unavailable</h2>
            <p>The published results file failed validation, so no numbers are shown.</p>
            <p><code>{state.message}</code></p>
          </div>
        )}
        {state.kind === "ready" && <Published r={state.results} />}
        <Sandbox />
      </main>
      <footer className="site">
        <div className="wrap foot">
          <img className="foot-mark" src="brand/scroll-lockup-on-dark.svg" alt="SCROLL" width="134" height="34" />
          <ul className="foot-links">
            <li><a href={REPO}>Source repository on GitHub</a></li>
            <li><a href={`${REPO}/blob/main/research/paper/manuscript.md`}>Manuscript (preprint draft)</a></li>
            <li><a href={LABS}>All lab studies</a></li>
          </ul>
          <p>Mohamed Bechir Kefi, independent researcher.</p>
          <p>
            Runs offline after the first load. No data about visitors is collected, stored or sent anywhere, and the
            page contacts no server other than the one that served it.
          </p>
          <p>
            Source-available, non-commercial research licence: SCROLL Source-Available Non-Commercial Research License
            v1.0. It is not an OSI-approved open-source licence. An AI system was used as a research and development
            assistant; it is not an author.
          </p>
          <p>
            Typefaces: Big Shoulders Display and Libre Franklin, both under the SIL Open Font License 1.1, self-hosted.
          </p>
        </div>
      </footer>
    </>
  );
}

function Legend() {
  return (
    <ul className="legend" aria-label="Labels used on this page">
      <li><span className="tag tag-measured">Measured</span> published benchmark result from committed files</li>
      <li><span className="tag tag-assumption">Assumption</span> design parameter or model, not a result</li>
      <li><span className="tag tag-sandbox">Sandbox output</span> computed in your browser from your settings</li>
      <li><span className="tag tag-illustrative">Illustrative, not a measurement</span> animated replay</li>
    </ul>
  );
}

function Published({ r }: { r: Results }) {
  return (
    <>
      <Traces r={r} />

      <section id="overview" aria-labelledby="h-overview">
        <h2 id="h-overview">Overview</h2>
        <p className="lede">{r.question}</p>
        <p className="status-label"><strong>Status.</strong> {r.status_label}</p>
        <p>
          One mock page was driven by scripted input in one browser. Each loading strategy saw the same seeded delays.
          The primary metric is time to usable content (TTUC): from the click to the first frame that shows the final,
          correct and usable state. Time to first feedback (TTFF) is secondary. Lower is better for both.
        </p>
        <Legend />
        {r.pending_decisions.map((d) => (
          <div key={d.id} className="panel pending" role="note" aria-labelledby={`h-${d.id}`}>
            <h3 id={`h-${d.id}`}>
              <span className="tag tag-pending">{d.state}</span> {d.id}: {d.title}
            </h3>
            <p>The owner chose no reading (2026-11-26). Each reading the manuscript reports is shown:</p>
            <dl className="readings">
              {d.readings.map((x) => (
                <div key={x.label}>
                  <dt>{x.label}</dt>
                  <dd>{x.text}</dd>
                </div>
              ))}
            </dl>
          </div>
        ))}
      </section>

      <section id="results" aria-labelledby="h-results">
        <h2 id="h-results">Published results</h2>
        <p className="note">
          <span className="tag tag-measured">Measured</span> These numbers come from the committed results at code
          revision <code>{r.code_revision}</code> and are printed exactly as in the manuscript. Each contrast is the
          median over seeds of per-seed median trial-paired differences against BLANK, in ms, with a 95% percentile
          bootstrap interval over seeds. Null results are listed with the same weight as positive ones. Reading A
          (Holm-adjusted Wilcoxon) and reading B (the unadjusted interval) are both shown, because the owner chose neither
          reading of DEC-011.
        </p>
        {r.experiments.map((e) => (
          <ExperimentPanel key={e.id} e={e} r={r} />
        ))}
      </section>

      <section id="assumptions" aria-labelledby="h-assumptions">
        <h2 id="h-assumptions">Assumptions</h2>
        <p className="note">
          <span className="tag tag-assumption">Assumption</span> Design parameters of the frozen protocol and the
          reference model. They are inputs, not results.
        </p>
        <dl className="assumptions">
          {r.assumptions.map((a) => (
            <div key={a.name}>
              <dt>{a.name}</dt>
              <dd>
                {a.value} <span className="meta">({a.source})</span>
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <section id="method" aria-labelledby="h-method">
        <h2 id="h-method">Method and limitations</h2>
        <p>
          The protocol (v1.0) was frozen by the owner on 2026-11-24 before any confirmatory run, and a run guard refused
          any configuration that differed from the frozen one. The seed is the independent unit. The hypothesis test is
          the two-sided Wilcoxon signed-rank test with Holm correction over each experiment's primary family (8 contrasts
          in EXP-002, 15 in EXP-003); the skeleton equivalence uses two one-sided tests with a 17 ms margin. The full
          method is in <code>research/paper/manuscript.md</code> and the experiment reports.
        </p>
        <h3>Limitations</h3>
        <ol className="limitations">
          {r.limitations.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ol>
        <h3>Author, funding and addresses</h3>
        <ul className="facts">
          {r.placeholders.map((p) => (
            <li key={p}>{p}</li>
          ))}
        </ul>
        <details>
          <summary>Source files and hashes</summary>
          <ul className="meta">
            {r.sources.map((s) => (
              <li key={s.path}>
                <code>{s.path}</code> <code>{s.sha256.slice(0, 12)}</code>
              </li>
            ))}
          </ul>
        </details>
      </section>
    </>
  );
}

function ExperimentPanel({ e, r }: { e: Experiment; r: Results }) {
  const primary = e.estimates.some((x) => x.reading_a !== null);
  return (
    <article className="panel frame" aria-labelledby={`h-${e.id}`}>
      <h3 id={`h-${e.id}`}>
        {e.id}: {e.title}
      </h3>
      <p>
        <span className="tag tag-measured">Measured</span> <span className="badge">{e.status}</span>
      </p>
      <p><strong>{e.status.startsWith("exploratory") ? "Verdict (exploratory, no frozen rule):" : "Verdict under the frozen rule:"}</strong> {e.verdict}</p>
      {e.estimates.length > 0 && (
        <div className="table-scroll" role="region" aria-label={`${e.id} estimates`} tabIndex={0}>
          <table>
            <caption className="sr-only">{e.id} estimates in milliseconds</caption>
            <thead>
              <tr>
                <th scope="col">Contrast</th>
                <th scope="col">Seeds</th>
                <th scope="col">Median (ms)</th>
                <th scope="col">95% CI (ms)</th>
                {primary && (
                  <>
                    <th scope="col">Holm p</th>
                    <th scope="col">Reading A</th>
                    <th scope="col">Reading B</th>
                    <th scope="col">TOST 90% CI (ms)</th>
                  </>
                )}
                {!primary && <th scope="col">Frozen verdict</th>}
              </tr>
            </thead>
            <tbody>
              {e.estimates.map((x) => (
                <tr key={x.label}>
                  <th scope="row">{x.label}</th>
                  <td>{x.seeds ?? ""}</td>
                  <td className="num">{fmtEstimate(x)}</td>
                  <td className="num">{fmtInterval(x)}</td>
                  {primary && (
                    <>
                      <td className="num">{x.holm_p_display}</td>
                      <td>{x.reading_a}</td>
                      <td>{x.reading_b}</td>
                      <td>{x.tost_display ?? ""}</td>
                    </>
                  )}
                  {!primary && <td>{x.group}</td>}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {e.estimates.length === 0 && (
        <p className="note">No contrast with an interval is reported for this experiment; its checks are listed below.</p>
      )}
      {e.notes.map((n, i) => (
        <p key={i} className="note">{n.replace(/`/g, "")}</p>
      ))}
      {e.id === "EXP-004" && <RobustnessTable r={r} />}
      <p className="meta">
        Report: <code>{e.report_path}</code>
        {e.claim_ids.length > 0 && <>. Claims: {e.claim_ids.join(", ")}</>}
      </p>
    </article>
  );
}

function RobustnessTable({ r }: { r: Results }) {
  return (
    <>
      <h4>Robustness of the 23 primary contrasts, both S1 readings (DEC-011, owner chose none)</h4>
      <div className="table-scroll" role="region" aria-label="EXP-004 robustness under both readings" tabIndex={0}>
        <table>
          <thead>
            <tr>
              <th scope="col">Primary contrast</th>
              <th scope="col">S1 = rAF1 and Element Timing (DEC-011)</th>
              <th scope="col">S1 = Element Timing only ("no sensitivity level" = not assessed)</th>
            </tr>
          </thead>
          <tbody>
            {r.robustness.map((x) => (
              <tr key={x.contrast}>
                <th scope="row">{x.contrast}</th>
                <td>{x.verdict_dec011}</td>
                <td>{x.verdict_narrow}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
