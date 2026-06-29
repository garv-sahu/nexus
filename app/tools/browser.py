"""Browser tool adapters."""

from __future__ import annotations

from typing import Any

from app.core.base_tool import BaseTool, ToolCategory, ToolSpec
from app.core.result import ToolResult
from app.services.browser import BrowserService


class OpenUrlTool(BaseTool):
    """Open a URL in the default browser."""

    spec = ToolSpec(
        name="open_url",
        description="Open a URL in the default browser.",
        category=ToolCategory.BROWSER,
        parameters={"url": "URL to open."},
    )

    def __init__(self, service: BrowserService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        url = self._service.open_url(str(kwargs["url"]))
        return ToolResult.success(self.name, f"Opened URL: {url}", {"url": url})


class GoogleSearchTool(BaseTool):
    """Search Google."""

    spec = ToolSpec(
        name="google_search",
        description="Search Google in the default browser.",
        category=ToolCategory.BROWSER,
        parameters={"query": "Search query."},
    )

    def __init__(self, service: BrowserService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        url = self._service.google_search(str(kwargs["query"]))
        return ToolResult.success(self.name, f"Opened Google search: {url}", {"url": url})


class YouTubeSearchTool(BaseTool):
    """Search YouTube."""

    spec = ToolSpec(
        name="youtube_search",
        description="Search YouTube in the default browser.",
        category=ToolCategory.BROWSER,
        parameters={"query": "Search query."},
    )

    def __init__(self, service: BrowserService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        url = self._service.youtube_search(str(kwargs["query"]))
        return ToolResult.success(self.name, f"Opened YouTube search: {url}", {"url": url})


class GithubSearchTool(BaseTool):
    """Search GitHub."""

    spec = ToolSpec(
        name="github_search",
        description="Search GitHub in the default browser.",
        category=ToolCategory.BROWSER,
        parameters={"query": "Search query."},
    )

    def __init__(self, service: BrowserService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        url = self._service.github_search(str(kwargs["query"]))
        return ToolResult.success(self.name, f"Opened GitHub search: {url}", {"url": url})
