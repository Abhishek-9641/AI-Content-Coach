from openai import OpenAI
from langchain.tools import Tool
from config.key_manager import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def seo_analysis(content: str):
    if not content.strip():
        return "❌ Empty content."
    prompt = f"SEO analyze this content: {content}"
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content

seo_tool = Tool(
    name="AdvancedSEOAnalyzer",
    func=seo_analysis,
    description="Analyzes content for SEO and suggests improvements."
)
