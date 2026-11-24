# SPDX-License-Identifier: LicenseRef-SCROLL-NC-Research-1.0
"""Seeded latency and failure schedule (DEC-004, proposed).

Pure functions. Twin of ``src/web/schedule.js``: both must give identical
results for identical inputs (checked by a differential test through Node).
Units: milliseconds for latency and delay; probabilities in [0, 1].
"""
from __future__ import annotations

import math
from dataclasses import dataclass

STREAMS = {"read": 0, "write": 1, "decoy": 2}
FIELD_DELAY = 0
FIELD_OUTCOME = 1
_MASK = 0xFFFFFFFF
_TWO_32 = 4294967296


def _imul(a: int, b: int) -> int:
    return (a * b) & _MASK


def fmix32(h: int) -> int:
    """MurmurHash3 32-bit finaliser."""
    h &= _MASK
    h ^= h >> 16
    h = _imul(h, 0x85EBCA6B)
    h ^= h >> 13
    h = _imul(h, 0xC2B2AE35)
    h ^= h >> 16
    return h & _MASK


def _is_uint32(x: object) -> bool:
    return isinstance(x, int) and not isinstance(x, bool) and 0 <= x < _TWO_32


def hash32(seed: int, stream: int, index: int, field: int) -> int:
    if not _is_uint32(seed):
        raise ValueError("seed must be an integer in [0, 2^32)")
    if not _is_uint32(stream):
        raise ValueError("stream must be an integer in [0, 2^32)")
    if not _is_uint32(index) or index >= _TWO_32 - 1:
        raise ValueError("index must be an integer in [0, 2^32 - 1)")
    if not _is_uint32(field):
        raise ValueError("field must be an integer in [0, 2^32)")
    h = fmix32(seed)
    h = fmix32(h ^ _imul(stream + 1, 0x9E3779B1))
    h = fmix32(h ^ _imul(index + 1, 0x85EBCA77))
    h = fmix32(h ^ _imul(field + 1, 0xC2B2AE3D))
    return h


def uniform(seed: int, stream: int, index: int, field: int) -> float:
    """Uniform variate in [0, 1)."""
    return hash32(seed, stream, index, field) / _TWO_32


def stream_id(name: str) -> int:
    if name not in STREAMS:
        raise ValueError(f"unknown stream: {name!r}")
    return STREAMS[name]


def delay_ms(seed: int, stream: str, index: int, latency_ms: float, jitter: float) -> int:
    """Injected delay in integer ms: floor(L * (1 + jitter * (2u - 1)) + 0.5)."""
    if isinstance(latency_ms, bool) or not isinstance(latency_ms, (int, float)) or not math.isfinite(latency_ms) or latency_ms < 0:
        raise ValueError("latency_ms must be a finite number >= 0")
    if isinstance(jitter, bool) or not isinstance(jitter, (int, float)) or not (0 <= jitter < 1):
        raise ValueError("jitter must be in [0, 1)")
    u = uniform(seed, stream_id(stream), index, FIELD_DELAY)
    return math.floor(latency_ms * (1 + jitter * (2 * u - 1)) + 0.5)


def succeeds(seed: int, stream: str, index: int, failure_prob: float) -> bool:
    """True when the request succeeds; failure iff u < p."""
    if isinstance(failure_prob, bool) or not isinstance(failure_prob, (int, float)) or not (0 <= failure_prob <= 1):
        raise ValueError("failure_prob must be in [0, 1]")
    u = uniform(seed, stream_id(stream), index, FIELD_OUTCOME)
    return not (u < failure_prob)


@dataclass(frozen=True)
class Scheduled:
    delay_ms: int
    ok: bool


def schedule(seed: int, stream: str, index: int, latency_ms: float, jitter: float, failure_prob: float) -> Scheduled:
    return Scheduled(delay_ms(seed, stream, index, latency_ms, jitter), succeeds(seed, stream, index, failure_prob))
