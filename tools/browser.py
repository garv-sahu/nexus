"""Browser features for the Nexus web agent.

The basic features use the standard library and work immediately:
open URLs, search supported engines, fetch pages, extract content, and summarize.

Interactive automation features such as screenshot, click, and fill use
Playwright when it is installed. They return structured failures with setup
guidance instead of pretending the action succeeded.
"""

from __future__ import annotations

import json
import re
import time
import webbrowser
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen


SEARCH_ENGINES: dict[str, str] = {
    "google": "https://www.google.com/search?q={query}",
    "web": "https://www.google.com/search?q={query}",
    "youtube": "https://www.youtube.com/results?search_query={query}",
    "spotify": "https://open.spotify.com/search/{query}",
    "github": "https://github.com/search?q={query}",
    "reddit": "https://www.reddit.com/search/?q={query}",
    "stackoverflow": "https://stackoverflow.com/search?q={query}",
    "stack overflow": "https://stackoverflow.com/search?q={query}",
    "amazon": "https://www.amazon.com/s?k={query}",
    "flipkart": "https://www.flipkart.com/search?q={query}",
    "bing": "https://www.bing.com/search?q={query}",
    "duckduckgo": "https://duckduckgo.com/?q={query}",
    "duck duck go": "https://duckduckgo.com/?q={query}",
    "maps": "https://www.google.com/maps/search/{query}",
    "google maps": "https://www.google.com/maps/search/{query}",
}

SITE_ALIASES: dict[str, str] = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "spotify": "https://open.spotify.com",
    "github": "https://github.com",
    "reddit": "https://www.reddit.com",
    "stackoverflow": "https://stackoverflow.com",
    "stack overflow": "https://stackoverflow.com",
    "amazon": "https://www.amazon.com",
    "flipkart": "https://www.flipkart.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
    "duck duck go": "https://duckduckgo.com",
    "maps": "https://www.google.com/maps",
    "google maps": "https://www.google.com/maps",
}


@dataclass
class BrowserState:
    """Small in-memory browser state for follow-up commands."""

    current_url: str | None = None
    last_html: str | None = None
    last_text: str | None = None
    last_title: str | None = None


class BrowserTool:
    """Generic web browser and web-page utility tool."""

    def __init__(self) -> None:
        self.state = BrowserState()
        self._playwright: Any = None
        self._browser: Any = None
        self._page: Any = None

    def open_url(self, url: str) -> dict[str, Any]:
        """Open a URL in the default browser."""

        started = time.perf_counter()
        try:
            normalized = normalize_url(url)
            opened = webbrowser.open(normalized)
            self.state.current_url = normalized
            return success(
                "Opened URL.",
                {
                    "url": normalized,
                    "opened": opened,
                    "elapsed_seconds": elapsed(started),
                },
            )
        except Exception as exc:
            return failure("Could not open URL.", exc, {"input": url, "elapsed_seconds": elapsed(started)})

    def search(self, query: str, engine: str = "google") -> dict[str, Any]:
        """Search a supported engine and open the result page."""

        started = time.perf_counter()
        try:
            search_query = require_text(query, "query")
            engine_key = normalize_engine(engine)
            template = SEARCH_ENGINES.get(engine_key)
            if template is None:
                return error_response(
                    "Unsupported search engine.",
                    f"Supported engines: {', '.join(sorted(SEARCH_ENGINES))}",
                    {"engine": engine, "query": search_query},
                )
            encoded_query = quote_plus(search_query)
            url = template.format(query=encoded_query)
            result = self.open_url(url)
            result["message"] = "Opened search results."
            result["data"].update(
                {
                    "engine": engine_key,
                    "query": search_query,
                    "url": url,
                    "elapsed_seconds": elapsed(started),
                }
            )
            return result
        except Exception as exc:
            return failure("Could not search the web.", exc, {"engine": engine, "query": query})

    def fetch(self, url: str | None = None) -> dict[str, Any]:
        """Fetch a web page into memory for summarize/extract operations."""

        started = time.perf_counter()
        target = url or self.state.current_url
        if not target:
            return error_response("No page selected.", "Open a URL or provide a URL first.")
        try:
            normalized = normalize_url(target)
            html = fetch_html(normalized)
            parser = PageParser()
            parser.feed(html)
            text = clean_text(" ".join(parser.text_parts))
            self.state.current_url = normalized
            self.state.last_html = html
            self.state.last_text = text
            self.state.last_title = parser.title
            return success(
                "Fetched page.",
                {
                    "url": normalized,
                    "title": parser.title,
                    "text_preview": text[:1000],
                    "text_length": len(text),
                    "links": parser.links[:50],
                    "headings": parser.headings[:50],
                    "elapsed_seconds": elapsed(started),
                },
            )
        except Exception as exc:
            return failure("Could not fetch page.", exc, {"url": target, "elapsed_seconds": elapsed(started)})

    def summarize(self, url: str | None = None, max_sentences: int = 5) -> dict[str, Any]:
        """Summarize the current page or a supplied URL."""

        page = self.fetch(url)
        if not page["success"]:
            return page
        text = self.state.last_text or ""
        sentences = split_sentences(text)
        summary = " ".join(sentences[: max(1, max_sentences)])
        return success(
            "Summarized page.",
            {
                "url": self.state.current_url,
                "title": self.state.last_title,
                "summary": summary or "No readable text was found on the page.",
                "sentence_count": len(sentences),
            },
        )

    def extract(self, kind: str = "text", url: str | None = None) -> dict[str, Any]:
        """Extract text, links, headings, emails, or phone-like values."""

        page = self.fetch(url)
        if not page["success"]:
            return page
        html = self.state.last_html or ""
        text = self.state.last_text or ""
        parser = PageParser()
        parser.feed(html)
        kind_key = kind.strip().lower()
        if kind_key in {"text", "content"}:
            data = {"text": text}
        elif kind_key == "links":
            data = {"links": parser.links}
        elif kind_key == "headings":
            data = {"headings": parser.headings}
        elif kind_key == "emails":
            data = {"emails": sorted(set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)))}
        elif kind_key in {"phones", "phone"}:
            data = {"phones": sorted(set(re.findall(r"(?:\+?\d[\d\s().-]{7,}\d)", text)))}
        else:
            return error_response(
                "Unsupported extraction type.",
                "Use one of: text, links, headings, emails, phones.",
                {"kind": kind},
            )
        data.update({"url": self.state.current_url, "title": self.state.last_title})
        return success("Extracted page data.", data)

    def screenshot(self, url: str | None = None, output_dir: str = "screenshots") -> dict[str, Any]:
        """Take a page screenshot using Playwright when available."""

        started = time.perf_counter()
        target = url or self.state.current_url
        if not target:
            return error_response("No page selected.", "Open a URL or provide a URL first.")
        try:
            page = self._ensure_page()
            page.goto(normalize_url(target), wait_until="domcontentloaded")
            folder = Path(output_dir).expanduser().resolve()
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / f"nexus-{int(time.time())}.png"
            page.screenshot(path=str(path), full_page=True)
            self.state.current_url = page.url
            return success(
                "Captured screenshot.",
                {"url": page.url, "path": str(path), "elapsed_seconds": elapsed(started)},
            )
        except Exception as exc:
            return failure("Could not capture screenshot.", exc, {"url": target})

    def click(self, selector_or_text: str) -> dict[str, Any]:
        """Click an element by CSS selector or visible text using Playwright."""

        started = time.perf_counter()
        try:
            page = self._ensure_page(require_page=True)
            target = require_text(selector_or_text, "selector_or_text")
            if target.startswith((".", "#", "[", "button", "a", "input")):
                page.click(target)
            else:
                page.get_by_text(target, exact=False).click()
            return success("Clicked element.", {"target": target, "url": page.url, "elapsed_seconds": elapsed(started)})
        except Exception as exc:
            return failure("Could not click element.", exc, {"target": selector_or_text})

    def fill(self, selector_or_label: str, value: str) -> dict[str, Any]:
        """Fill an input by CSS selector or label using Playwright."""

        started = time.perf_counter()
        try:
            page = self._ensure_page(require_page=True)
            target = require_text(selector_or_label, "selector_or_label")
            text = str(value)
            if target.startswith((".", "#", "[", "input", "textarea")):
                page.fill(target, text)
            else:
                page.get_by_label(target, exact=False).fill(text)
            return success("Filled field.", {"target": target, "url": page.url, "elapsed_seconds": elapsed(started)})
        except Exception as exc:
            return failure("Could not fill field.", exc, {"target": selector_or_label})

    def status(self) -> dict[str, Any]:
        """Return current browser tool status."""

        return success(
            "Browser status.",
            {
                "current_url": self.state.current_url,
                "has_fetched_page": self.state.last_html is not None,
                "playwright_available": is_playwright_available(),
                "supported_search_engines": sorted(SEARCH_ENGINES),
            },
        )

    def _ensure_page(self, require_page: bool = False) -> Any:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError(
                "Playwright is required for screenshots, clicks, and form filling. "
                "Install it with `pip install playwright` and then run `playwright install chromium`."
            ) from exc

        if self._playwright is None:
            self._playwright = sync_playwright().start()
        if self._browser is None:
            self._browser = self._playwright.chromium.launch(headless=False)
        if self._page is None:
            self._page = self._browser.new_page()
        if require_page and self._page.url == "about:blank" and self.state.current_url:
            self._page.goto(self.state.current_url, wait_until="domcontentloaded")
        return self._page


class PageParser(HTMLParser):
    """Small HTML parser for readable text, links, headings, and titles."""

    def __init__(self) -> None:
        super().__init__()
        self.text_parts: list[str] = []
        self.links: list[dict[str, str]] = []
        self.headings: list[dict[str, str]] = []
        self.title: str | None = None
        self._skip_depth = 0
        self._current_link: str | None = None
        self._current_heading: str | None = None
        self._heading_text: list[str] = []
        self._in_title = False
        self._title_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        if tag == "a" and attrs_dict.get("href"):
            self._current_link = attrs_dict["href"]
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._current_heading = tag
            self._heading_text = []
        if tag == "title":
            self._in_title = True
            self._title_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "a":
            self._current_link = None
        if tag == self._current_heading:
            text = clean_text(" ".join(self._heading_text))
            if text:
                self.headings.append({"level": tag, "text": text})
            self._current_heading = None
            self._heading_text = []
        if tag == "title":
            self._in_title = False
            self.title = clean_text(" ".join(self._title_text)) or None

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = clean_text(data)
        if not text:
            return
        self.text_parts.append(text)
        if self._current_link:
            self.links.append({"text": text, "href": self._current_link})
        if self._current_heading:
            self._heading_text.append(text)
        if self._in_title:
            self._title_text.append(text)


def fetch_html(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
            )
        },
    )
    try:
        with urlopen(request, timeout=15) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(str(exc)) from exc


def normalize_url(value: str) -> str:
    text = require_text(value, "url").strip()
    alias = SITE_ALIASES.get(" ".join(text.lower().split()))
    if alias:
        return alias
    parsed = urlparse(text)
    if not parsed.scheme:
        text = f"https://{text}"
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http and https URLs are supported.")
    return text


def normalize_engine(engine: str) -> str:
    return " ".join(require_text(engine, "engine").lower().replace("_", " ").split())


def require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required.")
    return value.strip()


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]


def is_playwright_available() -> bool:
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        return False
    return True


def elapsed(started: float) -> float:
    return round(time.perf_counter() - started, 3)


def success(message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"success": True, "message": message, "data": data or {}}


def error_response(message: str, error: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"success": False, "message": message, "error": error, "data": data or {}}


def failure(message: str, exc: BaseException, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return error_response(message, f"{type(exc).__name__}: {exc}", data)


def to_markdown(result: dict[str, Any]) -> str:
    """Render a browser result for the chat stream."""

    status = "Done" if result.get("success") else "Failed"
    lines = [f"**{status}:** {result.get('message', '')}".strip()]
    if result.get("error"):
        lines.append(f"Error: {result['error']}")
    data = result.get("data") or {}
    for key in ("url", "title", "summary", "path", "engine", "query"):
        if data.get(key):
            lines.append(f"- `{key}`: {data[key]}")
    if "links" in data:
        links = data["links"][:10]
        lines.append(f"- `links`: {len(data['links'])} found")
        lines.extend(f"  - [{item.get('text') or item.get('href')}]({item.get('href')})" for item in links)
    if "headings" in data:
        lines.append(f"- `headings`: {len(data['headings'])} found")
        lines.extend(f"  - {item['level']}: {item['text']}" for item in data["headings"][:10])
    if "text" in data:
        preview = data["text"][:1500]
        lines.append(f"\n```text\n{preview}\n```")
    if len(data) and not any(key in data for key in ("url", "title", "summary", "path", "links", "headings", "text")):
        lines.append(f"\n```json\n{json.dumps(data, indent=2, ensure_ascii=True)}\n```")
    return "\n".join(lines)
