"""Tool factories for Nexus."""

from __future__ import annotations

from app.config import Settings
from app.core.base_tool import BaseTool
from app.services.applications import ApplicationService
from app.services.browser import BrowserService
from app.services.filesystem import FilesystemService
from app.services.media import MediaService
from app.services.system import SystemService
from app.services.terminal import TerminalService
from app.tools.applications import CloseApplicationTool, OpenApplicationTool
from app.tools.browser import (
    GithubSearchTool,
    GoogleSearchTool,
    OpenUrlTool,
    YouTubeSearchTool,
)
from app.tools.filesystem import (
    CopyPathTool,
    CreateFolderTool,
    DeleteFolderTool,
    MovePathTool,
    ReadTextFileTool,
    RenamePathTool,
    SearchFilesTool,
)
from app.tools.media import MediaControlTool
from app.tools.system import RestartTool, ShutdownTool, SystemInfoTool
from app.tools.terminal import RunTerminalCommandTool


def build_default_tools(settings: Settings) -> list[BaseTool]:
    """Create all built-in tools with their service dependencies."""

    filesystem = FilesystemService()
    browser = BrowserService()
    applications = ApplicationService()
    terminal = TerminalService()
    system = SystemService()
    media = MediaService()

    return [
        CreateFolderTool(filesystem),
        DeleteFolderTool(filesystem),
        CopyPathTool(filesystem),
        MovePathTool(filesystem),
        RenamePathTool(filesystem),
        SearchFilesTool(filesystem),
        ReadTextFileTool(filesystem),
        OpenUrlTool(browser),
        GoogleSearchTool(browser),
        YouTubeSearchTool(browser),
        GithubSearchTool(browser),
        OpenApplicationTool(applications),
        CloseApplicationTool(applications),
        RunTerminalCommandTool(terminal, timeout_seconds=settings.terminal_timeout_seconds),
        SystemInfoTool(system),
        ShutdownTool(system),
        RestartTool(system),
        MediaControlTool(media),
    ]
