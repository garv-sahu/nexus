"""Small reusable helper functions."""

from __future__ import annotations

import json
from typing import Any


def compact_json(data: Any) -> str:
    """Serialize data for prompts and logs."""

    return json.dumps(data, ensure_ascii=True, separators=(",", ":"))


def first_non_empty(*values: str | None) -> str | None:
    """Return the first string that contains non-whitespace content."""

    for value in values:
        if value and value.strip():
            return value.strip()
    return None
