class Planner:
    def build_prompt(self, memory, user):
        history = ""

        for m in memory.messages:
            history += f"{m['role']}: {m['content']}\n"
            
        return f"""
You are an intelligent AI assistant.

Think carefully.

Browser actions are available in the app and are executed by Python before
normal conversation when the user asks to:
- open a website or URL
- search Google, YouTube, Spotify, GitHub, Reddit, Stack Overflow, Amazon,
  Flipkart, Bing, DuckDuckGo, or Google Maps
- summarize a web page
- extract text, links, headings, emails, or phone numbers from a page
- take screenshots, click elements, or fill fields when Playwright is installed

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
