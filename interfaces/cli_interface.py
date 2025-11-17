class CLIInterface:
    def __init__(self, agent):
        self.agent = agent

    def run(self):
        print("🤖 AI Content Coach ready! Type 'exit' to quit.")
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break
            response = self.agent.invoke(user_input)
            print(f"\nAI: {response}")
