#!/usr/bin/env python3
"""InfluxDB line protocol formatter."""

from dataclasses import asdict
from enum import Enum
from typing import Dict, Optional

from config.app_config import AppConfig
from model.models import CombinedServingCell, PacketDataCounter


class InfluxExporter:
    """Format metrics using InfluxDB line protocol."""

    def __init__(self, config: AppConfig) -> None:
        self._allowed_fields = config.allowed_fields
        self._derived_tags = config.derived_tags
        self._measurement = config.measurement
        self._static_tags = config.static_tags

    def _get_fields(self, source) -> Dict[str, object]:
        raw = asdict(source)
        allowed = self._allowed_fields
        if allowed is None:
            return raw

        return {key: value for key, value in raw.items() if key in allowed}

    def _tag_value(self, value) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, Enum):
            return str(value.value)
        return str(value)

    def _escape_measurement(self, value: str) -> str:
        return value.replace(" ", "\\ ").replace(",", "\\,")

    def _escape_tag(self, value: str) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace(" ", "\\ ")
            .replace(",", "\\,")
            .replace("=", "\\=")
        )

    def _escape_field_key(self, value: str) -> str:
        return value.replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")

    def _format_field_value(self, value) -> str:
        if isinstance(value, Enum):
            value = value.value
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int):
            return f"{value}i"
        if isinstance(value, float):
            if value != value:  # NaN
                return ""
            return f"{value}"
        return '"' + str(value).replace('"', '\\"') + '"'

    def line(
        self,
        measurement: str,
        tags: Dict[str, str],
        fields: Dict[str, object],
        timestamp_ns: int,
    ) -> Optional[str]:
        fields_clean = {k: v for k, v in fields.items() if v is not None}
        if not fields_clean:
            return None

        tag_parts = []
        for k, v in tags.items():
            if v is None or v == "" or v is False:
                continue
            tag_parts.append(f"{self._escape_tag(k)}={self._escape_tag(str(v))}")

        field_parts = []
        for k, v in fields_clean.items():
            field_val = self._format_field_value(v)
            if field_val == "" or field_val == "false":
                continue
            field_parts.append(f"{self._escape_field_key(k)}={field_val}")

        if not field_parts:
            return None

        meas = self._escape_measurement(measurement)
        tag_str = ("," + ",".join(tag_parts)) if tag_parts else ""
        field_str = ",".join(field_parts)

        return f"{meas}{tag_str} {field_str} {timestamp_ns}"

    def build_cell_lines(
        self,
        cells: list[CombinedServingCell],
        timestamp_ns: int,
    ) -> list[str]:
        lines: list[str] = []
        for cell in cells:
            line_tags = dict(self._static_tags)
            raw_fields = asdict(cell)
            for tag_key, field_key in self._derived_tags.items():
                if field_key in raw_fields:
                    tag_value = self._tag_value(raw_fields[field_key])
                    if tag_value is not None:
                        line_tags[tag_key] = tag_value

            line = self.line(
                self._measurement, line_tags, self._get_fields(cell), timestamp_ns
            )
            if line:
                lines.append(line)

        return lines

    def build_pktcnt_line(
        self,
        pkt_cnt: PacketDataCounter,
        timestamp_ns: int,
    ) -> str | None:
        line_tags = dict(self._static_tags)
        raw_fields = asdict(pkt_cnt)

        for tag_key, field_key in self._derived_tags.items():
            if field_key in raw_fields:
                tag_value = self._tag_value(raw_fields[field_key])
                if tag_value is not None:
                    line_tags[tag_key] = tag_value

        line = self.line(
            self._measurement, line_tags, self._get_fields(pkt_cnt), timestamp_ns
        )
        if line:
            return line

        return None

    def build_temp_lines(
        self,
        temp_readings: list,
        timestamp_ns: int,
    ) -> list[str]:
        lines: list[str] = []
        for reading in temp_readings:
            line_tags = dict(self._static_tags)
            raw_fields = asdict(reading)
            for tag_key, field_key in self._derived_tags.items():
                if field_key in raw_fields:
                    tag_value = self._tag_value(raw_fields[field_key])
                    if tag_value is not None:
                        line_tags[tag_key] = tag_value

            line = self.line(
                self._measurement, line_tags, self._get_fields(reading), timestamp_ns
            )
            if line:
                lines.append(line)

        return lines
