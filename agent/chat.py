from .planner import Planner
from .llm import LLM
from .memory import Memory

class Nexus:
    def __init__(self):
        self.memory = Memory()
        self.planner = Planner()
        self.llm = LLM()

    def set_model(self, model):
        self.llm.set_model(model)

    def get_model(self):
        return self.llm.get_model()

    def chat(self, user_input):
        self.memory.add("user", user_input)

        prompt = self.planner.build_prompt(
            self.memory,
            user_input
        )

        response = self.llm.generate(prompt)

        self.memory.add("assistant", response)

        return response