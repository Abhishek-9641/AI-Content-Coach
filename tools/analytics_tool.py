from openai import OpenAI
from langchain.tools import Tool
from config.key_manager import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_metrics(data: dict) -> dict:
    views, likes, comments, shares = map(data.get, ["views", "likes", "comments", "shares"])
    engagement = (likes + comments + shares) / max(views, 1) * 100
    prompt = f"""Analyze engagement data:
    Views: {views}, Likes: {likes}, Comments: {comments}, Shares: {shares}, Engagement: {engagement:.2f}%
    Provide 3–5 tips to improve performance."""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"summary": f"Engagement rate: {engagement:.2f}%", "advice": resp.choices[0].message.content}

analytics_tool = Tool(
    name="AnalyticsWithGPTAdvice",
    func=analyze_metrics,
    description="Analyzes content engagement metrics and gives GPT advice."
)
