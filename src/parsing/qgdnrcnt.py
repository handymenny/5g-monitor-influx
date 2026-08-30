#!/usr/bin/env python3
"""Parser for +QGDNRCNT responses."""

from model.models import PacketDataCounter
from .common import parse_int, parse_response


def parse_qgdnrcnt(response: str) -> PacketDataCounter | None:
    # Example response:
    # +QGDNRCNT: 231743605,4951875263
    #
    # Fields: tx_bytes,rx_bytes

    for values in parse_response(response, "+QGDNRCNT"):
        if len(values) < 2:
            continue

        try:
            tx_bytes: int = parse_int(values[0], 0)  # type: ignore always an int
            rx_bytes: int = parse_int(values[1], 0)  # type: ignore always an int

            return PacketDataCounter(
                tx_bytes=tx_bytes,
                rx_bytes=rx_bytes,
            )
        except (ValueError, IndexError):
            pass

    return None
