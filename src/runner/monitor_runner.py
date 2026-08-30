#!/usr/bin/env python3
"""Monitoring runtime logic."""

import sys
import time
import traceback

from model.mappings import Source

from .atcmd_client import AtCmdClient
from config.app_config import AppConfig
from export.influx_exporter import InfluxExporter
from model.combine_sources import collect_cells
from parsing.qcainfo import parse_qcainfo
from parsing.qeng import parse_qeng_servingcell
from parsing.qgdnrcnt import parse_qgdnrcnt


class MonitorRunner:
    """Collect modem metrics and emit InfluxDB line protocol."""

    def __init__(self, config: AppConfig, debug: bool) -> None:
        self._config = config
        self._debug = debug

    def run(self) -> int:
        try:
            atcmd_client = AtCmdClient(
                host=self._config.ssh_host,
                user=self._config.ssh_user,
                port=self._config.ssh_port,
                password=self._config.ssh_password,
                atcmd="atcmd",
                timeout=self._config.timeout,
            )
            with atcmd_client:
                # Filter sources based on config, default to all if not specified
                sources = self._config.sources

                if Source.QENG_SERVINGCELL in sources:
                    serving_raw = atcmd_client.run('AT+QENG="servingcell"')
                    if self._debug:
                        print(
                            'AT+QENG="servingcell" response:\n' + serving_raw,
                            file=sys.stderr,
                        )
                else:
                    serving_raw = ""

                if Source.QCAINFO in sources:
                    qca_raw = atcmd_client.run("AT+QCAINFO")
                    if self._debug:
                        print("\nAT+QCAINFO response:\n" + qca_raw, file=sys.stderr)
                else:
                    qca_raw = ""

                if Source.QGDNRCNT in sources:
                    pkt_cnt_raw = atcmd_client.run("AT+QGDNRCNT?")
                    if self._debug:
                        print(
                            "\nAT+QGDNRCNT? response:\n" + pkt_cnt_raw, file=sys.stderr
                        )
                else:
                    pkt_cnt_raw = ""

                serving_cells = parse_qeng_servingcell(serving_raw)
                ca = parse_qcainfo(qca_raw)
                pkt_cnt = parse_qgdnrcnt(pkt_cnt_raw)

                timestamp_ns = time.time_ns()
                cells = collect_cells(serving_cells, ca)
                exporter = InfluxExporter(self._config)
                cell_lines = exporter.build_cell_lines(cells, timestamp_ns)
                if pkt_cnt:
                    pktcnt_line = exporter.build_pktcnt_line(pkt_cnt, timestamp_ns)
                else:
                    pktcnt_line = None

                # concatenate the cell lines and packet count line into a single list
                lines = cell_lines
                if pktcnt_line is not None:
                    lines.append(pktcnt_line)

                # Print the lines to stdout
                for line in lines:
                    print(line)

        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            traceback.print_exc()

        return 0
