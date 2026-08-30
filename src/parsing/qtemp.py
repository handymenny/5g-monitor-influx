#!/usr/bin/env python3
"""Parser for +QTEMP responses."""

from typing import List

from model.models import TemperatureReading
from .common import parse_int, parse_response


def parse_qtemp(response: str, temp_sensors: list[str]) -> List[TemperatureReading]:
    # Example response:
    #    +QTEMP:"modem-lte-sub6-pa1","41"
    #    +QTEMP:"cpuss-0-usr","46"
    #    +QTEMP:"modem-ambient-usr","43"

    readings = []
    for values in parse_response(response, "+QTEMP"):
        if len(values) < 2:
            continue

        try:
            temp_sensor_name: str = str(values[0])
            temp_celsius: int = parse_int(values[1], 0)  # type: ignore always an int

            if temp_sensor_name in temp_sensors:
                readings.append(
                    TemperatureReading(
                        temp_sensor_name=temp_sensor_name,
                        temp_celsius=temp_celsius,
                    )
                )
        except (ValueError, IndexError):
            pass

    return readings
