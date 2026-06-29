# Nexus

Nexus is a modular local AI desktop agent for Windows. It uses Ollama for language
model planning and keeps all operating system interaction behind service classes,
so the architecture can grow into MCP support without reshaping the application.

## Architecture

The project follows this flow:

```text
User
  -> DesktopAgent
  -> Planner
  -> Executor
  -> ToolManager
  -> Tool
  -> Service
  -> Operating System
```

Important boundaries:

- `app/agent/` contains AI orchestration, memory, planning, execution, prompts,
  and the LLM abstraction.
- `app/agent/llm.py` is the only module that communicates with Ollama.
- `app/core/` contains reusable framework infrastructure such as `BaseTool`,
  `ToolManager`, `ToolResult`, and custom exceptions.
- `app/tools/` contains thin tool adapters. Every tool wraps one service and
  inherits `BaseTool`.
- `app/services/` contains operating system implementations.
- `app/mcp/` is an intentional boundary for future MCP registry/server support.

## Requirements

- Windows
- Python 3.12+
- Ollama running locally
- A pulled Ollama model, for example:

```powershell
ollama pull qwen3-coder
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` if you want to keep local settings. Environment
variables are read directly by the app:

```powershell
$env:NEXUS_OLLAMA_MODEL = "qwen3-coder"
$env:NEXUS_OLLAMA_HOST = "http://localhost:11434"
```

## Run

Interactive mode:

```powershell
python run.py
```

One-shot prompt:

```powershell
python run.py "create folder C:\Temp\nexus-demo"
```

## Built-in Tools

Nexus includes tools for:

- Creating, deleting, copying, moving, renaming, searching, and reading files
- Opening URLs and searching Google, YouTube, and GitHub
- Opening and closing applications
- Running terminal commands
- Reading system information
- Sending media controls
- Shutdown and restart commands

Dangerous tools are blocked by default, including delete, close application,
terminal commands, shutdown, and restart. To enable them:

```powershell
$env:NEXUS_ALLOW_DANGEROUS_ACTIONS = "true"
```

## Development

Run tests:

```powershell
python -m pytest
```

Run linting:

```powershell
python -m ruff check .
```

## Design Notes

The planner returns strongly typed `Action` objects. The executor accepts those
actions and routes every call through `ToolManager`, where logging and permission
hooks are centralized. Services are the only layer that calls Windows APIs,
`subprocess`, filesystem functions, browser APIs, or media key events.
