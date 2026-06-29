"""System tool adapters."""

from __future__ import annotations

from typing import Any

from app.core.base_tool import BaseTool, ToolCategory, ToolSpec
from app.core.result import ToolResult
from app.services.system import SystemService


class SystemInfoTool(BaseTool):
    """Read system information."""

    spec = ToolSpec(
        name="system_info",
        description="Read operating system, CPU, memory, and disk information.",
        category=ToolCategory.SYSTEM,
    )

    def __init__(self, service: SystemService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        info = self._service.info()
        return ToolResult.success(self.name, "Read system information.", info)


class ShutdownTool(BaseTool):
    """Shutdown the computer."""

    spec = ToolSpec(
        name="shutdown",
        description="Shutdown the computer immediately.",
        category=ToolCategory.SYSTEM,
        dangerous=True,
    )

    def __init__(self, service: SystemService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        action = self._service.shutdown()
        return ToolResult.success(self.name, "Shutdown command issued.", {"action": action})


class RestartTool(BaseTool):
    """Restart the computer."""

    spec = ToolSpec(
        name="restart",
        description="Restart the computer immediately.",
        category=ToolCategory.SYSTEM,
        dangerous=True,
    )

    def __init__(self, service: SystemService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        action = self._service.restart()
        return ToolResult.success(self.name, "Restart command issued.", {"action": action})
