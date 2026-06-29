"""Path utility functions."""

from __future__ import annotations

from pathlib import Path


def expand_path(path: str | Path) -> Path:
    """Expand environment variables and user home markers in a path."""

    return Path(path).expanduser().resolve()


def ensure_parent(path: str | Path) -> Path:
    """Create the parent directory for a path and return the resolved path."""

    resolved = expand_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved
