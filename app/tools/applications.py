"""Application tool adapters."""

from __future__ import annotations

from typing import Any

from app.core.base_tool import BaseTool, ToolCategory, ToolSpec
from app.core.result import ToolResult
from app.services.applications import ApplicationService


class OpenApplicationTool(BaseTool):
    """Open an application or file with the Windows shell."""

    spec = ToolSpec(
        name="open_application",
        description="Open an application, executable, shortcut, or file.",
        category=ToolCategory.APPLICATIONS,
        parameters={"target": "Application name, executable, shortcut, or file path."},
    )

    def __init__(self, service: ApplicationService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        target = self._service.open_application(str(kwargs["target"]))
        return ToolResult.success(self.name, f"Opened application: {target}", {"target": target})


class CloseApplicationTool(BaseTool):
    """Close a process by image name."""

    spec = ToolSpec(
        name="close_application",
        description="Close a running application by process name.",
        category=ToolCategory.APPLICATIONS,
        parameters={"process_name": "Process image name, such as notepad.exe."},
        dangerous=True,
    )

    def __init__(self, service: ApplicationService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        process_name = self._service.close_application(str(kwargs["process_name"]))
        return ToolResult.success(
            self.name,
            f"Closed application: {process_name}",
            {"process_name": process_name},
        )
