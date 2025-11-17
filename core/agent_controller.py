import traceback
from langchain.agents import initialize_agent, AgentType
from tools import ALL_TOOLS

class AgentController:
    def __init__(self, llm, memory):
        self.agent = initialize_agent(
            tools=ALL_TOOLS,
            llm=llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True
        )

    @property
    def memory(self):
        """Exposes agent memory."""
        return self.agent.memory
    
    def invoke(self, query: str, context: str = None) -> str:
        """
        Handles user query, optionally injecting context (like from PDF or URL ingestion).
        - Splits context if too long.
        """
        try:
            # Option 1: Prepend context safely
            if context:
                max_chars = 3000  # adjust based on LLM token limit
                context = context[:max_chars] + ("..." if len(context) > max_chars else "")
                query = f"Use the following context to answer accurately:\n\n{context}\n\nUser query: {query}"

            # Invoke the agent
            result = self.agent.invoke({"input": query})
            # result might be a dict or string
            if isinstance(result, dict):
                return result.get("output", str(result))
            return str(result)

        except Exception as e:
            print("❌ Error during agent invocation:", e)
            traceback.print_exc()
            return "❌ Something went wrong while processing your message."
    
    def add_to_memory(self, content: str, role: str = "user"):
        """
        Safely adds content to agent memory.
        role: 'user', 'ai', or 'system'
        """
        try:
            if role == "user":
                self.agent.memory.chat_memory.add_user_message(content)
            elif role == "ai":
                self.agent.memory.chat_memory.add_ai_message(content)
            elif role == "system":
                self.agent.memory.chat_memory.add_system_message(content)
            else:
                print(f"⚠️ Unknown role: {role}, treating as user message")
                self.agent.memory.chat_memory.add_user_message(content)
        except Exception as e:
            print("❌ Error adding content to memory:", e)
            traceback.print_exc()

