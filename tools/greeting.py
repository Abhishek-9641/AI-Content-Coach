import random
from langchain.tools import Tool

def greet_user(user_input=None):
    greetings = [
        "Hi! 👋 I’m your AI Content Coach.",
        "Hello there! Ready to create amazing content?",
        "Hey! Let’s make something great today."
    ]
    return {"answer": random.choice(greetings)}

greeting_tool = Tool(
    name="Greeting",
    func=greet_user,
    description="Responds in a friendly but professional manner to greetings like hi/hello/good morning/afternoon/evening/night."
)
