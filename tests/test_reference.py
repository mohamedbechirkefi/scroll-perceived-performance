# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
import pytest

from scroll.reference import expected, residual_wait_ms


def test_reference_read():
    assert expected("read", "BLANK", 300).ttuc_lower_bound_ms == 300
    assert expected("read", "SKELETON", 300).ttff_lower_bound_ms == 0
    assert expected("read", "SKELETON", 300).ttuc_lower_bound_ms == 300
    assert expected("read", "PREFETCH", 300, lead_ms=150).ttuc_lower_bound_ms == 150
    assert expected("read", "PREFETCH", 100, lead_ms=150).ttuc_lower_bound_ms == 0


def test_reference_write():
    e = expected("write", "OPTIMISTIC", 300, ok=True)
    assert (e.ttuc_lower_bound_ms, e.final_pressed, e.error_shown) == (0, True, False)
    e = expected("write", "OPTIMISTIC", 300, ok=False)
    assert (e.ttuc_lower_bound_ms, e.final_pressed, e.error_shown) == (300, False, True)
    e = expected("write", "BLANK", 300, ok=True, before=True)
    assert (e.ttuc_lower_bound_ms, e.final_pressed) == (300, False)


@pytest.mark.parametrize("args,kw", [(("read", "OPTIMISTIC", 1), {}), (("write", "SKELETON", 1), {}), (("x", "BLANK", 1), {}),
                                     (("read", "BLANK", -1), {}), (("read", "BLANK", 1), {"ok": False})])
def test_reference_invalid(args, kw):
    with pytest.raises(ValueError):
        expected(*args, **kw)


def test_residual_wait():
    assert residual_wait_ms(100, 40) == 60 and residual_wait_ms(100, 400) == 0
    with pytest.raises(ValueError):
        residual_wait_ms(-1, 0)
