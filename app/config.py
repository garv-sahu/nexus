"""Runtime configuration for Nexus."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from app.constants import (
    DATA_DIR,
    DEFAULT_MEMORY_LIMIT,
    DEFAULT_OLLAMA_HOST,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
    DEFAULT_TERMINAL_TIMEOUT_SECONDS,
    LOG_DIR,
)


def _bool_from_env(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Immutable application settings loaded from environment variables."""

    ollama_host: str = DEFAULT_OLLAMA_HOST
    ollama_model: str = DEFAULT_OLLAMA_MODEL
    request_timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS
    terminal_timeout_seconds: int = DEFAULT_TERMINAL_TIMEOUT_SECONDS
    memory_limit: int = DEFAULT_MEMORY_LIMIT
    data_dir: Path = DATA_DIR
    log_dir: Path = LOG_DIR
    allow_dangerous_actions: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings from environment variables."""

        return cls(
            ollama_host=os.getenv("NEXUS_OLLAMA_HOST", DEFAULT_OLLAMA_HOST),
            ollama_model=os.getenv("NEXUS_OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
            request_timeout_seconds=int(
                os.getenv(
                    "NEXUS_REQUEST_TIMEOUT_SECONDS",
                    str(DEFAULT_REQUEST_TIMEOUT_SECONDS),
                )
            ),
            terminal_timeout_seconds=int(
                os.getenv(
                    "NEXUS_TERMINAL_TIMEOUT_SECONDS",
                    str(DEFAULT_TERMINAL_TIMEOUT_SECONDS),
                )
            ),
            memory_limit=int(os.getenv("NEXUS_MEMORY_LIMIT", str(DEFAULT_MEMORY_LIMIT))),
            data_dir=Path(os.getenv("NEXUS_DATA_DIR", str(DATA_DIR))).expanduser(),
            log_dir=Path(os.getenv("NEXUS_LOG_DIR", str(LOG_DIR))).expanduser(),
            allow_dangerous_actions=_bool_from_env(
                os.getenv("NEXUS_ALLOW_DANGEROUS_ACTIONS"),
                default=False,
            ),
        )


def load_settings() -> Settings:
    """Load settings and create runtime directories."""

    settings = Settings.from_env()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    return settings
