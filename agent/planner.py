class Planner:
    def build_prompt(self, memory, user):
        history = ""

        for m in memory.messages:
            history += f"{m['role']}: {m['content']}\n"
            
        return f"""
You are an intelligent AI assistant.

Think carefully.

If tools are needed,
DO NOT pretend you executed them.

Instead respond like this:

PLAN:
...

ACTION:
tool(arguments)

Conversation:

{history}

User:
{user}
"""