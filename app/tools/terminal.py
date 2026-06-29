"""Terminal tool adapter."""

from __future__ import annotations

from typing import Any

from app.core.base_tool import BaseTool, ToolCategory, ToolSpec
from app.core.result import ToolResult, ToolStatus
from app.services.terminal import TerminalService


class RunTerminalCommandTool(BaseTool):
    """Run a terminal command."""

    spec = ToolSpec(
        name="run_terminal_command",
        description="Run a terminal command and capture output.",
        category=ToolCategory.TERMINAL,
        parameters={"command": "Command string to run."},
        dangerous=True,
    )

    def __init__(self, service: TerminalService, *, timeout_seconds: int) -> None:
        self._service = service
        self._timeout_seconds = timeout_seconds

    def run(self, **kwargs: Any) -> ToolResult:
        result = self._service.run(
            str(kwargs["command"]),
            timeout_seconds=int(kwargs.get("timeout_seconds", self._timeout_seconds)),
        )
        data = {
            "command": result.command,
            "return_code": result.return_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
        if result.return_code == 0:
            return ToolResult.success(self.name, "Command completed successfully.", data)
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.FAILURE,
            message="Command completed with a non-zero exit code.",
            data=data,
            error=result.stderr.strip() or result.stdout.strip(),
        )
