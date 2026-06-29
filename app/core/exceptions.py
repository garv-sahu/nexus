"""Custom exceptions used across Nexus."""

from __future__ import annotations


class NexusError(Exception):
    """Base exception for all expected Nexus errors."""


class ConfigurationError(NexusError):
    """Raised when configuration is invalid."""


class PlanningError(NexusError):
    """Raised when a request cannot be planned."""


class LLMError(NexusError):
    """Raised when the language model provider fails."""


class ToolNotFoundError(NexusError):
    """Raised when a requested tool is not registered."""


class ToolExecutionError(NexusError):
    """Raised when a tool cannot complete successfully."""


class PermissionDeniedError(NexusError):
    """Raised when permission hooks reject an action."""


class ServiceError(NexusError):
    """Raised by services when operating system work fails."""
