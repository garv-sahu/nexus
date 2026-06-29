"""Tool registration and execution gateway."""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from typing import Any

from app.core.base_tool import BaseTool
from app.core.exceptions import PermissionDeniedError, ToolNotFoundError
from app.core.result import ToolResult

PermissionHook = Callable[[BaseTool, dict[str, Any]], None]


class ToolManager:
    """Registers tools and routes every execution through permission hooks."""

    def __init__(
        self,
        *,
        permission_hooks: Iterable[PermissionHook] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._tools: dict[str, BaseTool] = {}
        self._permission_hooks = list(permission_hooks or [])
        self._logger = logger or logging.getLogger(__name__)

    def register(self, tool: BaseTool) -> None:
        """Register a tool by name."""

        self._tools[tool.name] = tool
        self._logger.debug("Registered tool: %s", tool.name)

    def register_many(self, tools: Iterable[BaseTool]) -> None:
        """Register multiple tools."""

        for tool in tools:
            self.register(tool)

    def list_tools(self) -> list[BaseTool]:
        """Return all registered tools."""

        return list(self._tools.values())

    def get(self, name: str) -> BaseTool:
        """Return a registered tool by name."""

        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(f"Tool not found: {name}") from exc

    def add_permission_hook(self, hook: PermissionHook) -> None:
        """Add a hook that can deny tool execution."""

        self._permission_hooks.append(hook)

    def execute(self, tool_name: str, arguments: dict[str, Any] | None = None) -> ToolResult:
        """Execute a registered tool and always return a ToolResult."""

        arguments = arguments or {}
        try:
            tool = self.get(tool_name)
            self._logger.info("Executing tool '%s' with arguments %s", tool_name, arguments)
            for hook in self._permission_hooks:
                hook(tool, arguments)
            result = tool.run(**arguments)
            self._logger.info("Tool '%s' completed with status %s", tool_name, result.status)
            return result
        except PermissionDeniedError as exc:
            self._logger.warning("Tool '%s' denied: %s", tool_name, exc)
            return ToolResult.denied(tool_name, str(exc), data={"arguments": arguments})
        except ToolNotFoundError as exc:
            self._logger.error("Tool lookup failed: %s", exc)
            return ToolResult.failure(tool_name, "Tool not found.", error=str(exc))
        except Exception as exc:  # pragma: no cover - defensive boundary
            self._logger.exception("Tool '%s' failed unexpectedly", tool_name)
            return ToolResult.failure(
                tool_name,
                "Tool execution failed.",
                error=f"{type(exc).__name__}: {exc}",
                data={"arguments": arguments},
            )
