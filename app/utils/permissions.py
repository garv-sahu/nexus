"""Permission hooks for tool execution."""

from __future__ import annotations

from typing import Any

from app.core.base_tool import BaseTool
from app.core.exceptions import PermissionDeniedError


def dangerous_action_guard(*, allow_dangerous_actions: bool) -> Any:
    """Return a permission hook that blocks dangerous tools by default."""

    def hook(tool: BaseTool, arguments: dict[str, Any]) -> None:
        if tool.spec.dangerous and not allow_dangerous_actions:
            raise PermissionDeniedError(
                f"'{tool.name}' is dangerous and is disabled. "
                "Set NEXUS_ALLOW_DANGEROUS_ACTIONS=true to enable it."
            )

    return hook
