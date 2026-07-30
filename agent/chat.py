from .planner import Planner
from .llm import LLM
from .memory import Memory
from .browser_router import BrowserRouter
from tools.browser import BrowserTool

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

        browser_response = self.browser_router.handle(user_input)
        if browser_response is not None:
            self.memory.add("assistant", browser_response)
            return browser_response

        prompt = self.planner.build_prompt(
            self.memory,
            user_input
        )

        response = self.llm.generate(prompt)

        self.memory.add("assistant", response)

        return response
