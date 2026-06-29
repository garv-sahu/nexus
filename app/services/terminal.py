"""Terminal service for controlled shell command execution."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    """Result of a terminal command."""

    command: str
    return_code: int
    stdout: str
    stderr: str


class TerminalService:
    """Run terminal commands without exposing subprocess details elsewhere."""

    def run(self, command: str, *, timeout_seconds: int = 30) -> CommandResult:
        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return CommandResult(
            command=command,
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
