"""Natural-language planning into typed actions."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from app.agent.llm import LLMClient, LLMMessage
from app.agent.memory import MemoryMessage
from app.agent.prompts import PLANNER_SYSTEM_PROMPT, render_tool_catalog
from app.core.base_tool import BaseTool
from app.core.exceptions import LLMError, PlanningError


@dataclass(frozen=True)
class Action:
    """A strongly typed executable action."""

    tool_name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    action_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class Plan:
    """A typed plan returned by the planner."""

    actions: list[Action]
    notes: str = ""


class Planner:
    """Convert natural language into strongly typed actions."""

    def __init__(
        self,
        llm: LLMClient,
        tools: list[BaseTool],
        *,
        logger: logging.Logger | None = None,
    ) -> None:
        self._llm = llm
        self._tools = tools
        self._tool_names = {tool.name for tool in tools}
        self._logger = logger or logging.getLogger(__name__)

    def plan(self, user_input: str, history: list[MemoryMessage]) -> Plan:
        """Create a plan for user input."""

        try:
            plan = self._plan_with_llm(user_input, history)
            if plan.actions:
                return plan
        except (LLMError, PlanningError) as exc:
            self._logger.warning("LLM planning failed, using fallback planner: %s", exc)
        return self._fallback_plan(user_input)

    def _plan_with_llm(self, user_input: str, history: list[MemoryMessage]) -> Plan:
        tool_catalog = render_tool_catalog(self._tools)
        messages = [
            LLMMessage(role=item.role.value, content=item.content)
            for item in history[-8:]
            if item.role.value in {"user", "assistant"}
        ]
        messages.append(
            LLMMessage(
                role="user",
                content=f"Available tools:\n{tool_catalog}\n\nUser request:\n{user_input}",
            )
        )
        response = self._llm.chat(messages, system_prompt=PLANNER_SYSTEM_PROMPT)
        return self._parse_plan(response.content)

    def _parse_plan(self, content: str) -> Plan:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise PlanningError(f"Planner returned invalid JSON: {content}") from exc

        actions: list[Action] = []
        for item in data.get("actions", []):
            tool_name = str(item.get("tool", "")).strip()
            if tool_name not in self._tool_names:
                raise PlanningError(f"Planner selected unknown tool: {tool_name}")
            arguments = item.get("arguments", {})
            if not isinstance(arguments, dict):
                raise PlanningError(f"Planner returned invalid arguments for {tool_name}")
            actions.append(Action(tool_name=tool_name, arguments=arguments))
        return Plan(actions=actions, notes=str(data.get("notes", "")))

    def _fallback_plan(self, user_input: str) -> Plan:
        text = user_input.strip()
        lowered = text.lower()

        if "system info" in lowered or "computer info" in lowered:
            return Plan([Action("system_info")])

        if "google" in lowered and "search" in lowered:
            return Plan([Action("google_search", {"query": self._query_after(text, "search")})])
        if "youtube" in lowered and "search" in lowered:
            return Plan([Action("youtube_search", {"query": self._query_after(text, "search")})])
        if "github" in lowered and "search" in lowered:
            return Plan([Action("github_search", {"query": self._query_after(text, "search")})])

        if lowered.startswith("open url "):
            return Plan([Action("open_url", {"url": text[9:].strip()})])
        if lowered.startswith("open "):
            return Plan([Action("open_application", {"target": text[5:].strip()})])

        if lowered.startswith("create folder "):
            return Plan([Action("create_folder", {"path": text[14:].strip().strip('"')})])
        if lowered.startswith("delete folder "):
            return Plan([Action("delete_folder", {"path": text[14:].strip().strip('"')})])
        if lowered.startswith("run "):
            return Plan([Action("run_terminal_command", {"command": text[4:].strip()})])

        media_action = self._match_media(lowered)
        if media_action:
            return Plan([Action("media_control", {"action": media_action})])

        return Plan([], notes="No executable action found.")

    @staticmethod
    def _query_after(text: str, marker: str) -> str:
        index = text.lower().find(marker)
        if index == -1:
            return text
        return text[index + len(marker) :].strip(" :")

    @staticmethod
    def _match_media(lowered: str) -> str | None:
        if "play" in lowered or "pause" in lowered:
            return "play_pause"
        if "next" in lowered and "track" in lowered:
            return "next"
        if "previous" in lowered or "prev" in lowered:
            return "previous"
        if "mute" in lowered:
            return "mute"
        if "volume up" in lowered:
            return "volume_up"
        if "volume down" in lowered:
            return "volume_down"
        return None
