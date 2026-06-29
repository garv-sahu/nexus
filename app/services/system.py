"""System service for host information and power actions."""

from __future__ import annotations

import getpass
import platform
import socket
import subprocess
from typing import Any

try:
    import psutil
except ImportError:  # pragma: no cover - depends on local environment
    psutil = None  # type: ignore[assignment]


class SystemService:
    """Read system information and perform power operations."""

    def info(self) -> dict[str, Any]:
        return {
            "user": getpass.getuser(),
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count() if psutil else None,
            "memory": psutil.virtual_memory()._asdict() if psutil else {},
            "disk": psutil.disk_usage("/")._asdict() if psutil else {},
        }

    def shutdown(self) -> str:
        subprocess.run(["shutdown", "/s", "/t", "0"], check=False)
        return "shutdown"

    def restart(self) -> str:
        subprocess.run(["shutdown", "/r", "/t", "0"], check=False)
        return "restart"
