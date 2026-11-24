# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Report generator: tables, figures and a Markdown report built only from a validated result file.

PDF route (DEC-002): pandoc -> Typst with -V mainfont="Libertinus Serif", compiled with the typst
Python package of the labs toolchain.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from . import analysis
from .config import load_config
from .manifest import repo_root, utc_now
from .runner import flatten_trials, write_csv
from .schema import read_result

PANDOC = os.environ.get("SCROLL_PANDOC", "/Users/bechir/research/labs/.tools/pandoc")
TYPST_PY = os.environ.get("SCROLL_TYPST_PYTHON", "/Users/bechir/research/labs/.tools/py/bin/python")
PROJECTION_CONFIGS = ("EXP-002.json", "EXP-003.json", "EXP-004-S2.json", "EXP-004-S3.json", "EXP-004-S4.json")
ARM_COLORS = {"BLANK": "#555555", "SKELETON": "#1a5fb4", "PREFETCH": "#2e7d32", "OPTIMISTIC": "#b5651d"}


def _fmt(v: Any, nd: int = 1) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def md_table(rows: list[dict[str, Any]], cols: list[tuple[str, str]], nd: int = 1) -> str:
    head = "| " + " | ".join(h for _, h in cols) + " |\n|" + "---|" * len(cols) + "\n"
    body = "".join("| " + " | ".join(_fmt(r.get(k), nd) for k, _ in cols) + " |\n" for r in rows)
    return head + body


def figures(result: dict[str, Any], contrasts: list[dict[str, Any]], out: Path) -> list[dict[str, str]]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    out.mkdir(parents=True, exist_ok=True)
    made = []
    # Figure 1: TTUC per trial, per cell and arm.
    groups: dict[tuple, list[float]] = {}
    for s in result["sessions"]:
        for t in s["trials"]:
            m = t["metrics"]
            if s["status"] == "ok" and m["status"] == "ok":
                groups.setdefault((analysis.cell_label(analysis.cell_key(s["spec"])), s["spec"]["arm"]), []).append(m["ttuc_ms"])
    keys = sorted(groups)
    if keys:
        fig, ax = plt.subplots(figsize=(8, 0.42 * len(keys) + 1.2))
        rng = np.random.default_rng(0)
        for i, k in enumerate(keys):
            v = np.array(groups[k])
            ax.scatter(v, i + rng.uniform(-0.18, 0.18, v.size), s=10, alpha=0.7, color=ARM_COLORS.get(k[1], "k"))
            ax.plot([np.median(v)] * 2, [i - 0.3, i + 0.3], color="k", lw=1.5)
        ax.set_yticks(range(len(keys)), [f"{c}  {a}" for c, a in keys], fontsize=7)
        ax.set_xscale("log")
        ax.set_xlabel("TTUC, ms (log scale); dots = trials, bar = median")
        ax.set_title("EXPLORATORY: time to usable content per trial", fontsize=9)
        fig.tight_layout()
        for ext in ("svg", "png"):
            fig.savefig(out / f"fig-ttuc.{ext}", dpi=150)
        plt.close(fig)
        made.append({"id": "FIG-E1", "file": "fig-ttuc.svg",
                     "caption": "Time to usable content (TTUC, ms, log scale) for every analysed trial, by cell and arm. Vertical bars mark medians. Exploratory pre-freeze run; trials within a session are not independent.",
                     "alt": "Strip plot of TTUC per trial for each condition cell and arm, log-scaled horizontal axis in milliseconds."})
    # Figure 2: paired per-seed differences.
    if contrasts:
        fig, ax = plt.subplots(figsize=(8, 0.42 * len(contrasts) + 1.2))
        for i, c in enumerate(contrasts):
            ax.scatter(c["diffs_ms"], [i] * len(c["diffs_ms"]), s=14, color="#444")
            if c.get("ci95_low_ms") is not None:
                ax.plot([c["ci95_low_ms"], c["ci95_high_ms"]], [i, i], color="#1a5fb4", lw=3, alpha=0.5)
            ax.plot([c["median_diff_ms"]] * 2, [i - 0.3, i + 0.3], color="k", lw=1.5)
        ax.axvline(0, color="#999", lw=0.8)
        ax.set_yticks(range(len(contrasts)), [f"{c['cell']}  {c['contrast']}" for c in contrasts], fontsize=7)
        ax.set_xlabel("Per-seed difference in median TTUC, ms (dots = seeds; bar = median; band = 95% bootstrap over seeds)")
        ax.set_title("EXPLORATORY: paired seed-level contrasts against BLANK", fontsize=9)
        fig.tight_layout()
        for ext in ("svg", "png"):
            fig.savefig(out / f"fig-paired.{ext}", dpi=150)
        plt.close(fig)
        made.append({"id": "FIG-E2", "file": "fig-paired.svg",
                     "caption": "Per-seed paired differences in median TTUC (arm minus BLANK, ms), with the median and a 95% percentile bootstrap interval over seeds. Exploratory; few seeds give wide intervals.",
                     "alt": "Dot plot of per-seed TTUC differences against BLANK for each contrast with median bars and interval bands."})
    # Figure 3: excess over the reference lower bound.
    ex: dict[tuple, list[float]] = {}
    for s in result["sessions"]:
        for t in s["trials"]:
            m = t["metrics"]
            if s["status"] == "ok" and m["status"] == "ok":
                ex.setdefault((analysis.cell_label(analysis.cell_key(s["spec"])), s["spec"]["arm"]), []).append(m["ttuc_excess_ms"])
    if ex:
        keys = sorted(ex)
        fig, ax = plt.subplots(figsize=(8, 0.42 * len(keys) + 1.2))
        ax.boxplot([ex[k] for k in keys], orientation="horizontal", widths=0.5)
        ax.set_yticks(range(1, len(keys) + 1), [f"{c}  {a}" for c, a in keys], fontsize=7)
        ax.axvline(0, color="#a51d2d", lw=0.8)
        ax.set_xlabel("TTUC minus the reference-model lower bound, ms (instrumentation overhead; must be >= 0)")
        ax.set_title("EXPLORATORY: timing-chain overhead over the ideal model", fontsize=9)
        fig.tight_layout()
        for ext in ("svg", "png"):
            fig.savefig(out / f"fig-excess.{ext}", dpi=150)
        plt.close(fig)
        made.append({"id": "FIG-E3", "file": "fig-excess.svg",
                     "caption": "TTUC minus the reference-model lower bound (ms) per cell and arm; boxes show quartiles over trials. Negative values would indicate an instrumentation defect.",
                     "alt": "Horizontal box plots of timing overhead above the ideal model for each cell and arm."})
    return made


def build_report(run_dir: str | Path, pdf: bool = False, projection_dir: Path | None = None) -> Path:
    run_dir = Path(run_dir)
    result = read_result(run_dir / "results.json")  # fails closed on malformed input
    rdir = run_dir / "report"
    rdir.mkdir(exist_ok=True)
    cells = analysis.cell_summaries(result)
    contrasts = analysis.paired_contrasts(result)
    notes = analysis.degenerate_cases(result, contrasts, cells)
    model = analysis.runtime_model(result)
    projection_dir = projection_dir or (repo_root() / "experiments")
    projections = []
    for name in PROJECTION_CONFIGS:
        p = projection_dir / name
        if p.is_file():
            projections.append(analysis.project_runtime(model, load_config(p)))

    write_csv(flatten_trials(result), rdir / "metrics.csv")
    write_csv(cells, rdir / "cell_summary.csv")
    write_csv([{k: (";".join(map(str, v)) if isinstance(v, list) else v) for k, v in c.items()} for c in contrasts], rdir / "paired_contrasts.csv")
    write_csv(projections, rdir / "runtime_projection.csv")
    figs = figures(result, contrasts, rdir / "figures")

    man = result["manifest"]
    label = result["label"].upper()
    res_sha = hashlib.sha256((run_dir / "results.json").read_bytes()).hexdigest()
    lines = [
        "<!-- SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0 -->",
        f"# {label} run report: {man['run_id']}",
        "",
        f"**{label}. Pre-freeze run; not evidence for any research hypothesis. Never cite these numbers as findings.**" if result["label"] == "exploratory" else "",
        "",
        "Generated by `python -m scroll report` from `results.json` (SHA-256 `" + res_sha + "`). Every number below is computed from that file.",
        "",
        "## Run",
        "",
        md_table([{
            "experiment": man["experiment_id"], "config_hash": man["config_hash"][:16], "git": (man["git"]["revision"] or "n/a")[:10] + (" (dirty)" if man["git"]["dirty"] else ""),
            "browser": f"{man['browser'].get('channel')} {man['browser'].get('version')} headless={man['browser'].get('headless')} cpu={man['browser'].get('cpu_throttle')}x",
            "runtime_s": man["runtime_s"], "load_start": man.get("load_average_start"), "load_end": man.get("load_average_end"),
            "peak_rss_MiB": man["peak_rss_bytes"] / 2**20 if man.get("peak_rss_bytes") else None}],
            [("experiment", "Experiment"), ("config_hash", "Config hash (prefix)"), ("git", "Code revision"), ("browser", "Browser"),
             ("runtime_s", "Runtime (s)"), ("load_start", "Load avg start"), ("load_end", "Load avg end"), ("peak_rss_MiB", "Peak RSS Python (MiB)")]),
        "",
        f"Platform: {man['platform'].get('cpu')}, {man['platform'].get('ncpu')} logical CPUs, {man['platform'].get('os')} {man['platform'].get('mac_ver') or man['platform'].get('os_release')}. "
        "Other processes (including other agents) were running during the run, so wall-clock and timing values are noisy.",
        "",
        "## Cell summaries (trial level, descriptive)",
        "",
        md_table(cells, [("cell", "Cell"), ("arm", "Arm"), ("trials_ok", "Trials ok"), ("trials_excluded", "Excl."), ("seeds", "Seeds"),
                         ("ttuc_median_ms", "TTUC median (ms)"), ("ttuc_q1_ms", "Q1"), ("ttuc_q3_ms", "Q3"),
                         ("seed_median_sd_ms", "SD of seed medians"), ("ttff_median_ms", "TTFF median"),
                         ("excess_min_ms", "Excess min"), ("excess_median_ms", "Excess median")]),
        "",
        md_table(cells, [("cell", "Cell"), ("arm", "Arm"), ("element_minus_raf2_median_ms", "Element - rAF2 (ms)"),
                         ("event_below_threshold_share", "Event <16 ms share"), ("layout_shift_all_median", "Shift all (median)"),
                         ("layout_shift_cls_median", "Shift CLS-eligible (median)"), ("wrong_state_median_ms", "Wrong-state (ms)"),
                         ("false_state_median_ms", "False-state (ms)"), ("failures_injected", "Failures"),
                         ("final_correct_share", "Final correct"), ("prefetch_hit_share", "Prefetch hit"), ("defects", "Defects")], nd=3),
        "",
        "## Paired seed-level contrasts (descriptive; no hypothesis tests on exploratory data)",
        "",
        "Unit: the seed. Each seed contributes the median TTUC of its session; differences are arm minus BLANK for the same seed and cell. "
        "Intervals are 95% percentile bootstrap over seeds (10,000 resamples, seed 20261124). `n req.` is the protocol 5.1 formula with delta = 17 ms, alpha 0.05, power 0.80.",
        "",
        md_table(contrasts, [("cell", "Cell"), ("contrast", "Contrast"), ("pairs", "Pairs"), ("median_diff_ms", "Median diff (ms)"),
                             ("ci95_low_ms", "CI low"), ("ci95_high_ms", "CI high"), ("sigma_d_ms", "sigma_d (ms)"),
                             ("sigma_d_ci95_high_ms", "sigma_d CI high"), ("required_n", "n req."), ("required_n_at_sigma_upper", "n req. (CI high)"),
                             ("median_diff_raf1_ms", "Median diff, rAF1"), ("median_diff_element_ms", "Median diff, Element")]),
        "",
        "## Degenerate cases and warnings",
        "",
        *([f"- {n}" for n in notes] or ["- none detected"]),
        "",
        "## Runtime and projection",
        "",
        f"Fitted on this run: per-trial overhead median {model['trial_overhead_s']:.3f} s (90th percentile {model['trial_overhead_p90_s']:.3f} s) beyond delay + settle + pre-input + hover lead; "
        f"per-session overhead median {model['session_overhead_s']:.3f} s; median session wall {model['session_wall_median_s']:.2f} s; median trial wall {model['trial_wall_median_s']:.3f} s. "
        "Projections use the nominal latency as the delay and do not model CPU throttling or headed-mode cost.",
        "",
        md_table([{**p, "projected_min": p["projected_s"] / 60} for p in projections],
                 [("experiment_id", "Experiment"), ("description", "Config"), ("sessions", "Sessions"), ("interactions", "Interactions"),
                  ("projected_min", "Projected (min)")]),
        "",
        "## Figures",
        "",
    ]
    for f in figs:
        lines += [f"![{f['alt']}](figures/{f['file'].replace('.svg', '.png')})", "", f"**{f['id']}.** {f['caption']}", ""]
    lines += ["## Files", "", "- `../results.json` (validated against `src/scroll/schemas/result-1.0.0.json`)", "- `metrics.csv`, `cell_summary.csv`, `paired_contrasts.csv`, `runtime_projection.csv`", "- `figures/`", "",
              f"Report generated {utc_now()}."]
    md = "\n".join(lines) + "\n"
    (rdir / "report.md").write_text(md, encoding="utf-8")
    (rdir / "analysis.json").write_text(json.dumps({"cells": cells, "contrasts": contrasts, "notes": notes, "runtime_model": model,
                                                    "projections": projections, "results_sha256": res_sha}, indent=1, default=str) + "\n", encoding="utf-8")
    if pdf:
        build_pdf(rdir / "report.md", rdir / "report.pdf")
    return rdir / "report.md"


def build_pdf(md: Path, out_pdf: Path) -> Path:
    typ = out_pdf.with_suffix(".typ")
    subprocess.run([PANDOC, str(md), "-s", "-t", "typst", "-V", 'mainfont=Libertinus Serif', "--resource-path", str(md.parent), "-o", str(typ)], check=True, cwd=md.parent)
    subprocess.run([TYPST_PY, "-c", "import typst,sys; typst.compile(sys.argv[1], output=sys.argv[2], root=sys.argv[3])", str(typ), str(out_pdf), str(md.parent)], check=True, cwd=md.parent)
    return out_pdf
