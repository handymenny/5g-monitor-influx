#!/usr/bin/env python3
"""SSH AT command client."""

import shlex
from typing import Optional

import paramiko


class AtCmdClient:
    """Execute AT commands over SSH using a remote atcmd wrapper."""

    def __init__(
        self,
        host: str,
        user: str,
        port: int,
        password: str,
        atcmd: str,
        timeout: float,
    ) -> None:
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.atcmd = atcmd
        self.timeout = timeout
        self._client: Optional["paramiko.SSHClient"] = None

    def __enter__(self) -> "AtCmdClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def connect(self) -> None:
        if self._client is not None:
            return

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                hostname=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                look_for_keys=False,
                allow_agent=False,
                timeout=self.timeout,
                banner_timeout=self.timeout,
                auth_timeout=self.timeout,
            )
        except Exception:
            client.close()
            raise

        self._client = client

    def close(self) -> None:
        if self._client is None:
            return
        self._client.close()
        self._client = None

    def run(self, command: str) -> str:
        try:
            if self._client is None:
                self.connect()

            if self._client is None:
                raise RuntimeError("SSH client is not connected")

            remote_cmd = f"{self.atcmd} {shlex.quote(command)}"
            _, stdout, stderr = self._client.exec_command(
                remote_cmd, timeout=self.timeout
            )  # nosec B601
            exit_status = stdout.channel.recv_exit_status()
            out = stdout.read().decode("utf-8", errors="ignore")
            err = stderr.read().decode("utf-8", errors="ignore")

            if exit_status != 0:
                combined = (out + "\n" + err).strip()
                if "OK" in combined:
                    return combined

                msg = err.strip() or out.strip()
                raise RuntimeError(
                    msg or f"SSH command failed ({exit_status}) for {command}"
                )

            return out
        except Exception as exc:
            raise RuntimeError(f"{command}: {exc}") from exc
