#!/usr/bin/env python3
"""Mapping tables for modem values."""

from enum import Enum


class Rat(str, Enum):
    LTE = "LTE"
    NR_NSA = "5G-NSA"
    NR_SA = "5G-SA"


class CarrierComponentType(str, Enum):
    LTE_PCC = "LTE-PCC"
    LTE_SCC = "LTE-SCC"
    NR_PCC = "5G-PCC"
    NR_SCC = "5G-SCC"


class CarrierComponentState(str, Enum):
    PCC_IDLE = "Idle"
    PCC_REGISTERED = "Registered"
    PCC_SEARCHING = "Searching"
    PCC_DENIED = "Denied"
    PCC_UNKNOWN = "Unknown"
    PCC_ROAMING = "Roaming"
    SCC_DECONFIGURED = "Deconfigured"
    SCC_INACTIVE = "Inactive"
    SCC_ACTIVE = "Active"


PCELL_STATE_MAP = {
    "0": CarrierComponentState.PCC_IDLE,
    "1": CarrierComponentState.PCC_REGISTERED,
    "2": CarrierComponentState.PCC_SEARCHING,
    "3": CarrierComponentState.PCC_DENIED,
    "4": CarrierComponentState.PCC_UNKNOWN,
    "5": CarrierComponentState.PCC_ROAMING,
}

SCELL_STATE_MAP = {
    "0": CarrierComponentState.SCC_DECONFIGURED,
    "1": CarrierComponentState.SCC_INACTIVE,
    "2": CarrierComponentState.SCC_ACTIVE,
}

LTE_BW_INDEX_TO_MHZ = {
    0: 1.4,
    1: 3.0,
    2: 5.0,
    3: 10.0,
    4: 15.0,
    5: 20.0,
}

LTE_RB_INDEX_TO_MHZ = {
    6: 1.4,
    15: 3.0,
    25: 5.0,
    50: 10.0,
    75: 15.0,
    100: 20.0,
}

NR_BW_INDEX_TO_MHZ = {
    0: 5.0,
    1: 10.0,
    2: 15.0,
    3: 20.0,
    4: 25.0,
    5: 30.0,
    6: 40.0,
    7: 50.0,
    8: 60.0,
    9: 70.0,
    10: 80.0,
    11: 90.0,
    12: 100.0,
    13: 200.0,
    14: 400.0,
    15: 35.0,
    16: 45.0,
}

NR_SCS_INDEX_TO_KHZ = {
    0: 15,
    1: 30,
    2: 60,
    3: 120,
    4: 240,
}
