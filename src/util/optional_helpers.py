#!/usr/bin/env python3
"""None-safe helpers."""

from typing import Mapping, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


def optional_avg(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None:
        return b
    if b is None:
        return a
    if a == b:
        return a
    return (a + b) / 2.0


def optional_round(value: Optional[float]) -> Optional[int]:
    if value is None:
        return None
    return round(value)


def optional_scale_int(
    value: Optional[int],
    scale: int,
    offset: int = 0,
) -> Optional[int]:
    if value is None:
        return None
    return value * scale + offset


def optional_div(value: Optional[float], divisor: float) -> Optional[float]:
    if value is None or divisor == 0:
        return None
    return value / divisor


def optional_map_get(
    mapping: Mapping[K, V],
    key: Optional[K],
) -> Optional[V]:
    if key is None:
        return None
    return mapping.get(key)
