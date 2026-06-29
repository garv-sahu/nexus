from __future__ import annotations

from collections.abc import Iterable, Iterator

from app.agent.llm import LLMClient, LLMMessage, LLMResponse
from app.agent.memory import ConversationMemory
from app.agent.planner import Planner
from app.services.filesystem import FilesystemService
from app.tools.filesystem import CreateFolderTool


class FakeLLM(LLMClient):
    def __init__(self, content: str) -> None:
        self.content = content

    def chat(
        self,
        messages: Iterable[LLMMessage],
        *,
        system_prompt: str | None = None,
    ) -> LLMResponse:
        return LLMResponse(content=self.content, model="fake", raw={})

    def stream_chat(
        self,
        messages: Iterable[LLMMessage],
        *,
        system_prompt: str | None = None,
    ) -> Iterator[str]:
        yield self.content


def test_planner_returns_typed_actions_from_llm() -> None:
    llm = FakeLLM('{"actions":[{"tool":"create_folder","arguments":{"path":"C:/Temp/x"}}]}')
    planner = Planner(llm, [CreateFolderTool(FilesystemService())])
    memory = ConversationMemory(limit=5)

    plan = planner.plan("create folder C:/Temp/x", memory.messages())

    assert len(plan.actions) == 1
    assert plan.actions[0].tool_name == "create_folder"
    assert plan.actions[0].arguments == {"path": "C:/Temp/x"}


def test_planner_fallback_creates_folder_action() -> None:
    llm = FakeLLM("not json")
    planner = Planner(llm, [CreateFolderTool(FilesystemService())])

    plan = planner.plan("create folder C:/Temp/example", [])

    assert plan.actions[0].tool_name == "create_folder"
    assert plan.actions[0].arguments["path"] == "C:/Temp/example"
