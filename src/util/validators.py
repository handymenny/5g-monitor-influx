#!/usr/bin/env python3
"""Validation helpers."""

from typing import Optional


def check_range(
    value: Optional[float],
    min_val: float,
    max_val: float,
) -> Optional[float]:
    """Return *None* when *value* is outside [min_val, max_val]."""
    if value is None:
        return None
    if min_val <= value <= max_val:
        return value
    return None
