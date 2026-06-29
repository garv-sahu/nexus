"""Base classes for Nexus tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.core.result import ToolResult


class ToolCategory(StrEnum):
    """High-level tool groups."""

    FILESYSTEM = "filesystem"
    BROWSER = "browser"
    APPLICATIONS = "applications"
    TERMINAL = "terminal"
    SYSTEM = "system"
    MEDIA = "media"


@dataclass(frozen=True)
class ToolSpec:
    """Metadata used by the agent and ToolManager."""

    name: str
    description: str
    category: ToolCategory
    parameters: dict[str, str] = field(default_factory=dict)
    dangerous: bool = False


class BaseTool(ABC):
    """Base class for all tools.

    Tools adapt strongly typed agent actions to service calls. They must not
    contain operating system implementation details.
    """

    spec: ToolSpec

    @property
    def name(self) -> str:
        """Return the public tool name."""

        return self.spec.name

    @abstractmethod
    def run(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with validated keyword arguments."""
