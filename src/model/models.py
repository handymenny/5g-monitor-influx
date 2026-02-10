#!/usr/bin/env python3
"""Data models for parsed modem responses."""

from dataclasses import dataclass
from typing import Optional

from .mappings import CarrierComponentState, CarrierComponentType, Rat
from ..util.optional_helpers import optional_avg, optional_round


@dataclass
class ServingCellQENG:
    rat: Rat
    mcc: Optional[int]
    mnc: Optional[int]
    pci: Optional[int]
    rsrp: Optional[int]
    rsrq: Optional[int]
    sinr: Optional[int]
    arfcn: Optional[int]
    band: Optional[int]
    dl_bandwidth: Optional[float]
    ul_bandwidth: Optional[float] = None
    cell_id: Optional[int] = None
    duplex: Optional[str] = None
    tac: Optional[int] = None
    rssi: Optional[int] = None
    cqi: Optional[int] = None
    tx_power: Optional[float] = None
    scs: Optional[int] = None


@dataclass
class CarrierComponentQCAINFO:
    type: CarrierComponentType
    arfcn: Optional[int]
    dl_bandwidth: Optional[float]
    band: Optional[int]
    pci: Optional[int]
    rsrp: Optional[int]
    rsrq: Optional[int]
    sinr: Optional[float]
    ulca: bool
    ul_bandwidth: Optional[float] = None
    ul_arfcn: Optional[int] = None
    rssi: Optional[int] = None
    state: Optional[CarrierComponentState] = None


@dataclass
class CombinedServingCell:
    rat: Optional[Rat] = None
    mcc: Optional[int] = None
    mnc: Optional[int] = None
    carrier_idx: int = 0
    pci: Optional[int] = None
    rsrp: Optional[int] = None
    rsrq: Optional[int] = None
    sinr: Optional[int] = None
    nr_sinr: Optional[float] = None
    rssi: Optional[int] = None
    arfcn: Optional[int] = None
    band: Optional[int] = None
    dl_bandwidth: Optional[int] = None
    ul_bandwidth: Optional[int] = None
    cell_id: Optional[int] = None
    duplex: Optional[str] = None
    tac: Optional[int] = None
    cqi: Optional[int] = None
    tx_power: Optional[float] = None
    scs: Optional[int] = None
    type: Optional[CarrierComponentType] = None
    ulca: bool = False
    ul_arfcn: Optional[int] = None
    state: Optional[CarrierComponentState] = None

    @classmethod
    def from_sources(
        cls,
        qeng: Optional[ServingCellQENG] = None,
        qcainfo: Optional[CarrierComponentQCAINFO] = None,
    ) -> "CombinedServingCell":
        if qeng is None and qcainfo is None:
            raise ValueError("qeng or qcainfo must be provided")

        combined = cls()

        if qcainfo:
            combined.type = qcainfo.type
            combined.arfcn = qcainfo.arfcn
            combined.band = qcainfo.band
            combined.pci = qcainfo.pci
            combined.dl_bandwidth = optional_round(qcainfo.dl_bandwidth)
            combined.ul_bandwidth = optional_round(qcainfo.ul_bandwidth)
            combined.ulca = qcainfo.ulca
            combined.ul_arfcn = qcainfo.ul_arfcn
            combined.state = qcainfo.state
            combined.rsrp = qcainfo.rsrp
            combined.rsrq = qcainfo.rsrq
            combined.sinr = optional_round(qcainfo.sinr)
            combined.rssi = qcainfo.rssi

        if qeng:
            combined.rat = qeng.rat
            combined.mcc = qeng.mcc
            combined.mnc = qeng.mnc
            combined.pci = qeng.pci if qeng.pci is not None else combined.pci
            combined.arfcn = qeng.arfcn if qeng.arfcn is not None else combined.arfcn
            combined.band = qeng.band if qeng.band is not None else combined.band
            combined.dl_bandwidth = (
                optional_round(qeng.dl_bandwidth)
                if qeng.dl_bandwidth is not None
                else combined.dl_bandwidth
            )
            combined.ul_bandwidth = (
                optional_round(qeng.ul_bandwidth)
                if qeng.ul_bandwidth is not None
                else combined.ul_bandwidth
            )
            combined.cell_id = qeng.cell_id if qeng.cell_id is not None else None
            combined.duplex = qeng.duplex if qeng.duplex is not None else None
            combined.tac = qeng.tac if qeng.tac is not None else None
            combined.cqi = qeng.cqi if qeng.cqi is not None else None
            combined.tx_power = qeng.tx_power if qeng.tx_power is not None else None
            combined.scs = qeng.scs if qeng.scs is not None else None

            if qcainfo:
                avg_rsrp = optional_avg(qeng.rsrp, qcainfo.rsrp)
                if avg_rsrp is not None:
                    combined.rsrp = round(avg_rsrp)

                avg_rsrq = optional_avg(qeng.rsrq, qcainfo.rsrq)
                if avg_rsrq is not None:
                    combined.rsrq = round(avg_rsrq)

                if combined.rat in (Rat.NR_NSA, Rat.NR_SA):
                    # For NR, do not average SINR from different sources.
                    combined.sinr = qeng.sinr
                    combined.nr_sinr = qcainfo.sinr
                else:
                    avg_sinr = optional_avg(qeng.sinr, qcainfo.sinr)
                    if avg_sinr is not None:
                        combined.sinr = round(avg_sinr)

                if qeng.rssi is not None or qcainfo.rssi is not None:
                    avg_rssi = optional_avg(qeng.rssi, qcainfo.rssi)
                    if avg_rssi is not None:
                        combined.rssi = round(avg_rssi)
            else:
                combined.rsrp = qeng.rsrp
                combined.rsrq = qeng.rsrq
                combined.sinr = qeng.sinr
                combined.rssi = qeng.rssi

            if combined.type is None:
                combined.type = (
                    CarrierComponentType.LTE_PCC
                    if qeng.rat == Rat.LTE
                    else CarrierComponentType.NR_PCC
                )

        return combined
