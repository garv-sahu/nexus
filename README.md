# Nexus

Nexus is a local web-agent UI backed by Flask and Ollama.

## Browser Features

The backend now implements real browser actions before falling back to normal
LLM conversation:

- Open URLs and websites
- Friendly site names like `open instagram`, `open github`, and `open gmail`
  resolve to real domains instead of broken URLs.
- Specific famous sites and short forms like `open twitch`, `open ig`,
  `open yt`, and `open gh` open directly.
- Vague requests like `open any cool website` ask a clarifying question instead
  of guessing.
- Nexus asks the model to decide whether a request should use tools, answer
  normally, or ask a clarification. Clear tool requests still have deterministic
  safeguards so simple site names are not blocked by over-cautious model output.
- Search Google, YouTube, Spotify, GitHub, Reddit, Stack Overflow, Amazon,
  Flipkart, Bing, DuckDuckGo, and Google Maps
- Fetch and summarize pages
- Extract page text, links, headings, emails, and phone numbers
- Report browser-tool status
- Take screenshots, click elements, and fill fields when Playwright is installed

## Tool Decisions

Before tool execution, Nexus asks the existing local model whether the request
should use a tool, answer normally, or ask for clarification. The Ollama/model
implementation itself is unchanged.

Local filesystem and local RAG actions are disabled. Nexus will not create,
open, edit, delete, index, or search local files/folders.

## Run

```powershell
pip install -r requirements.txt
playwright install chromium
python app.py
```

Ollama/model handling is unchanged and remains in `agent/llm.py`.
