"""Registry abstraction for future MCP tools and servers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MCPRegistry:
    """In-memory registry prepared for future MCP integration."""

    servers: dict[str, str] = field(default_factory=dict)

    def register_server(self, name: str, endpoint: str) -> None:
        """Register an MCP server endpoint."""

        self.servers[name] = endpoint

    def unregister_server(self, name: str) -> None:
        """Remove an MCP server endpoint."""

        self.servers.pop(name, None)

    def list_servers(self) -> dict[str, str]:
        """Return registered MCP servers."""

        return dict(self.servers)
