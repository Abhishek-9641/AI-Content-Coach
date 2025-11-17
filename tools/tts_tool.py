import os, tempfile
from openai import OpenAI
from langchain.agents import Tool
from config.key_manager import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def text_to_speech_live(text: str):
    if not text.strip():
        raise ValueError("❌ Empty text.")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    ) as response:
        response.stream_to_file(tmp_path)
    with open(tmp_path, "rb") as f:
        audio = f.read()
    os.remove(tmp_path)
    return audio

tts_tool = Tool(
    name="Text-to-Speech",
    func=text_to_speech_live,
    description="Converts text output of the agent to natural speech using OpenAI TTS."
)
