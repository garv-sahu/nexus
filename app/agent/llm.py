"""LLM abstractions and Ollama implementation.

This is the only module that knows Ollama exists.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.exceptions import LLMError


@dataclass(frozen=True)
class LLMMessage:
    """A provider-agnostic chat message."""

    role: str
    content: str


@dataclass(frozen=True)
class LLMResponse:
    """A provider-agnostic chat response."""

    content: str
    model: str
    raw: dict[str, Any]


class LLMClient(ABC):
    """Abstract LLM interface used by the rest of the application."""

    @abstractmethod
    def chat(
        self,
        messages: Iterable[LLMMessage],
        *,
        system_prompt: str | None = None,
    ) -> LLMResponse:
        """Return a complete assistant response."""

    @abstractmethod
    def stream_chat(
        self,
        messages: Iterable[LLMMessage],
        *,
        system_prompt: str | None = None,
    ) -> Iterator[str]:
        """Yield assistant response chunks."""


class OllamaLLMClient(LLMClient):
    """Reusable chat client for a local model provider."""

    def __init__(
        self,
        *,
        host: str,
        model: str,
        timeout_seconds: int,
        logger: logging.Logger | None = None,
    ) -> None:
        self._host = host.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._logger = logger or logging.getLogger(__name__)

    @property
    def model(self) -> str:
        """Return the configured model name."""

        return self._model

    def chat(
        self,
        messages: Iterable[LLMMessage],
        *,
        system_prompt: str | None = None,
    ) -> LLMResponse:
        """Return a complete model response."""

        payload = self._payload(messages, system_prompt=system_prompt, stream=False)
        raw = self._post_json("/api/chat", payload)
        content = raw.get("message", {}).get("content", "")
        return LLMResponse(content=content, model=self._model, raw=raw)

    def stream_chat(
        self,
        messages: Iterable[LLMMessage],
        *,
        system_prompt: str | None = None,
    ) -> Iterator[str]:
        """Yield model response chunks from a streaming chat call."""

        payload = self._payload(messages, system_prompt=system_prompt, stream=True)
        request = self._request("/api/chat", payload)
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                for line in response:
                    if not line.strip():
                        continue
                    data = json.loads(line.decode("utf-8"))
                    message = data.get("message", {})
                    chunk = message.get("content", "")
                    if chunk:
                        yield chunk
                    if data.get("done"):
                        break
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            self._logger.exception("Streaming LLM call failed")
            raise LLMError(f"LLM streaming call failed: {exc}") from exc

    def _payload(
        self,
        messages: Iterable[LLMMessage],
        *,
        system_prompt: str | None,
        stream: bool,
    ) -> dict[str, Any]:
        rendered_messages = []
        if system_prompt:
            rendered_messages.append({"role": "system", "content": system_prompt})
        rendered_messages.extend(
            {"role": message.role, "content": message.content}
            for message in messages
            if message.content.strip()
        )
        return {
            "model": self._model,
            "messages": rendered_messages,
            "stream": stream,
        }

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = self._request(path, payload)
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            self._logger.exception("LLM call failed")
            raise LLMError(f"LLM call failed: {exc}") from exc

    def _request(self, path: str, payload: dict[str, Any]) -> Request:
        body = json.dumps(payload).encode("utf-8")
        return Request(
            f"{self._host}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
