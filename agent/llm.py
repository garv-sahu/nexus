import ollama

class LLM:
    def __init__(self):
        self.model = "gemma4"

    def set_model(self, model):
        self.model = model

    def get_model(self):
        return self.model

    def generate(self, prompt):
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
           ]
        )

        return response["message"]["content"]