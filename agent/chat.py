import re

from .planner import Planner
from .llm import LLM
from .memory import Memory
from .browser_router import BrowserIntent, BrowserRouter
from .tool_decider import ToolDecider
from tools.browser import BrowserTool
from tools.browser import to_markdown as browser_to_markdown

class Nexus:
    def __init__(self):
        self.memory = Memory()
        self.planner = Planner()
        self.llm = LLM()
        self.browser = BrowserTool()
        self.browser_router = BrowserRouter(self.browser)
        self.tool_decider = ToolDecider(self.llm)

    def set_model(self, model):
        self.llm.set_model(model)

    def get_model(self):
        return self.llm.get_model()

    def chat(self, user_input):
        self.memory.add("user", user_input)

        decision = self.tool_decider.decide(user_input)
        if decision.mode == "clarify":
            browser_intent = self.browser_router.parse(user_input)
            should_clarify = (
                browser_intent is None
                or browser_intent.action == "clarify"
            )
            if should_clarify:
                response = decision.question or "What exactly do you want me to open or do?"
                self.memory.add("assistant", response)
                return response
        if decision.mode == "chat" and not looks_like_action_request(user_input):
            prompt = self.planner.build_prompt(
                self.memory,
                user_input
            )
            response = self.llm.generate(prompt)
            self.memory.add("assistant", response)
            return response

        browser_intent = self._intent_from_decision(decision) or self.browser_router.parse(user_input)
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

    def _intent_from_decision(self, decision):
        if decision.mode != "tool" or not decision.action:
            return None
        allowed_actions = {
            "open_url",
            "search",
            "summarize",
            "extract",
            "screenshot",
            "click",
            "fill",
            "status",
        }
        if decision.action not in allowed_actions:
            return None
        arguments = decision.arguments or {}
        if decision.action == "search":
            query = arguments.get("query")
            if not query:
                return None
            return BrowserIntent(
                "search",
                {
                    "query": clean_search_query(str(query)),
                    "engine": arguments.get("engine", "google"),
                },
            )
        if decision.action == "open_url" and not arguments.get("url"):
            return None
        return BrowserIntent(decision.action, arguments)

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


def looks_like_action_request(user_input):
    lowered = user_input.strip().lower()
    return lowered.startswith((
        "open ",
        "go to ",
        "navigate to ",
        "search ",
        "find ",
        "look up ",
        "play ",
        "summarize ",
        "summarise ",
        "extract ",
        "click ",
        "fill ",
    ))


def clean_search_query(query):
    cleaned = query.strip()
    cleaned = re.sub(r"^(?:me|for me|please|pls)\s+", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s+(?:for me|please|pls)$", "", cleaned, flags=re.I)
    return cleaned.strip()
