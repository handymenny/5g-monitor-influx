#!/usr/bin/env python3
"""Parser for +QENG servingcell responses."""

from typing import List

from model.mappings import (
    LTE_BW_INDEX_TO_MHZ,
    NR_BW_INDEX_TO_MHZ,
    NR_SCS_INDEX_TO_KHZ,
    Rat,
)
from model.models import ServingCellQENG
from util.optional_helpers import optional_div, optional_map_get, optional_scale_int
from .common import parse_int, parse_response


def parse_qeng_servingcell(response: str) -> List[ServingCellQENG]:
    cells: List[ServingCellQENG] = []

    for values in parse_response(response, "+QENG"):
        if len(values) < 3:
            continue

        if values[0] == "LTE" or values[2] == "LTE":
            if values[2] == "LTE":
                values = values[2:]

            try:
                # LTE SINR conversion: Y = 2 * X - 20
                raw_sinr = parse_int(values[14])
                corrected_sinr_value = optional_scale_int(raw_sinr, 2, -20)

                lte_cell = ServingCellQENG(
                    rat=Rat.LTE,
                    duplex=values[1],
                    mcc=parse_int(values[2]),
                    mnc=parse_int(values[3]),
                    cell_id=parse_int(values[4], hex=True),
                    pci=parse_int(values[5]),
                    arfcn=parse_int(values[6]),
                    band=parse_int(values[7]),
                    ul_bandwidth=optional_map_get(
                        LTE_BW_INDEX_TO_MHZ, parse_int(values[8])
                    ),
                    dl_bandwidth=optional_map_get(
                        LTE_BW_INDEX_TO_MHZ, parse_int(values[9])
                    ),
                    tac=parse_int(values[10], hex=True),
                    rsrp=parse_int(values[11]),
                    rsrq=parse_int(values[12]),
                    rssi=parse_int(values[13]),
                    sinr=corrected_sinr_value,
                    cqi=parse_int(values[15]),
                    tx_power=optional_div(parse_int(values[16]), 10),
                )
                cells.append(lte_cell)
            except (ValueError, IndexError):
                pass

        elif values[0] == "NR5G-NSA":
            try:
                nsa_cell = ServingCellQENG(
                    rat=Rat.NR_NSA,
                    mcc=parse_int(values[1]),
                    mnc=parse_int(values[2]),
                    pci=parse_int(values[3]),
                    rsrp=parse_int(values[4]),
                    sinr=parse_int(values[5]),
                    rsrq=parse_int(values[6]),
                    arfcn=parse_int(values[7]),
                    band=parse_int(values[8]),
                    dl_bandwidth=optional_map_get(
                        NR_BW_INDEX_TO_MHZ, parse_int(values[9])
                    ),
                    scs=optional_map_get(NR_SCS_INDEX_TO_KHZ, parse_int(values[10])),
                )
                cells.append(nsa_cell)
            except (ValueError, IndexError):
                pass

        elif len(values) > 3 and values[3] == "NR5G-SA":
            try:
                sa_cell = ServingCellQENG(
                    rat=Rat.NR_SA,
                    duplex=values[4],
                    mcc=parse_int(values[5]),
                    mnc=parse_int(values[6]),
                    cell_id=parse_int(values[7], hex=True),
                    pci=parse_int(values[8]),
                    tac=parse_int(values[9], hex=True),
                    arfcn=parse_int(values[10]),
                    band=parse_int(values[11]),
                    dl_bandwidth=optional_map_get(
                        NR_BW_INDEX_TO_MHZ, parse_int(values[12])
                    ),
                    rsrp=parse_int(values[13]),
                    rsrq=parse_int(values[14]),
                    sinr=parse_int(values[15]),
                    scs=optional_map_get(NR_SCS_INDEX_TO_KHZ, parse_int(values[16])),
                )
                cells.append(sa_cell)
            except (ValueError, IndexError):
                pass

    return cells
