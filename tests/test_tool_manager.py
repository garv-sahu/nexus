from __future__ import annotations

from app.core.exceptions import PermissionDeniedError
from app.core.tool_manager import ToolManager
from app.services.filesystem import FilesystemService
from app.tools.filesystem import CreateFolderTool, DeleteFolderTool


def test_tool_manager_executes_registered_tool(tmp_path) -> None:
    manager = ToolManager()
    manager.register(CreateFolderTool(FilesystemService()))

    result = manager.execute("create_folder", {"path": str(tmp_path / "created")})

    assert result.ok
    assert (tmp_path / "created").is_dir()


def test_tool_manager_permission_hook_denies_dangerous_tool(tmp_path) -> None:
    def deny(tool, arguments) -> None:
        if tool.spec.dangerous:
            raise PermissionDeniedError("blocked")

    manager = ToolManager(permission_hooks=[deny])
    manager.register(DeleteFolderTool(FilesystemService()))

    result = manager.execute("delete_folder", {"path": str(tmp_path)})

    assert not result.ok
    assert result.status == "denied"
