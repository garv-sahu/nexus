"""Server boundary for future MCP support."""

from __future__ import annotations

from dataclasses import dataclass

from app.mcp.registry import MCPRegistry


@dataclass
class MCPServer:
    """Placeholder boundary object for future MCP hosting."""

    registry: MCPRegistry

    def is_configured(self) -> bool:
        """Return whether MCP servers are registered."""

        return bool(self.registry.servers)
