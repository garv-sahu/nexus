"""Prompt templates used by the agent."""

from __future__ import annotations

from app.core.base_tool import BaseTool

PLANNER_SYSTEM_PROMPT = """You are Nexus, a local Windows desktop agent planner.
Convert the user's request into one or more tool actions.

Rules:
- Return only valid JSON. No markdown, no prose.
- Use only tools from the supplied tool list.
- Do not invent tools.
- Prefer one clear action unless multiple actions are explicitly needed.
- Put all tool parameters in the "arguments" object.
- If the request is conversational or unsupported, return an empty actions list.

Response schema:
{"actions":[{"tool":"tool_name","arguments":{"key":"value"}}],"notes":"short optional note"}
"""

FINAL_RESPONSE_SYSTEM_PROMPT = """You are Nexus, a concise desktop assistant.
Summarize completed actions in natural language.
If any action failed or was denied, say so clearly and include the reason.
"""


def render_tool_catalog(tools: list[BaseTool]) -> str:
    """Render registered tool specs for the planner prompt."""

    lines: list[str] = []
    for tool in sorted(tools, key=lambda item: item.name):
        params = ", ".join(f"{name}: {desc}" for name, desc in tool.spec.parameters.items())
        dangerous = " dangerous=true" if tool.spec.dangerous else ""
        lines.append(
            f"- {tool.name}: {tool.spec.description} "
            f"(category={tool.spec.category}{dangerous}; parameters={{{params}}})"
        )
    return "\n".join(lines)
