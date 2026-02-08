#!/usr/bin/env python3
"""SSH-based Quectel monitor exporter (InfluxDB line protocol)."""

import argparse
from config.app_config import AppConfig
from runner.monitor_runner import MonitorRunner


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Quectel monitor exporter (InfluxDB line protocol)"
    )
    parser.add_argument(
        "--config",
        default="config/export_config.yaml",
        help="YAML config path (default: config/export_config.yaml)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print raw AT responses to stderr for debugging (default: false)",
    )

    args = parser.parse_args()

    config = AppConfig.from_file(args.config)
    return MonitorRunner(config, args.debug).run()


if __name__ == "__main__":
    raise SystemExit(main())
