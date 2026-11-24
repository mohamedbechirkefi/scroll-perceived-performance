# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
import math

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from scroll import stats


def test_required_n_hand_computed():
    # ((1.959964 + 0.841621) * 20 / 17)^2 = 10.86 -> 11 (protocol 5.1 "about 11").
    assert stats.required_n(20) == 11
    # sigma_d = 28: (2.801585 * 28 / 17)^2 = 21.29 -> 22.
    assert stats.required_n(28) == 22
    assert stats.required_n(0) == 1


def test_holm_hand_computed():
    # sorted: 0.01*3 = 0.03; 0.03*2 = 0.06; 0.04*1 = 0.04 -> running max 0.06.
    assert stats.holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert stats.holm([0.5, 0.9]) == pytest.approx([1.0, 1.0])


def test_paired_differences_matches_seeds_only():
    d = stats.paired_differences({1: 10.0, 2: 20.0, 3: 5.0}, {2: 15.0, 3: 5.0, 4: 1.0})
    assert d == {2: 5.0, 3: 0.0}
    with pytest.raises(stats.StatsError):
        stats.paired_differences({1: 1.0}, {2: 1.0})


def test_bootstrap_constant_and_deterministic():
    assert stats.bootstrap_ci([3.0] * 6) == (3.0, 3.0)
    a = [1.0, 4.0, 2.0, 8.0, 5.0]
    assert stats.bootstrap_ci(a) == stats.bootstrap_ci(a)
    lo, hi = stats.bootstrap_ci(a)
    assert lo <= np.median(a) <= hi


def test_sd_and_iqr_hand_computed():
    assert stats.sd([1.0, 3.0]) == pytest.approx(math.sqrt(2))
    assert stats.iqr([1.0, 2.0, 3.0, 4.0, 5.0]) == (2.0, 4.0)


def test_tost():
    assert stats.tost_bootstrap([1.0, -2.0, 0.5, 1.5, -1.0], margin=17)["equivalent"] is True
    assert stats.tost_bootstrap([30.0, 40.0, 25.0, 35.0, 50.0], margin=17)["equivalent"] is False


def test_wilcoxon():
    assert stats.wilcoxon_p([0.0, 0.0, 0.0]) == 1.0
    assert stats.wilcoxon_p([5.0, 6.0, 7.0, 8.0, 9.0, 10.0]) < 0.05


@pytest.mark.parametrize("fn,args", [
    (stats.median, ([],)), (stats.iqr, ([],)), (stats.sd, ([1.0],)), (stats.bootstrap_ci, ([1.0],)),
    (stats.bootstrap_ci, ([1.0, float("nan")],)), (stats.required_n, (-1,)), (stats.required_n, (float("inf"),)),
    (stats.holm, ([1.5],)), (stats.tost_bootstrap, ([1.0, 2.0], 0)), (stats.wilcoxon_p, ([1.0],)),
])
def test_invalid_inputs(fn, args):
    with pytest.raises(stats.StatsError):
        fn(*args)


@settings(max_examples=100, deadline=None)
@given(st.lists(st.floats(0, 1), min_size=1, max_size=12))
def test_holm_invariants(p):
    adj = stats.holm(p)
    assert all(a >= b - 1e-12 and a <= 1 for a, b in zip(adj, p))
    order = np.argsort(p, kind="stable")
    assert all(adj[order[i]] <= adj[order[i + 1]] + 1e-12 for i in range(len(p) - 1))


@settings(max_examples=50, deadline=None)
@given(st.lists(st.floats(-500, 500), min_size=2, max_size=20))
def test_bootstrap_interval_inside_range(v):
    lo, hi = stats.bootstrap_ci(v, n_resamples=500)
    assert min(v) - 1e-9 <= lo <= hi <= max(v) + 1e-9
