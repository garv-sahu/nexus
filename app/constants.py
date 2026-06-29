"""Application-wide constants."""

from pathlib import Path

APP_NAME = "Nexus"
APP_DESCRIPTION = "A local AI desktop agent for Windows automation."
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen3-coder"
DEFAULT_REQUEST_TIMEOUT_SECONDS = 120
DEFAULT_TERMINAL_TIMEOUT_SECONDS = 30

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "nexus.log"

DEFAULT_MEMORY_LIMIT = 20
