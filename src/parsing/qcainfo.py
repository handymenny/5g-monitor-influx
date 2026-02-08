#!/usr/bin/env python3
"""Parser for +QCAINFO responses."""

from typing import List, Optional

from model.mappings import (
    LTE_RB_INDEX_TO_MHZ,
    NR_BW_INDEX_TO_MHZ,
    CarrierComponentType,
    PCELL_STATE_MAP,
    SCELL_STATE_MAP,
)
from model.models import CarrierComponentQCAINFO
from .common import parse_int, parse_optional_int, parse_response


def _parse_qcainfo_lte_component(
    values: List[str],
    cell_type: CarrierComponentType,
) -> Optional[CarrierComponentQCAINFO]:
    arfcn = parse_int(values[1])
    band = parse_int(values[3].split()[-1])
    dl_bandwidth = LTE_RB_INDEX_TO_MHZ.get(parse_int(values[2]), 0)
    state = (
        PCELL_STATE_MAP.get(values[4])
        if cell_type == CarrierComponentType.LTE_PCC
        else SCELL_STATE_MAP.get(values[4])
    )

    pci = parse_int(values[5])
    rsrp = parse_int(values[6])
    rsrq = parse_int(values[7])
    rssi = parse_int(values[8])
    sinr = parse_int(values[9])

    ulca = None
    ul_bandwidth = None
    ul_arfcn = None
    if cell_type == CarrierComponentType.LTE_SCC:
        ulca = parse_int(values[10])
        ul_bandwidth = LTE_RB_INDEX_TO_MHZ.get(parse_int(values[11]), None)
        ul_arfcn = parse_optional_int(values[12])

    return CarrierComponentQCAINFO(
        type=cell_type,
        arfcn=arfcn,
        dl_bandwidth=dl_bandwidth,
        band=band,
        state=state,
        pci=pci,
        rsrp=rsrp,
        rsrq=rsrq,
        sinr=sinr,
        rssi=rssi,
        ulca=ulca == 1,
        ul_bandwidth=ul_bandwidth,
        ul_arfcn=ul_arfcn,
    )


def _parse_qcainfo_nr_component(
    values: List[str],
    cell_type: CarrierComponentType,
) -> Optional[CarrierComponentQCAINFO]:
    arfcn = parse_int(values[1])
    band = parse_int(values[3].split()[-1])
    dl_bandwidth = NR_BW_INDEX_TO_MHZ.get(parse_int(values[2]), 0)

    state = None
    ulca = None
    ul_bandwidth = None
    ul_arfcn = None

    if cell_type == CarrierComponentType.NR_PCC:
        pci = parse_int(values[4])
        last_index = 4
    else:
        state = SCELL_STATE_MAP.get(values[4])
        pci = parse_int(values[5])
        ulca = parse_int(values[6])
        ul_bandwidth = NR_BW_INDEX_TO_MHZ.get(parse_int(values[7]), 0)
        ul_arfcn = parse_optional_int(values[8])
        last_index = 8

    rsrp = parse_int(values[last_index + 1])
    rsrq = parse_int(values[last_index + 2])
    sinr = parse_int(values[last_index + 3]) / 100.0

    return CarrierComponentQCAINFO(
        type=cell_type,
        arfcn=arfcn,
        dl_bandwidth=dl_bandwidth,
        band=band,
        state=state,
        pci=pci,
        rsrp=rsrp,
        rsrq=rsrq,
        sinr=sinr,
        ulca=ulca == 1,
        ul_bandwidth=ul_bandwidth,
        ul_arfcn=ul_arfcn,
    )


def parse_qcainfo(response: str) -> List[CarrierComponentQCAINFO]:
    components: List[CarrierComponentQCAINFO] = []

    found_sa_pcell = False
    found_nsa_pscell = False

    for values in parse_response(response, "+QCAINFO"):
        if len(values) < 5:
            continue

        is_5g = "NR5G" in values[3]
        raw_type = values[0]

        # Normalize LTE vs 5G component types using explicit prefixes.
        if not is_5g:
            cell_type = (
                CarrierComponentType.LTE_PCC
                if raw_type == "PCC"
                else CarrierComponentType.LTE_SCC
            )
        elif raw_type == "PCC":
            cell_type = CarrierComponentType.NR_PCC
            found_sa_pcell = True
        elif found_sa_pcell:
            cell_type = CarrierComponentType.NR_SCC
        elif not found_nsa_pscell:
            cell_type = CarrierComponentType.NR_PCC
            found_nsa_pscell = True
        else:
            cell_type = CarrierComponentType.NR_SCC

        try:
            is_lte = cell_type in (
                CarrierComponentType.LTE_PCC,
                CarrierComponentType.LTE_SCC,
            )
            if is_lte:
                component = _parse_qcainfo_lte_component(values, cell_type)
            else:
                component = _parse_qcainfo_nr_component(values, cell_type)

            if component:
                components.append(component)
        except (ValueError, IndexError):
            continue

    return components
