import os
import tempfile
import sounddevice as sd
# import soundfile as sf
from openai import OpenAI
from dotenv import load_dotenv
from langchain.tools import Tool  # if you're using LangChain for tool registration

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize client
client = OpenAI(api_key=OPENAI_API_KEY)


# 🎙️ Record audio locally (for local use only)
def record_audio(duration=5, fs=16000):
    """
    Records audio from the user's microphone for 'duration' seconds.
    Returns a temporary WAV file path.
    """
    print(f"🎙️ Recording for {duration} seconds...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, audio, fs)
    return tmp.name


# 🧠 Speech-to-text (local mode)
def speech_to_text_tool(duration=10):
    """
    Records the user's voice locally and converts it to text using Whisper.
    """
    audio_path = record_audio(duration)
    result = client.audio.transcriptions.create(
        file=open(audio_path, "rb"),
        model="whisper-1"
    )
    os.remove(audio_path)
    return result.text


# 🌐 Speech-to-text (web upload mode)
def speech_to_text_tool_web(audio_path):
    """
    Converts an uploaded audio file (from the Flask frontend) to text using Whisper.
    """
    try:
        result = client.audio.transcriptions.create(
            file=open(audio_path, "rb"),
            model="whisper-1"
        )
        return result.text
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        raise


# 🧩 Register as a LangChain tool (optional)
speech_tool = Tool(
    name="Speech-to-Text",
    func=speech_to_text_tool,
    description="Converts spoken input to text using OpenAI Whisper."
)

