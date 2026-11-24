# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Statistics at the seed level (research/protocol.md, sections 5 and 6).

The independent unit is the seed: interactions within a session are summarised
by their median before any inference. Pure functions on plain sequences.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Sequence

import numpy as np
from scipy import stats as sps


class StatsError(ValueError):
    pass


def _finite_array(values: Sequence[float], name: str = "values") -> np.ndarray:
    a = np.asarray(list(values), dtype=float)
    if a.ndim != 1:
        raise StatsError(f"{name} must be one-dimensional")
    if not np.all(np.isfinite(a)):
        raise StatsError(f"{name} contains non-finite values")
    return a


def median(values: Sequence[float]) -> float:
    a = _finite_array(values)
    if a.size == 0:
        raise StatsError("median of an empty sequence")
    return float(np.median(a))


def iqr(values: Sequence[float]) -> tuple[float, float]:
    a = _finite_array(values)
    if a.size == 0:
        raise StatsError("IQR of an empty sequence")
    q1, q3 = np.percentile(a, [25, 75])
    return float(q1), float(q3)


def paired_differences(treated: dict[int, float], baseline: dict[int, float]) -> dict[int, float]:
    """Per-seed differences treated - baseline over seeds present in both (matched pairs only)."""
    common = sorted(set(treated) & set(baseline))
    if not common:
        raise StatsError("no common seeds")
    return {s: float(treated[s]) - float(baseline[s]) for s in common}


def bootstrap_ci(values: Sequence[float], stat: Callable[[np.ndarray], float] = np.median, n_resamples: int = 10_000,
                 level: float = 0.95, seed: int = 20261124) -> tuple[float, float]:
    """Percentile bootstrap interval of `stat` over the independent units in `values`."""
    a = _finite_array(values)
    if a.size < 2:
        raise StatsError("bootstrap needs at least two independent units")
    if not (0 < level < 1):
        raise StatsError("level must be in (0, 1)")
    if n_resamples < 100:
        raise StatsError("n_resamples must be >= 100")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, a.size, size=(n_resamples, a.size))
    boot = np.apply_along_axis(stat, 1, a[idx])
    lo, hi = np.percentile(boot, [100 * (1 - level) / 2, 100 * (1 + level) / 2])
    return float(lo), float(hi)


def sd(values: Sequence[float]) -> float:
    a = _finite_array(values)
    if a.size < 2:
        raise StatsError("standard deviation needs at least two values")
    return float(np.std(a, ddof=1))


def required_n(sigma_d: float, delta: float = 17.0, alpha: float = 0.05, power: float = 0.80) -> int:
    """n = ceil(((z_{1-alpha/2} + z_{power}) * sigma_d / delta)^2), protocol section 5.1."""
    if not (sigma_d >= 0 and math.isfinite(sigma_d)):
        raise StatsError("sigma_d must be finite and >= 0")
    if not delta > 0:
        raise StatsError("delta must be > 0")
    if not (0 < alpha < 1 and 0 < power < 1):
        raise StatsError("alpha and power must be in (0, 1)")
    z = sps.norm.ppf(1 - alpha / 2) + sps.norm.ppf(power)
    return max(1, math.ceil((z * sigma_d / delta) ** 2))


def holm(pvalues: Sequence[float]) -> list[float]:
    """Holm step-down adjusted p-values, in input order."""
    p = _finite_array(pvalues, "pvalues")
    if np.any((p < 0) | (p > 1)):
        raise StatsError("p-values must be in [0, 1]")
    m = p.size
    order = np.argsort(p, kind="stable")
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p[i]))
        adj[i] = running
    return [float(x) for x in adj]


def tost_bootstrap(diffs: Sequence[float], margin: float, seed: int = 20261124, n_resamples: int = 10_000) -> dict[str, float | bool]:
    """Equivalence by the 90% percentile bootstrap interval of the median difference (protocol 6)."""
    if not margin > 0:
        raise StatsError("margin must be > 0")
    lo, hi = bootstrap_ci(diffs, level=0.90, seed=seed, n_resamples=n_resamples)
    return {"ci90_low": lo, "ci90_high": hi, "equivalent": bool(-margin < lo and hi < margin)}


def wilcoxon_p(diffs: Sequence[float]) -> float:
    """Two-sided Wilcoxon signed-rank p-value (secondary check, protocol 6)."""
    a = _finite_array(diffs, "diffs")
    if a.size < 2:
        raise StatsError("Wilcoxon needs at least two pairs")
    if np.all(a == 0):
        return 1.0
    return float(sps.wilcoxon(a, zero_method="wilcox", alternative="two-sided").pvalue)
