class Planner:
    def build_prompt(self, memory, user):
        history = ""

        for m in memory.messages:
            history += f"{m['role']}: {m['content']}\n"
            
        return f"""
You are an intelligent AI assistant.

Think carefully before answering. Use your own knowledge and reasoning first.

Browser actions are available in the app, but Python executes them before this
prompt only when the user explicitly asks to:
- open a website or URL
- search the web or search a named site
- summarize a web page
- extract text, links, headings, emails, or phone numbers from a page
- take screenshots, click elements, or fill fields when Playwright is installed

Do not output tool-call syntax such as ACTION: search(...). If live web or
browser access would improve the answer but the user did not explicitly ask for
it, answer from your knowledge and mention any uncertainty briefly.

Conversation:

{history}

User:
{user}
"""