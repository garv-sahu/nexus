"""Model-assisted decision gate for tool use."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolDecision:
    """Decision returned before tool execution."""

    mode: str
    reason: str = ""
    question: str = ""
    action: str = ""
    arguments: dict[str, Any] | None = None


class ToolDecider:
    """Ask the existing LLM whether to use tools, chat, or clarify."""

    def __init__(self, llm) -> None:
        self._llm = llm

    def decide(self, user_input: str) -> ToolDecision:
        """Return a conservative tool-use decision."""

        prompt = f"""
Decide whether the assistant should use local/browser tools before answering.
Return only JSON.

Rules:
- Use "tool" for clear browser actions: open a named site, search, summarize
  page, extract page data, click elements, fill web forms, or take screenshots.
- Use "clarify" for vague action requests where the target is missing, such as
  "open any cool website" or "open something interesting".
- Use "chat" for normal questions or conversation.
- Specific site names and short forms are clear targets: twitch, instagram, ig,
  yt, youtube, gh, github, gmail, reddit, spotify, etc.
- Clean the user's intent before choosing arguments. For example:
  "search me sites to watch f1" means action "search" with query
  "sites to watch f1", not "me sites to watch f1".
- If the user says "open twitch", use action "open_url" with url "twitch".
- If the user says "search f1 highlights on youtube", use action "search" with
  engine "youtube" and query "f1 highlights".
- Local filesystem actions are not available. If the user asks to create, open,
  read, write, delete, index, or search local files/folders, use "chat" and
  explain that local file actions are disabled.

Schema:
{{
  "mode":"tool|chat|clarify",
  "action":"open_url|search|summarize|extract|screenshot|click|fill|status",
  "arguments":{{}},
  "reason":"short reason",
  "question":"question if clarify"
}}

User:
{user_input}
"""
        try:
            raw = self._llm.generate(prompt).strip()
            data = json.loads(strip_code_fence(raw))
            mode = str(data.get("mode", "")).lower()
            if mode not in {"tool", "chat", "clarify"}:
                return ToolDecision("auto", "model returned an unknown mode")
            return ToolDecision(
                mode=mode,
                reason=str(data.get("reason", "")),
                question=str(data.get("question", "")),
                action=str(data.get("action", "")),
                arguments=data.get("arguments") if isinstance(data.get("arguments"), dict) else {},
            )
        except Exception as exc:
            return ToolDecision("auto", f"decision failed: {type(exc).__name__}: {exc}")


def strip_code_fence(value: str) -> str:
    """Remove Markdown code fences around JSON if the model adds them."""

    cleaned = value.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned
