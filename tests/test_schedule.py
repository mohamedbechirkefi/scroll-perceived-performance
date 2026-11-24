# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Unit, golden and property tests for the seeded schedule."""
import math

import pytest
from hypothesis import given, settings, strategies as st

from scroll import schedule as S

def test_fmix32_hand_computed():
    # fmix32(0) = 0: every step of the finaliser maps 0 to 0.
    assert S.fmix32(0) == 0
    # fmix32 is a bijection on 32-bit words; masking keeps results in range.
    assert 0 <= S.fmix32(0xFFFFFFFF) <= 0xFFFFFFFF


def test_delay_without_jitter_is_rounded_latency():
    # Hand-computed: jitter 0 => floor(L + 0.5).
    assert S.delay_ms(1, "read", 0, 100, 0.0) == 100
    assert S.delay_ms(1, "read", 0, 99.5, 0.0) == 100
    assert S.delay_ms(1, "read", 0, 99.49, 0.0) == 99
    assert S.delay_ms(1, "read", 0, 0, 0.0) == 0


def test_delay_formula_matches_uniform():
    u = S.uniform(7, S.STREAMS["write"], 3, S.FIELD_DELAY)
    assert S.delay_ms(7, "write", 3, 300, 0.1) == math.floor(300 * (1 + 0.1 * (2 * u - 1)) + 0.5)


def test_outcome_extremes():
    assert all(S.succeeds(s, "write", i, 0.0) for s in range(20) for i in range(20))
    assert not any(S.succeeds(s, "write", i, 1.0) for s in range(20) for i in range(20))


@pytest.mark.parametrize("args", [(-1, "read", 0, 100, 0.1), (2**32, "read", 0, 100, 0.1), (1.5, "read", 0, 100, 0.1),
                                  (True, "read", 0, 100, 0.1), (1, "nope", 0, 100, 0.1), (1, "read", -1, 100, 0.1),
                                  (1, "read", 0, -1, 0.1), (1, "read", 0, float("nan"), 0.1), (1, "read", 0, float("inf"), 0.1),
                                  (1, "read", 0, 100, 1.0), (1, "read", 0, 100, -0.1)])
def test_delay_invalid_inputs(args):
    with pytest.raises(ValueError):
        S.delay_ms(*args)


@pytest.mark.parametrize("p", [-0.01, 1.01, float("nan"), True])
def test_succeeds_invalid_probability(p):
    with pytest.raises(ValueError):
        S.succeeds(1, "write", 0, p)


@settings(max_examples=300, deadline=None)
@given(seed=st.integers(0, 2**32 - 1), idx=st.integers(0, 10_000), L=st.floats(0, 60_000), j=st.floats(0, 0.99))
def test_delay_within_jitter_bounds(seed, idx, L, j):
    d = S.delay_ms(seed, "read", idx, L, j)
    assert math.floor(L * (1 - j) + 0.5) <= d <= math.floor(L * (1 + j) + 0.5)
    assert d == S.delay_ms(seed, "read", idx, L, j)  # deterministic


@settings(max_examples=200, deadline=None)
@given(seed=st.integers(0, 2**32 - 1), idx=st.integers(0, 10_000), p1=st.floats(0, 1), p2=st.floats(0, 1))
def test_failure_monotone_in_p(seed, idx, p1, p2):
    lo, hi = sorted((p1, p2))
    # If a request fails at the lower probability, it also fails at the higher one (common random numbers).
    if not S.succeeds(seed, "write", idx, lo):
        assert not S.succeeds(seed, "write", idx, hi)


def test_uniformity_and_failure_rate():
    us = [S.uniform(s, 1, i, 0) for s in range(100) for i in range(100)]
    assert abs(sum(us) / len(us) - 0.5) < 0.01
    assert min(us) >= 0 and max(us) < 1
    fails = sum(not S.succeeds(s, "write", i, 0.3) for s in range(100) for i in range(100))
    assert abs(fails / 10_000 - 0.3) < 0.02


def test_streams_are_independent_of_each_other():
    a = [S.delay_ms(5, "read", i, 1000, 0.1) for i in range(50)]
    b = [S.delay_ms(5, "decoy", i, 1000, 0.1) for i in range(50)]
    assert a != b


def test_common_random_numbers_across_arms():
    # The schedule has no arm input: every arm sees the same delay and outcome for (seed, stream, index).
    sig = S.schedule.__code__.co_varnames[: S.schedule.__code__.co_argcount]
    assert "arm" not in sig


# Regression fixture: values produced by this implementation at M2 (2026-11-24), not hand-computed.
# A change here changes every schedule and therefore every experiment; it must be a recorded decision.
REGRESSION = [
    ((1001, "read", 0), 2808980183, 309, False),
    ((1001, "write", 4), 3469531250, 318, False),
    ((1, "decoy", 9), 3909823985, 325, True),
    ((4294967295, "write", 0), 706783870, 280, True),
]


@pytest.mark.parametrize("key,h,d300,ok03", REGRESSION)
def test_regression_fixture(key, h, d300, ok03):
    seed, stream, idx = key
    assert S.hash32(seed, S.STREAMS[stream], idx, S.FIELD_DELAY) == h
    assert S.delay_ms(seed, stream, idx, 300, 0.1) == d300
    assert S.succeeds(seed, stream, idx, 0.3) is ok03
