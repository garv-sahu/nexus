from .planner import Planner
from .llm import LLM
from .memory import Memory
from .browser_router import BrowserRouter
from tools.browser import BrowserTool
from tools.browser import to_markdown as browser_to_markdown

class Nexus:
    def __init__(self):
        self.memory = Memory()
        self.planner = Planner()
        self.llm = LLM()
        self.browser = BrowserTool()
        self.browser_router = BrowserRouter(self.browser)

    def set_model(self, model):
        self.llm.set_model(model)

    def get_model(self):
        return self.llm.get_model()

    def chat(self, user_input):
        self.memory.add("user", user_input)

        browser_intent = self._explicit_browser_intent(user_input)
        if browser_intent is not None:
            browser_result = self.browser_router.execute(browser_intent)
            if browser_intent.action == "summarize" and browser_result.get("success"):
                response = self._answer_with_page_summary(user_input, browser_result)
            else:
                response = browser_to_markdown(browser_result)
            self.memory.add("assistant", response)
            return response

        prompt = self.planner.build_prompt(
            self.memory,
            user_input
        )

        response = self.llm.generate(prompt)

        self.memory.add("assistant", response)

        return response

    def _explicit_browser_intent(self, user_input):
        """Return a browser intent only for explicit browser/tool requests."""

        if not is_explicit_browser_request(user_input):
            return None
        intent = self.browser_router.parse(user_input)
        if intent is None:
            return None
        if intent.action == "clarify":
            return intent
        return intent

    def _answer_with_page_summary(self, user_input, summary_result):
        data = summary_result.get("data", {})
        content = data.get("content") or data.get("content_preview") or data.get("summary") or ""
        if len(content.strip()) < 120:
            return (
                "I could not extract enough readable page content to summarize properly. "
                "If this is a dynamic page, open it with browser automation/Playwright or provide the URL directly."
            )

        prompt = f"""
Summarize the web page using the extracted page content below.
Do not summarize only the title or meta description.
Give:
1. A concise overview
2. Key points
3. Important details or caveats

URL: {data.get("url")}
Title: {data.get("title")}

Extracted page content:
{content[:12000]}

User request:
{user_input}
"""
        return self.llm.generate(prompt)


def is_explicit_browser_request(user_input):
    lowered = user_input.strip().lower()
    if lowered in {"browser status", "web status", "status browser"}:
        return True
    if lowered.startswith((
        "open ",
        "go to ",
        "navigate to ",
        "search ",
        "play ",
        "click ",
        "fill ",
    )):
        return True
    explicit_phrases = (
        "search the web",
        "search online",
        "find online",
        "find on the web",
        "look up online",
        "look up on the web",
        "take a screenshot",
        "screenshot of",
    )
    if any(phrase in lowered for phrase in explicit_phrases):
        return True
    if lowered.startswith(("summarize ", "summarise ")):
        return refers_to_web_page(lowered)
    if lowered.startswith("extract "):
        return refers_to_web_page(lowered)
    return False


def refers_to_web_page(lowered):
    return (
        "http://" in lowered
        or "https://" in lowered
        or "www." in lowered
        or "current page" in lowered
        or "this page" in lowered
        or "web page" in lowered
        or "website" in lowered
        or " from page" in lowered
        or " from site" in lowered
    )