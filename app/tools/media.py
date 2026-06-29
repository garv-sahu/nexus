"""Media tool adapters."""

from __future__ import annotations

from typing import Any

from app.core.base_tool import BaseTool, ToolCategory, ToolSpec
from app.core.result import ToolResult
from app.services.media import MediaService, MediaVirtualKey


class MediaControlTool(BaseTool):
    """Control playback and volume through media keys."""

    spec = ToolSpec(
        name="media_control",
        description="Control media playback and volume.",
        category=ToolCategory.MEDIA,
        parameters={
            "action": "play_pause, next, previous, mute, volume_up, or volume_down.",
        },
    )

    _ACTION_MAP = {
        "play_pause": MediaVirtualKey.PLAY_PAUSE,
        "pause": MediaVirtualKey.PLAY_PAUSE,
        "play": MediaVirtualKey.PLAY_PAUSE,
        "next": MediaVirtualKey.NEXT_TRACK,
        "previous": MediaVirtualKey.PREVIOUS_TRACK,
        "prev": MediaVirtualKey.PREVIOUS_TRACK,
        "mute": MediaVirtualKey.VOLUME_MUTE,
        "volume_up": MediaVirtualKey.VOLUME_UP,
        "volume_down": MediaVirtualKey.VOLUME_DOWN,
    }

    def __init__(self, service: MediaService) -> None:
        self._service = service

    def run(self, **kwargs: Any) -> ToolResult:
        action = str(kwargs["action"]).strip().lower().replace(" ", "_")
        key = self._ACTION_MAP[action]
        result = self._service.press(key)
        return ToolResult.success(self.name, f"Media action sent: {action}", {"action": result})
