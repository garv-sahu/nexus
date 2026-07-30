# NEXUS

NEXUS is a local-first AI web agent built for fast, natural interaction with the open web. It combines a polished chat interface, Ollama-powered local models, and deterministic browser tools so users can ask questions, open sites, search the web, summarize pages, and extract useful page data from one place.

Built for a GDG hackathon, NEXUS focuses on a simple idea: an assistant should not feel like a search box with extra steps. It should understand when to answer, when to use the web, and when to act on a browser command.

## Problem

Most AI assistants split the workflow across too many surfaces:

- Ask the model a question.
- Open a browser manually.
- Search Google.
- Copy links or page text back into chat.
- Ask the model to summarize or extract information.

NEXUS brings that loop into a single local interface. The user describes the outcome in plain language, and the backend decides whether to answer with the model or run a browser/web utility.

## Solution

NEXUS provides an LLM-first chat experience with explicit web actions:

- Normal questions are answered by the selected local Ollama model.
- Web search requests are answered directly inside NEXUS.
- Open commands launch specific websites.
- Page summarization works on URLs or previously opened pages.
- Data extraction pulls text, links, headings, emails, and phone-like values from readable pages.
- Model switching is available from the UI.

The command router is intentionally conservative. It only runs browser tools when the user clearly asks for a web or browser action, which keeps everyday chat predictable.

## Key Features

- Local AI chat powered by Ollama
- Flask backend with a single-page web UI
- Model picker with Ollama model discovery
- Intent routing for browser and web commands
- Direct in-app web search answers
- Website opening with friendly aliases like `open github`, `open gmail`, and `open youtube`
- Page fetching and summarization
- Structured page extraction for links, headings, text, emails, and phone numbers
- Browser status endpoint for frontend health checks
- Clean separation between chat, planning, routing, and browser utilities

## Demo Prompts

Try these after starting the app:

```text
What is DRS in Formula 1?
```

```text
Search the web for SF-26 performance
```

```text
Open github
```

```text
Summarize https://example.com
```

```text
Extract links from https://example.com
```

```text
Browser status
```

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Flask
- AI runtime: Ollama
- Language: Python
- Web utilities: Python standard library HTML parsing and URL handling

## Architecture

```text
User
  |
  v
NEXUS Web UI
  |
  v
Flask API
  |
  v
Nexus Chat Controller
  |
  +--> Planner + Ollama LLM
  |
  +--> Browser Router
          |
          +--> Open URL
          +--> Web Search Results
          +--> Fetch Page
          +--> Summarize Page
          +--> Extract Page Data
```

## Project Structure

```text
nexus/
  app.py                  Flask app and API routes
  requirements.txt        Python dependencies
  templates/
    index.html            NEXUS single-page interface
  agent/
    chat.py               Main chat controller
    llm.py                Ollama integration
    planner.py            Prompt construction
    browser_router.py     Browser intent parser and dispatcher
    memory.py             Conversation memory
    prompts.py            Shared prompt text
  tools/
    browser.py            URL opening, search, fetch, summarize, extract
```

## Setup

### 1. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 2. Start Ollama

Install and run Ollama, then pull a local model:

```powershell
ollama pull qwen3:8b
```

You can use any compatible local model available in Ollama. The active model is handled in `agent/llm.py` and can be switched from the UI when Ollama model discovery is available.

### 3. Run NEXUS

```powershell
python app.py
```

Open the app at:

```text
http://127.0.0.1:5000
```

## API Overview

### Chat

```http
POST /api/chat
```

Request:

```json
{
  "message": "Search the web for SF-26 performance"
}
```

Response:

```text
Plain text assistant response
```

### Models

```http
GET /api/models
POST /api/switch-model
```

### Browser Utilities

```http
GET /api/browser/status
POST /api/browser/action
```

Supported browser actions:

- `open_url`
- `search`
- `web_search_results`
- `fetch`
- `summarize`
- `extract`
- `status`

## How Intent Routing Works

NEXUS separates normal conversation from explicit browser commands.

Examples treated as normal chat:

```text
Explain how hybrid engines work in F1
Summarise race results for the Belgian 2026 Grand Prix
What are the pros and cons of local LLMs?
```

Examples treated as browser/web actions:

```text
Open youtube
Search the web for latest Android Studio features
Summarize this page
Extract headings from https://example.com
```

This prevents accidental browser launches and keeps the assistant predictable during demos.

## Hackathon Pitch

NEXUS demonstrates a practical pattern for local AI agents:

- Keep the model local for privacy and responsiveness.
- Use deterministic tools for actions.
- Route only explicit commands to tools.
- Keep search and page understanding inside the assistant experience.
- Make the UI feel like a command center, not a chatbot demo.

## Current Limitations

- Web search snippets depend on public search-result pages, which may be rate-limited or blocked by providers.
- Page summarization works best on static, readable HTML pages.
- Local file actions are intentionally disabled.
- Browser automation actions such as clicking, screenshots, and form filling are not part of the current command set.

## Future Scope

- Add provider-backed search APIs for more reliable live results.
- Add citations for web answers.
- Support persistent conversation history.
- Add agent task timelines in the UI.
- Add safe browser automation with user confirmation.
- Add deployment profiles for local, LAN, and cloud demos.

## Team Notes

This project is designed for hackathon demos where the evaluator should immediately understand:

- What the app does
- Why it is useful
- How to run it
- What to try first
- How the backend is structured

NEXUS is not just a wrapper around a model. It is a local AI interface with a real command-routing layer for web tasks.
