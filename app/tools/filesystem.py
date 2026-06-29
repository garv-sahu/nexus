"""Filesystem tool adapters."""

from __future__ import annotations

from typing import Any

from app.core.base_tool import BaseTool, ToolCategory, ToolSpec
from app.core.result import ToolResult
from app.services.filesystem import FilesystemService


class CreateFolderTool(BaseTool):
    """Create a folder if it does not exist."""

    spec = ToolSpec(
        name="create_folder",
        description="Create a folder, including missing parents.",
        category=ToolCategory.FILESYSTEM,
        parameters={"path": "Folder path to create."},
    )

    def __init__(self, service: FilesystemService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        path = str(kwargs["path"])
        target = self._service.create_folder(path)
        return ToolResult.success(self.name, f"Created folder: {target}", {"path": str(target)})


class DeleteFolderTool(BaseTool):
    """Delete a folder and all of its contents."""

    spec = ToolSpec(
        name="delete_folder",
        description="Delete a folder recursively.",
        category=ToolCategory.FILESYSTEM,
        parameters={"path": "Folder path to delete."},
        dangerous=True,
    )

    def __init__(self, service: FilesystemService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        path = str(kwargs["path"])
        target = self._service.delete_folder(path)
        return ToolResult.success(self.name, f"Deleted folder: {target}", {"path": str(target)})


class CopyPathTool(BaseTool):
    """Copy a file or folder."""

    spec = ToolSpec(
        name="copy_path",
        description="Copy a file or folder to a destination.",
        category=ToolCategory.FILESYSTEM,
        parameters={
            "source": "Source file or folder.",
            "destination": "Destination file or folder.",
        },
    )

    def __init__(self, service: FilesystemService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        destination = self._service.copy(str(kwargs["source"]), str(kwargs["destination"]))
        return ToolResult.success(
            self.name,
            f"Copied to: {destination}",
            {"destination": str(destination)},
        )


class MovePathTool(BaseTool):
    """Move a file or folder."""

    spec = ToolSpec(
        name="move_path",
        description="Move a file or folder to a destination.",
        category=ToolCategory.FILESYSTEM,
        parameters={
            "source": "Source file or folder.",
            "destination": "Destination file or folder.",
        },
    )

    def __init__(self, service: FilesystemService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        destination = self._service.move(str(kwargs["source"]), str(kwargs["destination"]))
        return ToolResult.success(
            self.name,
            f"Moved to: {destination}",
            {"destination": str(destination)},
        )


class RenamePathTool(BaseTool):
    """Rename a file or folder inside its current parent."""

    spec = ToolSpec(
        name="rename_path",
        description="Rename a file or folder.",
        category=ToolCategory.FILESYSTEM,
        parameters={"source": "Existing path.", "new_name": "New filename or folder name."},
    )

    def __init__(self, service: FilesystemService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        destination = self._service.rename(str(kwargs["source"]), str(kwargs["new_name"]))
        return ToolResult.success(
            self.name,
            f"Renamed to: {destination}",
            {"destination": str(destination)},
        )


class SearchFilesTool(BaseTool):
    """Search files below a folder with a glob pattern."""

    spec = ToolSpec(
        name="search_files",
        description="Search for files or folders using a glob pattern.",
        category=ToolCategory.FILESYSTEM,
        parameters={
            "root": "Root folder to search.",
            "pattern": "Glob pattern, such as '*.txt'.",
            "limit": "Maximum number of matches.",
        },
    )

    def __init__(self, service: FilesystemService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        limit = int(kwargs.get("limit", 50))
        matches = self._service.search(str(kwargs["root"]), str(kwargs["pattern"]), limit=limit)
        data = {"matches": [str(path) for path in matches], "count": len(matches)}
        return ToolResult.success(self.name, f"Found {len(matches)} match(es).", data)


class ReadTextFileTool(BaseTool):
    """Read a text file."""

    spec = ToolSpec(
        name="read_text_file",
        description="Read a UTF-8 text file.",
        category=ToolCategory.FILESYSTEM,
        parameters={"path": "Text file path."},
    )

    def __init__(self, service: FilesystemService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        path = str(kwargs["path"])
        content = self._service.read_text(path)
        return ToolResult.success(
            self.name,
            f"Read file: {path}",
            {"path": path, "content": content},
        )
