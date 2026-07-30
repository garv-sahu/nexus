# Nexus

Nexus is a local web-agent UI backed by Flask and Ollama.

## Browser Features

The backend now implements real browser actions before falling back to normal
LLM conversation:

- Open URLs and websites
- Search Google, YouTube, Spotify, GitHub, Reddit, Stack Overflow, Amazon,
  Flipkart, Bing, DuckDuckGo, and Google Maps
- Fetch and summarize pages
- Extract page text, links, headings, emails, and phone numbers
- Report browser-tool status
- Take screenshots, click elements, and fill fields when Playwright is installed

## Run

```powershell
pip install -r requirements.txt
playwright install chromium
python app.py
```

Ollama/model handling is unchanged and remains in `agent/llm.py`.
