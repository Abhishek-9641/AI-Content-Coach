import os
from dotenv import load_dotenv

try:
    from google.colab import userdata
    _colab_available = True
except Exception:
    userdata = None
    _colab_available = False


def get_key(key_name: str) -> str:
    """Retrieve API keys from .env, Colab secrets, or environment variables."""
    load_dotenv()
    key = None
    if _colab_available and userdata:
        try:
            key = userdata.get(key_name)
        except Exception:
            key = None
    if not key:
        key = os.getenv(key_name)
    return key


# Preload important keys
OPENAI_API_KEY = get_key("OPENAI_API_KEY")
TAVILY_API_KEY = get_key("TAVILY_API_KEY")
SERPAPI_API_KEY = get_key("SERPAPI_API_KEY")
LANGCHAIN_API_KEY = get_key("LANGCHAIN_API_KEY")
