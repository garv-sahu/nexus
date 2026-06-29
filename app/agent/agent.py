"""Top-level desktop agent orchestration."""

from __future__ import annotations

import logging

from app.agent.executor import ExecutionSummary, Executor
from app.agent.llm import LLMClient, LLMMessage, OllamaLLMClient
from app.agent.memory import ConversationMemory, MessageRole
from app.agent.planner import Planner
from app.agent.prompts import FINAL_RESPONSE_SYSTEM_PROMPT
from app.config import Settings, load_settings
from app.core.exceptions import LLMError
from app.core.tool_manager import ToolManager
from app.tools import build_default_tools
from app.utils.logger import configure_logging
from app.utils.permissions import dangerous_action_guard


class DesktopAgent:
    """Nexus desktop agent facade."""

    def __init__(
        self,
        *,
        llm: LLMClient,
        planner: Planner,
        executor: Executor,
        memory: ConversationMemory,
        logger: logging.Logger,
    ) -> None:
        self._llm = llm
        self._planner = planner
        self._executor = executor
        self._memory = memory
        self._logger = logger

    def handle(self, user_input: str) -> str:
        """Plan, execute, and respond to one user request."""

        self._logger.info("Received user request")
        self._memory.add_user(user_input)
        plan = self._planner.plan(user_input, self._memory.messages())

        if not plan.actions:
            response = plan.notes or "I could not map that request to an available desktop action."
            self._memory.add_assistant(response)
            return response

        summary = self._executor.execute(plan.actions)
        response = self._build_response(user_input, summary)
        self._memory.add(MessageRole.TOOL, self._format_results(summary))
        self._memory.add_assistant(response)
        return response

    def _build_response(self, user_input: str, summary: ExecutionSummary) -> str:
        deterministic = self._deterministic_response(summary)
        try:
            messages = [
                LLMMessage(role="user", content=user_input),
                LLMMessage(role="tool", content=self._format_results(summary)),
            ]
            response = self._llm.chat(messages, system_prompt=FINAL_RESPONSE_SYSTEM_PROMPT)
            return response.content.strip() or deterministic
        except LLMError:
            self._logger.warning("Final LLM response failed; using deterministic summary")
            return deterministic

    @staticmethod
    def _deterministic_response(summary: ExecutionSummary) -> str:
        if not summary.results:
            return "No actions were executed."
        return "\n".join(f"- {result.message}" for result in summary.results)

    @staticmethod
    def _format_results(summary: ExecutionSummary) -> str:
        lines = []
        for result in summary.results:
            status = result.status.value
            error = f" Error: {result.error}" if result.error else ""
            lines.append(f"{result.tool_name}: {status}. {result.message}{error}")
        return "\n".join(lines)


def build_agent(settings: Settings | None = None) -> DesktopAgent:
    """Build a fully wired Nexus desktop agent."""

    settings = settings or load_settings()
    logger = configure_logging(settings.log_dir)
    logger.info("Starting Nexus")

    tools = build_default_tools(settings)
    tool_manager = ToolManager(
        permission_hooks=[
            dangerous_action_guard(
                allow_dangerous_actions=settings.allow_dangerous_actions,
            )
        ],
        logger=logger,
    )
    tool_manager.register_many(tools)

    llm = OllamaLLMClient(
        host=settings.ollama_host,
        model=settings.ollama_model,
        timeout_seconds=settings.request_timeout_seconds,
        logger=logger,
    )
    memory = ConversationMemory(limit=settings.memory_limit)
    planner = Planner(llm, tools, logger=logger)
    executor = Executor(tool_manager, logger=logger)

    return DesktopAgent(
        llm=llm,
        planner=planner,
        executor=executor,
        memory=memory,
        logger=logger,
    )
