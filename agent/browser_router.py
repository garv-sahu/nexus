"""Intent routing for browser commands."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from tools.browser import (
    SEARCH_ENGINES,
    BrowserTool,
    can_open_without_clarification,
    is_ambiguous_open_target,
    to_markdown,
)


@dataclass(frozen=True)
class BrowserIntent:
    """A parsed browser action."""

    action: str
    arguments: dict[str, Any]


class BrowserRouter:
    """Parse common natural-language browser requests into browser tool calls."""

    def __init__(self, browser: BrowserTool) -> None:
        self._browser = browser

    def handle(self, user_input: str) -> str | None:
        """Execute a browser command if the input is recognized."""

        intent = self.parse(user_input)
        if intent is None:
            return None
        result = self.execute(intent)
        return to_markdown(result)

    def parse(self, user_input: str) -> BrowserIntent | None:
        """Parse the user's request into a browser intent."""

        text = user_input.strip()
        lowered = text.lower()

        if lowered in {"browser status", "web status", "status browser"}:
            return BrowserIntent("status", {})

        screenshot_match = re.search(r"(?:take\s+a\s+)?screenshot(?:\s+of)?\s+(.+)?", text, re.I)
        if screenshot_match and "screenshot" in lowered:
            target = clean_optional(screenshot_match.group(1))
            return BrowserIntent("screenshot", {"url": target})

        summarize_match = re.search(r"summar(?:ize|ise)(?:\s+(?:the\s+)?(?:current\s+)?page)?(?:\s+(.+))?", text, re.I)
        if summarize_match and ("summarize" in lowered or "summarise" in lowered):
            target = clean_optional(summarize_match.group(1))
            return BrowserIntent("summarize", {"url": target})

        extract_match = re.search(
            r"extract(?:\s+all)?\s+(links|headings|emails|phones|phone|text|content)(?:\s+(?:from|of)\s+(.+))?",
            text,
            re.I,
        )
        if extract_match:
            return BrowserIntent(
                "extract",
                {
                    "kind": extract_match.group(1).lower(),
                    "url": clean_optional(extract_match.group(2)),
                },
            )

        click_match = re.search(r"click(?:\s+on)?\s+(.+)", text, re.I)
        if click_match and lowered.startswith("click"):
            return BrowserIntent("click", {"selector_or_text": click_match.group(1).strip()})

        fill_match = re.search(r"fill\s+(.+?)\s+with\s+(.+)", text, re.I)
        if fill_match:
            return BrowserIntent(
                "fill",
                {
                    "selector_or_label": fill_match.group(1).strip(),
                    "value": fill_match.group(2).strip(),
                },
            )

        open_match = re.search(r"^(?:open|go\s+to|navigate\s+to)\s+(.+)$", text, re.I)
        if open_match:
            target = open_match.group(1).strip()
            if looks_like_search_request(target):
                engine, query = extract_engine_and_query(target)
                return BrowserIntent("search", {"query": query, "engine": engine})
            if is_ambiguous_open_target(target):
                return BrowserIntent(
                    "clarify",
                    {
                        "target": target,
                        "question": (
                            "Do you want me to open a specific website, search the web, "
                            "or summarize the current page? For example: `open instagram`, "
                            "`search cool websites`, or `summarize this page`."
                        ),
                    },
                )
            if not can_open_without_clarification(target):
                return BrowserIntent("search", {"query": strip_search_words(target), "engine": "google"})
            return BrowserIntent("open_url", {"url": target})

        search_match = re.search(r"^search(?:\s+(?:the\s+web|online))?(?:\s+for)?\s+(.+)$", text, re.I)
        if search_match is None:
            search_match = re.search(r"^(?:find|look\s+up)\s+(?:the\s+web|online|on\s+the\s+web)(?:\s+for)?\s+(.+)$", text, re.I)
        if search_match:
            query_text = search_match.group(1).strip()
            engine, query = extract_engine_and_query(query_text)
            return BrowserIntent("search", {"query": query, "engine": engine})

        engine, media_query = parse_media_search(text)
        if engine and media_query:
            return BrowserIntent("search", {"query": media_query, "engine": engine})

        return None

    def execute(self, intent: BrowserIntent) -> dict[str, Any]:
        """Execute a parsed browser intent."""

        if intent.action == "status":
            return self._browser.status()
        if intent.action == "open_url":
            return self._browser.open_url(intent.arguments["url"])
        if intent.action == "search":
            return self._browser.search(intent.arguments["query"], intent.arguments.get("engine", "google"))
        if intent.action == "summarize":
            return self._browser.summarize(intent.arguments.get("url"))
        if intent.action == "extract":
            return self._browser.extract(intent.arguments.get("kind", "text"), intent.arguments.get("url"))
        if intent.action == "screenshot":
            return self._browser.screenshot(intent.arguments.get("url"))
        if intent.action == "click":
            return self._browser.click(intent.arguments["selector_or_text"])
        if intent.action == "fill":
            return self._browser.fill(intent.arguments["selector_or_label"], intent.arguments["value"])
        if intent.action == "clarify":
            return {
                "success": False,
                "message": "I need a bit more detail before opening something.",
                "error": intent.arguments["question"],
                "data": {"target": intent.arguments.get("target")},
            }
        return {
            "success": False,
            "message": "Unsupported browser action.",
            "error": intent.action,
            "data": intent.arguments,
        }


def extract_engine_and_query(text: str) -> tuple[str, str]:
    """Extract a search engine hint from text."""

    lowered = text.lower()
    for engine in sorted(SEARCH_ENGINES, key=len, reverse=True):
        patterns = (
            rf"(.+)\s+on\s+{re.escape(engine)}$",
            rf"{re.escape(engine)}\s+(.+)$",
            rf"(.+)\s+in\s+{re.escape(engine)}$",
        )
        for pattern in patterns:
            match = re.search(pattern, lowered, re.I)
            if match:
                groups = [group for group in match.groups() if group]
                if groups:
                    query = groups[0].strip()
                    return engine, strip_search_words(query)
    return "google", strip_search_words(text)


def parse_media_search(text: str) -> tuple[str | None, str | None]:
    """Parse commands like 'play Believer on Spotify'."""

    match = re.search(r"^(?:play|listen\s+to)\s+(.+?)\s+on\s+(spotify|youtube)$", text, re.I)
    if match:
        return match.group(2).lower(), match.group(1).strip()
    return None, None


def looks_like_search_request(text: str) -> bool:
    lowered = text.lower()
    return any(f" on {engine}" in lowered for engine in SEARCH_ENGINES) or lowered.startswith(
        ("search ", "find online ", "find the web ", "find on the web ", "look up online ", "look up on the web ")
    )


def strip_search_words(text: str) -> str:
    cleaned = re.sub(r"^(?:search|find|look\s+up)(?:\s+for)?\s+", "", text.strip(), flags=re.I).strip()
    cleaned = re.sub(r"^(?:me|for me|please|pls)\s+", "", cleaned, flags=re.I).strip()
    cleaned = re.sub(r"\s+(?:for me|please|pls)$", "", cleaned, flags=re.I).strip()
    return cleaned


def clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned or cleaned.lower() in {"it", "this", "current page", "the current page"}:
        return None
    return cleaned