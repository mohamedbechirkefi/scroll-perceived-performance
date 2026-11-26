// SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
// Hero illustration: a split-timer stopwatch and a film strip that advances frame by frame.
// It is a drawing of the idea, not data: it shows no number and plays once (CSS animations,
// final state by default, so reduced motion shows the still picture).

const FRAMES = ["empty", "empty", "skel", "skel", "skel", "usable", "usable"] as const;
const CX = 240;
const CY = 128;
const R = 92;

export function HeroIllustration() {
  const ticks = Array.from({ length: 60 }, (_, i) => i);
  const fw = 56;
  const gap = 8;
  const x0 = (480 - (FRAMES.length * fw + (FRAMES.length - 1) * gap)) / 2;
  const holes = Array.from({ length: 30 }, (_, i) => 8 + i * 16);
  return (
    <figure className="hero-plate" aria-labelledby="hero-cap">
      <svg viewBox="0 0 480 372" role="img" aria-label="Illustration: a stopwatch is started by a click; its split hand stops when the first feedback frame appears and its sweep hand stops on the first usable frame of the film strip below.">
        <g className="hx-watch">
          <rect className="hx-crown" x={CX - 16} y={CY - R - 30} width={32} height={14} />
          <rect className="hx-ink" x={CX - 6} y={CY - R - 18} width={12} height={14} />
          <circle className="hx-ring" cx={CX} cy={CY} r={R} />
          {ticks.map((i) => {
            const a = (i * 6 * Math.PI) / 180;
            const long = i % 5 === 0;
            const r0 = R - (long ? 16 : 9);
            return (
              <line key={i} className={long ? "hx-tick major" : "hx-tick"}
                x1={CX + r0 * Math.sin(a)} y1={CY - r0 * Math.cos(a)}
                x2={CX + (R - 5) * Math.sin(a)} y2={CY - (R - 5) * Math.cos(a)} />
            );
          })}
          <line className="hx-hand hx-split" x1={CX} y1={CY + 12} x2={CX} y2={CY - R + 20} />
          <line className="hx-hand hx-sweep" x1={CX} y1={CY + 16} x2={CX} y2={CY - R + 12} />
          <circle className="hx-hub" cx={CX} cy={CY} r={6} />
        </g>
        <g className="hx-strip">
          <rect className="hx-film" x={0} y={270} width={480} height={84} />
          {holes.map((x) => (
            <g key={x}>
              <rect className="hx-hole" x={x} y={276} width={8} height={7} rx={1.5} />
              <rect className="hx-hole" x={x} y={341} width={8} height={7} rx={1.5} />
            </g>
          ))}
          {FRAMES.map((kind, i) => {
            const x = x0 + i * (fw + gap);
            return (
              <g key={i} className={`hx-frame hx-${kind}`} style={{ animationDelay: `${200 + i * 280}ms` }}>
                <rect className="hx-cell" x={x} y={290} width={fw} height={44} />
                {kind === "skel" && (
                  <>
                    <rect className="hx-bar" x={x + 7} y={298} width={30} height={6} />
                    <rect className="hx-bar" x={x + 7} y={309} width={42} height={6} />
                    <rect className="hx-bar" x={x + 7} y={320} width={22} height={6} />
                  </>
                )}
                {kind === "usable" && (
                  <>
                    <rect className="hx-line strong" x={x + 7} y={298} width={30} height={6} />
                    <rect className="hx-line" x={x + 7} y={309} width={42} height={4} />
                    <rect className="hx-line" x={x + 7} y={317} width={36} height={4} />
                    <rect className="hx-line" x={x + 7} y={325} width={26} height={4} />
                  </>
                )}
              </g>
            );
          })}
          <rect className="hx-mark split" x={x0 + 2 * (fw + gap) - 3} y={262} width={3} height={100} />
          <rect className="hx-mark sweep" x={x0 + 5 * (fw + gap) - 3} y={262} width={3} height={100} />
        </g>
      </svg>
      <figcaption id="hero-cap">
        <span className="tag tag-illustrative">Illustration, not study data</span>
        <span className="hero-legend">
          <span className="leg"><span className="key key-split" aria-hidden="true" /> split hand: first feedback</span>
          <span className="leg"><span className="key key-sweep" aria-hidden="true" /> sweep hand: usable content</span>
        </span>
      </figcaption>
    </figure>
  );
}
