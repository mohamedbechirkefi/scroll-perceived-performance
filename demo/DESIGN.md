<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->
# SCROLL demo: design plan

Owner request of 2026-11-26: each lab demo gets its own brand, motion and premium UI. This file is the plan written before the code, then reviewed against the frontend-design tells and the other demos' directions.

## Subject, audience, job

- **Subject.** What a page shows between a click and the moment its content is usable: nothing, a skeleton, a prefetched result, or an optimistic guess. The study timed this frame by frame in one browser.
- **Audience.** A curious technical reader (front-end engineers), an admissions committee skimming for rigour, a researcher checking the method.
- **Primary job.** Answer in one sentence whether loading strategies deliver usable content sooner or only feedback, then show the measured traces as the study's own picture: a click, frames passing, the first usable frame.

## Direction: the stopwatch and the film strip

A timing lab, not a dashboard. Every measured trace is drawn as a strip of film: unexposed (nothing new), placeholder frames (feedback that is not yet usable), and developed frames once the content is usable. A stopwatch carries two hands, as a real split-timer does: the split hand marks first feedback (TTFF), the sweep hand marks usable content (TTUC). The page is silver photographic paper with dark film base; the only warm colour is the sweep hand.

## Colours

| Name | Hex | Role |
|---|---|---|
| Silver paper | `#EDF0EE` | page background, cool grey-white (not cream) |
| Emulsion | `#1D2A30` | text, logo ink |
| Film base | `#25333B` | film strips, hero plate, footer |
| Developed | `#F6F8F7` | usable frames on the strip, text on film base |
| Sweep red | `#C9301F` (text `#A82615`) | the TTUC hand, primary action, the logo's final frame |
| Split amber | `#E2A33A` (text `#80550A`) | the TTFF hand, the placeholder state |

## Type

- **Big Shoulders Display** (variable, OFL 1.1): headlines, the wordmark, the stopwatch readout in the replay. A condensed, signage-like face from Chicago street lettering; condensed numerals sit like a timer display.
- **Libre Franklin** (variable, OFL 1.1): body, tables, controls, chart labels; tabular figures for every number.

Scale (Elements of Typographic Style, base 17 px): 13, 15, 17, 21, 28, 40, 64 px. Body line length capped at 68 characters.

## Layout

Left-aligned throughout, one column of prose (max 42 rem) with wide figures breaking out to 72 rem.

```
+----------------------------------------------------------------+
| [mark] SCROLL   Traces  Overview  Results  Method  Sandbox      |  sticky, 56 px, paper with hairline
+----------------------------------------------------------------+
| Question (Big Shoulders, 40 to 64 px)       +----------------+ |
| Answer in one sentence                       |  stopwatch     | |
| author line, status chip                     |  + film strip  | |
|                                              | Illustration,  | |
|                                              | not study data | |
|                                              +----------------+ |
+----------------------------------------------------------------+
| TRACES: scenario control (sliding frame), latency slider        |
| [BLANK    |unexposed|placeholder|developed frames...  ]         |
| [SKELETON |...                                       ]         |  film strips, split and sweep hands
| [PREFETCH |...                                       ]         |
| values table, published contrasts                              |
+----------------------------------------------------------------+
| Overview: reading key, status, DEC-011 both readings            |
| Results: EXP-001..004 panels, tables                            |
| Assumptions | Method and limitations                            |
| SANDBOX workbench: controls, Run, lower bounds,                 |
|   replay: four viewfinders + stopwatch readout                  |
+----------------------------------------------------------------+
| footer on film base: links, licence, AI use, font credits       |
+----------------------------------------------------------------+
```

## Motion

- **One orchestrated hero moment (about 2.4 s, once).** The stopwatch is pressed (crown dips), the split hand stops early on an amber frame while the film strip advances and its frames turn from unexposed to shimmering placeholders to developed; the sweep hand stops on the first developed frame. It is labelled "Illustration, not study data" and shows no number.
- **Answering actions.** The scenario control's frame indicator slides between options (transform only, 220 ms, strong ease-out). The trace strips wipe in from the left once when first scrolled into view (clip-path, 600 ms, 60 ms stagger). The Run button presses (scale 0.97, 120 ms); new sandbox rows appear with a 40 ms stagger. The replay's placeholders shimmer only while a replay shows them.
- **Not animated.** The latency slider and the scenario switch redraw the chart instantly: they are used tens of times and the data must not move for style.
- **Reduced motion.** The hero renders its final state; the wipe, stagger and shimmer are removed; indicators change without movement.
- Hover effects only inside `(hover: hover) and (pointer: fine)`; no `transition: all`.

## The one memorable thing

The measured traces drawn as film strips with a split hand and a sweep hand: the visitor sees "feedback" and "usable" as two different marks on the same strip, which is the study's whole point.

## Review against the tells and the other demos

- *Cream plus terracotta:* the paper is cool grey (`#EDF0EE`), the accent is a stopwatch red used only for the sweep hand and the primary action. Kept, with that restriction.
- *Near-black with one acid accent:* the dark film base appears only in strips, the hero plate and the footer, and it carries two hands (amber and red), not one acid accent. Kept.
- *All-caps tracked eyebrows, mono data labels:* removed the old uppercase kicker; labels are sentence case in Libre Franklin; no monospace anywhere except file paths in `code`.
- *01/02/03 markers:* none. The limitations list stays an ordered list because the manuscript numbers them.
- *Identical rounded SaaS cards:* experiment panels became frames of a contact sheet (square corners, a film-edge rule on the left), the sandbox a workbench with a dashed register mark border; different shapes for different jobs.
- *Fade-up on every section:* removed from the first draft, which faded every section in; only the trace strips reveal, because they are the result.
- *Other demos:* PULSE is a broadcast control room (channel strips, colour bars), FARE a split-flap board, TOKEN a die shot and thermal glow. SCROLL avoids colour bars and flipping digits: its vocabulary is film frames, sprocket holes and a two-hand stopwatch, on light paper rather than a dark control room.
- First draft changes: a dark "projection room" page was dropped (it read as the near-black tell and competed with TOKEN and PULSE); a counting timer in the hero was dropped (it would show a number that looks like a result).
