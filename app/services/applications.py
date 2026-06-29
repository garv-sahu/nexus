"""Windows application service."""

from __future__ import annotations

import os
import subprocess

from app.core.exceptions import ServiceError


class ApplicationService:
    """Open and close applications through Windows shell commands."""

    def open_application(self, target: str) -> str:
        try:
            os.startfile(target)  # type: ignore[attr-defined]
        except OSError as exc:
            raise ServiceError(f"Could not open application: {target}") from exc
        return target

    def close_application(self, process_name: str) -> str:
        image_name = process_name
        if not image_name.lower().endswith(".exe"):
            image_name = f"{image_name}.exe"

        completed = subprocess.run(
            ["taskkill", "/IM", image_name, "/F"],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip()
            raise ServiceError(f"Could not close {image_name}: {message}")
        return image_name
