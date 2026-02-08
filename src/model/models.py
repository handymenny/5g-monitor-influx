#!/usr/bin/env python3
"""Data models for parsed modem responses."""

from dataclasses import dataclass
from typing import Optional

from .mappings import CarrierComponentState, CarrierComponentType, Rat


@dataclass
class ServingCellQENG:
    rat: Rat
    mcc: int
    mnc: int
    pci: int
    rsrp: int
    rsrq: int
    sinr: int
    arfcn: int
    band: int
    dl_bandwidth: float
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
    arfcn: int
    dl_bandwidth: float
    band: int
    pci: int
    rsrp: int
    rsrq: int
    sinr: float
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
    pci: int = 0
    rsrp: int = 0
    rsrq: int = 0
    sinr: int = 0
    nr_sinr: Optional[float] = None
    rssi: Optional[int] = None
    arfcn: int = 0
    band: int = 0
    dl_bandwidth: int = 0
    ul_bandwidth: Optional[int] = None
    cell_id: Optional[int] = None
    duplex: Optional[str] = None
    tac: Optional[int] = None
    cqi: Optional[int] = None
    tx_power: Optional[float] = None
    scs: Optional[int] = None
    type: Optional[CarrierComponentType] = None
    ulca: Optional[bool] = None
    ul_arfcn: Optional[int] = None
    state: Optional[CarrierComponentState] = None

    @staticmethod
    def _avg_signal(a: Optional[float], b: Optional[float]) -> Optional[float]:
        if a is None:
            return b
        if b is None:
            return a
        if a == b:
            return a
        return (a + b) / 2.0

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
            combined.dl_bandwidth = round(qcainfo.dl_bandwidth)
            combined.ul_bandwidth = (
                round(qcainfo.ul_bandwidth) if qcainfo.ul_bandwidth else None
            )
            combined.ulca = qcainfo.ulca
            combined.ul_arfcn = qcainfo.ul_arfcn
            combined.state = qcainfo.state
            combined.rsrp = qcainfo.rsrp
            combined.rsrq = qcainfo.rsrq
            combined.sinr = round(qcainfo.sinr)
            combined.rssi = qcainfo.rssi

        if qeng:
            combined.rat = qeng.rat
            combined.mcc = qeng.mcc
            combined.mnc = qeng.mnc
            combined.pci = qeng.pci
            combined.arfcn = qeng.arfcn
            combined.band = qeng.band
            combined.dl_bandwidth = round(qeng.dl_bandwidth)
            combined.ul_bandwidth = (
                round(qeng.ul_bandwidth) if qeng.ul_bandwidth else None
            )
            combined.cell_id = qeng.cell_id
            combined.duplex = qeng.duplex
            combined.tac = qeng.tac
            combined.cqi = qeng.cqi
            combined.tx_power = qeng.tx_power
            combined.scs = qeng.scs

            if qcainfo:
                avg_rsrp = cls._avg_signal(qeng.rsrp, qcainfo.rsrp)
                if avg_rsrp is not None:
                    combined.rsrp = round(avg_rsrp)

                avg_rsrq = cls._avg_signal(qeng.rsrq, qcainfo.rsrq)
                if avg_rsrq is not None:
                    combined.rsrq = round(avg_rsrq)

                if combined.rat in (Rat.NR_NSA, Rat.NR_SA):
                    # For NR, do not average SINR from different sources.
                    combined.sinr = qeng.sinr
                    combined.nr_sinr = qcainfo.sinr
                else:
                    avg_sinr = cls._avg_signal(qeng.sinr, qcainfo.sinr)
                    if avg_sinr is not None:
                        combined.sinr = round(avg_sinr)

                if qeng.rssi is not None or qcainfo.rssi is not None:
                    avg_rssi = cls._avg_signal(qeng.rssi, qcainfo.rssi)
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
