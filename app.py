import os
import io
import tempfile
from openai import OpenAI
import asyncio
import websockets
import threading
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
from io import BytesIO
from fpdf import FPDF
from datetime import datetime

# ===== Load Environment Variables =====
load_dotenv()
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# ===== Imports =====
import main
from main import agent
from tools.tts_tool import text_to_speech_live
from tools.stt_tool import speech_to_text_tool_web
from tools.ingest_tool import ingest_content
from tools.content_growth import content_growth_advanced
from tools.chat_exporter import save_chat_as_pdf

# ===== Flask Setup =====
app = Flask(__name__)

# ===== Temporary Memory for Ingested Content =====
temporary_context = ""

# =========================================================
# 🏠 HOME PAGE
# =========================================================
@app.route('/')
def index():
    return render_template('index.html')


# =========================================================
# 🤖 MAIN AGENT QUERY
# =========================================================

@app.route('/agent_query', methods=['POST'])
def agent_query():
    global temporary_context
    data = request.get_json()
    user_text = data.get("text", "").strip()

    if not user_text:
        return jsonify({
            "status": "error",
            "result": "❌ Empty message.",
            "icon": "❌"
        })

    try:
        # Build context-aware prompt that forces the agent to use the ingested content
        if temporary_context:
            prompt = (
                f"You have access to the following ingested document or web content:\n\n"
                f"{temporary_context[:4000]}\n\n"
                f"Answer the user's question **using only this content**.\n"
                f"Do NOT call web search, speech-to-text, or any other tools.\n\n"
                f"User question: {user_text}"
            )
        else:
            prompt = (
                f"{user_text}\n\n"
                f"IMPORTANT: There is no ingested content available. Answer based on general knowledge only.\n"
                f"Do NOT call web search, speech-to-text, or any other tools."
            )

        # Log prompt (first 500 chars)
        print("🧩 Prompt sent to agent:\n", prompt[:500])

        # Call the working agent
        response = main.run_text_agent(prompt)

        return jsonify({
            "status": "success",
            "result": response,
            "icon": "✅"
        })

    except Exception as e:
        print("❌ ERROR in /agent_query:", e)
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "result": f"⚠️ Something went wrong while processing your message: {str(e)}",
            "icon": "❌"
        })


# =========================================================
# 🧩 CONTENT INGESTION (PDF / URL)
# =========================================================

@app.route('/ingest', methods=['POST'])
def ingest():
    global temporary_context
    url = request.form.get('url')
    pdf_file = request.files.get('pdf_file')

    if not url and not pdf_file:
        return jsonify({
            "status": "error",
            "message": "❌ No URL or PDF provided",
            "icon": "❌"
        }), 400

    try:
        if url:
            full_message = ingest_content(url, state=None)
            summary_snippet = full_message.split("📝 Summary:")[-1].strip() if "📝 Summary:" in full_message else full_message[:200]
            temporary_context = summary_snippet
            message = "✅ URL successfully ingested!"
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf_file.save(tmp.name)
                tmp_path = tmp.name
            full_message = ingest_content(tmp_path, state=None)
            summary_snippet = full_message.split("📝 Summary:")[-1].strip() if "📝 Summary:" in full_message else full_message[:200]
            temporary_context = summary_snippet
            message = "✅ PDF successfully ingested!"

        print("✅ TEMP MEMORY UPDATED with summary snippet.")
        print("Preview:", temporary_context[:300])

        return jsonify({
            "status": "success",
            "message": message,               # still used by UI for green check
            "summary_snippet": temporary_context,  # new field for the short summary
            "icon": "✅"
        })

    except Exception as e:
        print("❌ ERROR in /ingest:", e)
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Failed to ingest content: {str(e)}",
            "icon": "❌"
        }), 500




# This is working too, better than the one below, but still two displays

# @app.route('/ingest', methods=['POST'])
# def ingest():
#     global temporary_context
#     url = request.form.get('url')
#     pdf_file = request.files.get('pdf_file')

#     if not url and not pdf_file:
#         return jsonify({
#             "status": "error",
#             "message": "❌ No URL or PDF provided",
#             "icon": "❌"
#         }), 400

#     try:
#         # --------------------------
#         # Ingest content from URL or PDF
#         # --------------------------
#         display_messages = []

#         if url:
#             full_message = ingest_content(url, state=None)
#             # Extract only the summary portion for display
#             if "📝 Summary:" in full_message:
#                 summary_snippet = full_message.split("📝 Summary:")[1].strip()
#             else:
#                 summary_snippet = full_message[:200]
#             display_messages.append(f"✅ URL successfully ingested!\n{summary_snippet}")

#         if pdf_file:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#                 pdf_file.save(tmp.name)
#                 tmp_path = tmp.name
#             full_message = ingest_content(tmp_path, state=None)
#             if "📝 Summary:" in full_message:
#                 summary_snippet = full_message.split("📝 Summary:")[1].strip()
#             else:
#                 summary_snippet = full_message[:200]
#             display_messages.append(f"✅ PDF successfully ingested!\n{summary_snippet}")

#         # Combine into a single message for frontend
#         message = "\n\n".join(display_messages)

#         # Store in temporary memory
#         temporary_context = message
#         print("✅ TEMP MEMORY UPDATED with message.")
#         print("Preview:", temporary_context[:300])

#         return jsonify({
#             "status": "success",
#             "message": message,
#             "icon": "✅",
#             "content_preview": message[:500] + "..."
#         })

#     except Exception as e:
#         print("❌ ERROR in /ingest:", e)
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "status": "error",
#             "message": f"Failed to ingest content: {str(e)}",
#             "icon": "❌"
#         }), 500




# This is working for both pdf and url, but a small issue with dual display
# @app.route('/ingest', methods=['POST'])
# def ingest():
#     global temporary_context
#     url = request.form.get('url')
#     pdf_file = request.files.get('pdf_file')

#     if not url and not pdf_file:
#         return jsonify({
#             "status": "error",
#             "message": "❌ No URL or PDF provided",
#             "icon": "❌"
#         }), 400

#     try:
#         # --------------------------
#         # Ingest content from URL and/or PDF
#         # --------------------------
#         messages = []

#         if url:
#             msg_url = ingest_content(url, state=None)
#             messages.append(f"URL successfully ingested!\nSnippet: {msg_url[:200]}")

#         if pdf_file:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#                 pdf_file.save(tmp.name)
#                 tmp_path = tmp.name
#             msg_pdf = ingest_content(tmp_path, state=None)
#             messages.append(f"PDF successfully ingested!\nSnippet: {msg_pdf[:200]}")

#         # Combine all messages into a single response
#         message = "\n\n".join(messages)
#         temporary_context = message
#         print("✅ TEMP MEMORY UPDATED with message.")
#         print("Preview:", temporary_context[:300])

#         return jsonify({
#             "status": "success",
#             "message": message,
#             "icon": "✅",
#             "content_preview": message[:500] + "..."
#         })

#     except Exception as e:
#         print("❌ ERROR in /ingest:", e)
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "status": "error",
#             "message": f"Failed to ingest content: {str(e)}",
#             "icon": "❌"
#         }), 500



# # This is working!!
# @app.route('/ingest', methods=['POST'])
# def ingest():
#     global temporary_context
#     url = request.form.get('url')
#     pdf_file = request.files.get('pdf_file')

#     if not url and not pdf_file:
#         return jsonify({
#             "status": "error",
#             "message": "❌ No URL or PDF provided",
#             "icon": "❌"
#         }), 400

#     try:
#         # Ingest content from URL or PDF
#         if url:
#             message = ingest_content(url, state=None)
#             print(f"✅ Ingested from URL: {url}")
#         else:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#                 pdf_file.save(tmp.name)
#                 tmp_path = tmp.name
#             print(f"✅ PDF saved to temporary path: {tmp_path}")
#             message = ingest_content(tmp_path, state=None)

#         # Store simple text preview in temporary memory (optional)
#         temporary_context = message
#         print("✅ TEMP MEMORY UPDATED with message.")
#         print("Preview:", temporary_context[:300])

#         return jsonify({
#             "status": "success",
#             "message": message,
#             "icon": "✅",
#             "content_preview": message[:500] + "..."
#         })

#     except Exception as e:
#         print("❌ ERROR in /ingest:", e)
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "status": "error",
#             "message": f"Failed to ingest content: {str(e)}",
#             "icon": "❌"
#         }), 500


# =========================================================
# 🧹 CLEAR INGESTED DATA
# =========================================================
@app.route('/clear-ingested', methods=['POST'])
def clear_ingested():
    global temporary_context
    temporary_context = ""
    return jsonify({
        "status": "success",
        "message": "✅ Temporary ingestion memory cleared.",
        "icon": "✅"
    })




# =========================================================
# 🔊 TEXT TO SPEECH
# =========================================================
@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        audio_data = text_to_speech_live(text)
        return send_file(
            io.BytesIO(audio_data),
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='speech.mp3'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# 🎙️ SPEECH TO TEXT (MICROPHONE) ------- handles complete audio files, used when you stop recording and send everything at once.
# =========================================================
@app.route("/transcribe_audio", methods=["POST"])
def transcribe_audio():
    """Handle audio from the browser and return Whisper transcription."""
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name

        from openai import OpenAI
        client = OpenAI()

        with open(tmp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )

        text = transcription.text.strip()
        print(f"📝 Whisper transcription (browser mic): {text}")
        return jsonify({"text": text})

    except Exception as e:
        print("❌ ERROR in /transcribe_audio:", e)
        return jsonify({"error": str(e)}), 500
    

# =========================================================
# 📈 CONTENT GROWTH ANALYSIS
# =========================================================
@app.route('/content_growth', methods=['POST'])
def content_growth():
    post_url = request.form.get("post_url")
    caption = request.form.get("caption", "")
    metrics_json = request.form.get("metrics")
    screenshot = request.files.get("screenshot")

    metrics = None
    if metrics_json:
        try:
            import json
            metrics = json.loads(metrics_json)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON in metrics"}), 400

    try:
        result = content_growth_advanced(
            post_url=post_url,
            screenshot=screenshot,
            metrics=metrics,
            caption=caption
        )
        return jsonify(result)
    except Exception as e:
        print("❌ Content Growth Error:", e)
        return jsonify({"error": str(e)}), 500

    

# @app.route('/content_growth', methods=['POST'])
# def content_growth():
#     post_url = request.form.get("post_url")
#     caption = request.form.get("caption", "")
#     metrics_json = request.form.get("metrics")
#     screenshot = request.files.get("screenshot")

#     metrics = None
#     if metrics_json:
#         try:
#             import json
#             metrics = json.loads(metrics_json)
#         except json.JSONDecodeError:
#             return jsonify({"error": "Invalid JSON in metrics"}), 400

#     try:
#         result = content_growth_advanced(
#             post_url=post_url,
#             screenshot=screenshot,
#             metrics=metrics,
#             caption=caption
#         )
#         return jsonify({"result": result})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



# =========================================================
#  CHAT EXPORTER
# =========================================================

# from flask import send_file, request, jsonify
# from fpdf import FPDF
# from io import BytesIO
# from datetime import datetime

from fpdf import FPDF
from io import BytesIO
from flask import send_file, request, jsonify
from datetime import datetime

@app.route('/export_chat', methods=['POST'])
def export_chat():
    try:
        chat_history = request.json.get("chat_history", [])
        if not chat_history:
            return jsonify({"status":"error","message":"❌ No chat history","icon":"❌"}), 400

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Chat History", ln=True, align="C")

        for i, pair in enumerate(chat_history, 1):
            user_msg, agent_msg = pair
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"--- Exchange {i} ---", ln=True)
            pdf.set_font("Arial", "", 10)
            # Replace unsupported characters
            user_msg = user_msg.encode('latin-1', 'replace').decode('latin-1')
            agent_msg = agent_msg.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, f"User: {user_msg}\n\nAgent: {agent_msg}\n\n")

        buf = BytesIO()
        pdf.output(buf)
        buf.seek(0)

        fname = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(buf, as_attachment=True, download_name=fname, mimetype="application/pdf")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status":"error","message":f"Failed to export: {str(e)}","icon":"❌"}), 500



    
# =========================================================
# 🚀 RUN SERVER
# =========================================================
if __name__ == '__main__':
    app.run(debug=True)
