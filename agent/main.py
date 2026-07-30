from chat import Nexus

agent = Nexus()

print("Welcome to the Nexus AI Agent. Type 'exit' or 'quit' to quit.")

while True:
    user = input("You: ")

    if user.lower() in ["exit", "quit"]:
        print("Exiting...")
        break

    response = agent.chat(user)
    print(f"Agent: {response}")