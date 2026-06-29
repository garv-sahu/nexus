"""Media service using Windows virtual key media controls."""

from __future__ import annotations

import ctypes
from enum import IntEnum


class MediaVirtualKey(IntEnum):
    """Windows media virtual key codes."""

    PLAY_PAUSE = 0xB3
    NEXT_TRACK = 0xB0
    PREVIOUS_TRACK = 0xB1
    VOLUME_MUTE = 0xAD
    VOLUME_DOWN = 0xAE
    VOLUME_UP = 0xAF


class MediaService:
    """Send media key events to Windows."""

    _KEYEVENTF_KEYUP = 0x0002

    def press(self, key: MediaVirtualKey) -> str:
        ctypes.windll.user32.keybd_event(key, 0, 0, 0)  # type: ignore[attr-defined]
        ctypes.windll.user32.keybd_event(  # type: ignore[attr-defined]
            key,
            0,
            self._KEYEVENTF_KEYUP,
            0,
        )
        return key.name.lower()
