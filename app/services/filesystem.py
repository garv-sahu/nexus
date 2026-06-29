"""Filesystem service containing all filesystem OS interactions."""

from __future__ import annotations

import shutil
from pathlib import Path

from app.core.exceptions import ServiceError
from app.utils.paths import expand_path


class FilesystemService:
    """Perform filesystem operations using pathlib and shutil."""

    def create_folder(self, path: str) -> Path:
        target = expand_path(path)
        target.mkdir(parents=True, exist_ok=True)
        return target

    def delete_folder(self, path: str) -> Path:
        target = expand_path(path)
        if not target.exists():
            raise ServiceError(f"Folder does not exist: {target}")
        if not target.is_dir():
            raise ServiceError(f"Path is not a folder: {target}")
        shutil.rmtree(target)
        return target

    def copy(self, source: str, destination: str) -> Path:
        src = expand_path(source)
        dst = expand_path(destination)
        if not src.exists():
            raise ServiceError(f"Source does not exist: {src}")
        if src.is_dir():
            if dst.exists() and dst.is_file():
                raise ServiceError(f"Destination is a file: {dst}")
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            if dst.exists() and dst.is_dir():
                dst = dst / src.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        return dst

    def move(self, source: str, destination: str) -> Path:
        src = expand_path(source)
        dst = expand_path(destination)
        if not src.exists():
            raise ServiceError(f"Source does not exist: {src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return dst

    def rename(self, source: str, new_name: str) -> Path:
        src = expand_path(source)
        if not src.exists():
            raise ServiceError(f"Source does not exist: {src}")
        dst = src.with_name(new_name)
        src.rename(dst)
        return dst

    def search(self, root: str, pattern: str, *, limit: int = 50) -> list[Path]:
        search_root = expand_path(root)
        if not search_root.exists():
            raise ServiceError(f"Search root does not exist: {search_root}")
        if not search_root.is_dir():
            raise ServiceError(f"Search root is not a folder: {search_root}")
        matches: list[Path] = []
        for path in search_root.rglob(pattern):
            matches.append(path)
            if len(matches) >= limit:
                break
        return matches

    def read_text(self, path: str, *, encoding: str = "utf-8") -> str:
        target = expand_path(path)
        if not target.exists():
            raise ServiceError(f"File does not exist: {target}")
        if not target.is_file():
            raise ServiceError(f"Path is not a file: {target}")
        return target.read_text(encoding=encoding)
