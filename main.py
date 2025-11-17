from core.rag_pipeline import build_rag_pipeline
from core.agent_controller import AgentController

# Initialize RAG pipeline
chain, retriever, memory, llm = build_rag_pipeline()
agent = AgentController(llm=llm, memory=memory)

def run_text_agent(user_input: str) -> str:
    if not user_input.strip():
        return "❌ No input provided."
    try:
        reply = agent.invoke(user_input)
        return reply
    except Exception as e:
        print("❌ Error in run_text_agent:", e)
        return "❌ Something went wrong while processing your message."

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        print("Agent:", run_text_agent(user_input))




# import os
# from core.rag_pipeline_old import build_rag_pipeline
# from core.agent_controller import AgentController
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # ------------------ Build agent pipeline ------------------
# chain, retriever, memory, llm = build_rag_pipeline()  # no need for persist_directory or collection_name
# agent = AgentController(llm=llm, memory=memory)

# # ------------------ Flask-friendly function ------------------
# def run_text_agent(user_input: str) -> str:
#     if not user_input.strip():
#         return "❌ No input provided."
#     try:
#         reply = agent.invoke(user_input)
#         return reply
#     except Exception as e:
#         print("❌ Error in run_text_agent:", e)
#         return "❌ Something went wrong while processing your message."

# # ------------------ Optional CLI test ------------------
# if __name__ == "__main__":
#     print("💬 Agent is ready. Type your message below:")
#     while True:
#         user_input = input("You: ")
#         reply = run_text_agent(user_input)
#         print("Agent:", reply)

