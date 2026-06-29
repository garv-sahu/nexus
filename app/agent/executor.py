"""Executor for planned actions."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.agent.planner import Action
from app.core.result import ToolResult
from app.core.tool_manager import ToolManager


@dataclass(frozen=True)
class ExecutionSummary:
    """Summary of an executed plan."""

    results: list[ToolResult] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        """Whether every result succeeded."""

        return bool(self.results) and all(result.ok for result in self.results)


class Executor:
    """Execute typed actions through the ToolManager."""

    def __init__(
        self,
        tool_manager: ToolManager,
        *,
        logger: logging.Logger | None = None,
    ) -> None:
        self._tool_manager = tool_manager
        self._logger = logger or logging.getLogger(__name__)

    def execute(self, actions: list[Action]) -> ExecutionSummary:
        """Execute a sequence of actions."""

        results: list[ToolResult] = []
        for action in actions:
            self._logger.info("Executing action %s via %s", action.action_id, action.tool_name)
            result = self._tool_manager.execute(action.tool_name, action.arguments)
            results.append(result)
        return ExecutionSummary(results=results)
