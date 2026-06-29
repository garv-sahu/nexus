"""Browser service for web navigation and searches."""

from __future__ import annotations

import webbrowser
from urllib.parse import quote_plus


class BrowserService:
    """Open URLs and search providers in the default browser."""

    def open_url(self, url: str) -> str:
        webbrowser.open(url)
        return url

    def google_search(self, query: str) -> str:
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        return self.open_url(url)

    def youtube_search(self, query: str) -> str:
        url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        return self.open_url(url)

    def github_search(self, query: str) -> str:
        url = f"https://github.com/search?q={quote_plus(query)}"
        return self.open_url(url)
