"""In-memory conversation memory."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MessageRole(StrEnum):
    """Conversation roles."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass(frozen=True)
class MemoryMessage:
    """A single conversation message."""

    role: MessageRole
    content: str


class ConversationMemory:
    """Bounded conversation memory with a future persistence boundary."""

    def __init__(self, *, limit: int) -> None:
        self._limit = limit
        self._messages: list[MemoryMessage] = []

    def add(self, role: MessageRole, content: str) -> None:
        """Append a message and trim old history."""

        self._messages.append(MemoryMessage(role=role, content=content))
        if len(self._messages) > self._limit:
            self._messages = self._messages[-self._limit :]

    def add_user(self, content: str) -> None:
        """Append a user message."""

        self.add(MessageRole.USER, content)

    def add_assistant(self, content: str) -> None:
        """Append an assistant message."""

        self.add(MessageRole.ASSISTANT, content)

    def messages(self) -> list[MemoryMessage]:
        """Return a copy of the current memory."""

        return list(self._messages)

    def clear(self) -> None:
        """Clear all memory."""

        self._messages.clear()
