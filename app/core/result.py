"""Structured results returned by tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ToolStatus(StrEnum):
    """Possible tool execution states."""

    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"


@dataclass(frozen=True)
class ToolResult:
    """A structured, serializable result from any tool."""

    tool_name: str
    status: ToolStatus
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    @property
    def ok(self) -> bool:
        """Whether the tool completed successfully."""

        return self.status == ToolStatus.SUCCESS

    @classmethod
    def success(
        cls,
        tool_name: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> "ToolResult":
        """Create a successful result."""

        return cls(
            tool_name=tool_name,
            status=ToolStatus.SUCCESS,
            message=message,
            data=data or {},
        )

    @classmethod
    def failure(
        cls,
        tool_name: str,
        message: str,
        *,
        error: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> "ToolResult":
        """Create a failed result."""

        return cls(
            tool_name=tool_name,
            status=ToolStatus.FAILURE,
            message=message,
            data=data or {},
            error=error,
        )

    @classmethod
    def denied(
        cls,
        tool_name: str,
        message: str,
        *,
        data: dict[str, Any] | None = None,
    ) -> "ToolResult":
        """Create a permission-denied result."""

        return cls(
            tool_name=tool_name,
            status=ToolStatus.DENIED,
            message=message,
            data=data or {},
        )
