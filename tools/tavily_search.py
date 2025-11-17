from langchain.tools import Tool
from tavily import TavilyClient
from config.key_manager import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)

def search_tavily(query: str):
    results = tavily.search(query, max_results=3)
    return [r["content"] for r in results["results"]]

search_tool = Tool(
    name="Google Search (Tavily)",
    func=search_tavily,
    description="Searches the web for relevant info when context is insufficient."
)
