#!/usr/bin/env python3
"""Cell combination logic extracted from the main monitor script."""

from typing import List, Optional

from .mappings import CarrierComponentType, Rat
from .models import CarrierComponentQCAINFO, CombinedServingCell, ServingCellQENG


def find_matching_pcc(
    qeng: Optional[ServingCellQENG],
    expected_type: CarrierComponentType,
    ca: List[CarrierComponentQCAINFO],
) -> Optional[CarrierComponentQCAINFO]:
    """Return the matching PCC component for a serving cell."""
    if not qeng:
        return None
    for comp in ca:
        if comp.type != expected_type:
            continue
        if comp.arfcn == qeng.arfcn and comp.pci == qeng.pci:
            return comp
    return None


def collect_cells(
    serving_cells: List[ServingCellQENG],
    ca: List[CarrierComponentQCAINFO],
) -> List[CombinedServingCell]:
    cells: List[CombinedServingCell] = []

    for serving in serving_cells:
        if serving.rat == Rat.LTE:
            expected_type = CarrierComponentType.LTE_PCC
        elif serving.rat in (Rat.NR_NSA, Rat.NR_SA):
            expected_type = CarrierComponentType.NR_PCC
        else:
            continue

        pcc = find_matching_pcc(serving, expected_type, ca)

        # If a PCC is expected but not found, skip all cells to avoid partial data.
        if pcc is None:
            ca = []

        combined = CombinedServingCell.from_sources(qeng=serving, qcainfo=pcc)
        cells.append(combined)

    lte_scc_idx = 0
    nr_scc_idx = 0

    for comp in ca:
        if comp.type not in (CarrierComponentType.LTE_SCC, CarrierComponentType.NR_SCC):
            continue

        scc_combined = CombinedServingCell.from_sources(qcainfo=comp)
        # QCAINFO does not include MCC/MNC; reuse PCC values for operator tagging.
        scc_combined.mcc = cells[0].mcc if cells else None
        scc_combined.mnc = cells[0].mnc if cells else None
        if comp.type == CarrierComponentType.LTE_SCC:
            lte_scc_idx += 1
            scc_combined.carrier_idx = lte_scc_idx
        else:
            nr_scc_idx += 1
            scc_combined.carrier_idx = nr_scc_idx
        cells.append(scc_combined)

    return cells
