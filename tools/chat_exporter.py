from fpdf import FPDF
from datetime import datetime
from langchain.tools import Tool

def save_chat_as_pdf(chat_history, filename_prefix="chat_export"):
    if not chat_history:
        return "❌ No chat to save."

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Chat History", ln=True, align="C")

    for i, (user_msg, agent_msg) in enumerate(chat_history, 1):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"--- Exchange {i} ---", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 5, f"User: {user_msg}\n\nAgent: {agent_msg}\n\n")

    fname = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(fname)
    return f"✅ Chat saved as {fname}"

chat_export_tool = Tool(
    name="SaveChatPDF",
    func=save_chat_as_pdf,
    description="Exports chat history as PDF."
)


print("✅ Chat exporter is ready!")
