#!/usr/bin/env python3
"""Shared YAML config loader for monitor and exporter."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import yaml
from model.mappings import Source


@dataclass(frozen=True)
class AppConfig:
    ssh_host: str
    ssh_user: str = "root"
    ssh_port: int = 22
    ssh_password: str = ""
    timeout: float = 10.0
    measurement: str = "modem"
    allowed_fields: Optional[set[str]] = None
    static_tags: Dict[str, str] = field(default_factory=dict)
    derived_tags: Dict[str, str] = field(default_factory=dict)
    sources: list[Source] = field(default_factory=list)

    @classmethod
    def from_file(cls, config_path: str) -> "AppConfig":
        payload = cls._load_yaml(config_path)

        ssh_host = cls._required(payload, "ssh_host", config_path)
        ssh_password = cls._required(payload, "ssh_password", config_path)
        ssh_user = str(payload.get("ssh_user", "root"))
        ssh_port = int(payload.get("ssh_port", 22))
        timeout = float(payload.get("timeout", 10.0))
        measurement = str(payload.get("measurement", "modem"))

        raw_fields = payload.get("allowed_fields")
        allowed_fields = None
        if isinstance(raw_fields, list):
            allowed_fields = {str(item) for item in raw_fields}

        raw_static_tags = payload.get("static_tags")
        static_tags: Dict[str, str] = {}
        if isinstance(raw_static_tags, dict):
            for key, value in raw_static_tags.items():
                if isinstance(key, str) and isinstance(value, str):
                    static_tags[key] = value

        raw_tags = payload.get("derived_tags")
        derived_tags: Dict[str, str] = {}
        if isinstance(raw_tags, dict):
            for key, value in raw_tags.items():
                if isinstance(key, str) and isinstance(value, str):
                    derived_tags[key] = value

        raw_sources = payload.get("sources")

        # All by default if not specified, otherwise parse the list of sources
        sources = [Source.QENG_SERVINGCELL, Source.QCAINFO, Source.QGDNRCNT]
        if isinstance(raw_sources, list):
            sources = []
            for item in raw_sources:
                if isinstance(item, str):
                    try:
                        source_enum = Source.from_string(item)
                        sources.append(source_enum)
                    except ValueError as e:
                        raise SystemExit(
                            f"Invalid source '{item}' in {config_path}: {e}"
                        )

        return cls(
            ssh_host=ssh_host,
            ssh_password=ssh_password,
            ssh_user=ssh_user,
            ssh_port=ssh_port,
            timeout=timeout,
            measurement=measurement,
            allowed_fields=allowed_fields,
            static_tags=static_tags,
            derived_tags=derived_tags,
            sources=sources,
        )

    @staticmethod
    def _load_yaml(config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, "r", encoding="utf-8") as handle:
                payload = yaml.safe_load(handle)
        except FileNotFoundError as exc:
            raise SystemExit(f"config not found: {config_path}") from exc
        except yaml.YAMLError as exc:
            raise SystemExit(f"invalid YAML config: {config_path}") from exc

        if not isinstance(payload, dict):
            raise SystemExit(f"invalid config format: {config_path}")

        return payload

    @staticmethod
    def _required(payload: Dict[str, Any], key: str, config_path: str) -> str:
        value = payload.get(key)
        if value is None or value == "":
            raise SystemExit(f"config missing '{key}' in {config_path}")
        return str(value)
