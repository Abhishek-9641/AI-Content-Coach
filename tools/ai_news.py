import os
from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool
from config.key_manager import SERPAPI_API_KEY

os.environ["SERPAPI_API_KEY"] = SERPAPI_API_KEY
search = SerpAPIWrapper()

def safe_news_search(query: str) -> str:
    if not query.strip():
        return "❌ Empty query."
    results = search.results(query)
    organic = results.get("organic_results", [])
    if not organic:
        return "No news found."
    summary = []
    for i, r in enumerate(organic[:5], 1):
        summary.append(f"{i}. {r.get('title')} - {r.get('snippet')}")
    return "\n".join(summary)

ai_news_tool = Tool(
    name="Latest AI News",
    func=safe_news_search,
    description="Fetches recent AI-related news or updates using SerpAPI."
)
