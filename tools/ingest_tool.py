from langchain.tools import Tool
from bs4 import BeautifulSoup
import requests, fitz, tempfile, os
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from pinecone import Pinecone, ServerlessSpec

# 🔑 Setup Pinecone + OpenAI
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "pinecone-db"

# 🧠 Initialize embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", openai_api_key=OPENAI_API_KEY)

# ✅ Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if missing
if INDEX_NAME not in pc.list_indexes().names():
    print(f"🆕 Creating Pinecone index: {INDEX_NAME}")
    pc.create_index(
        name=INDEX_NAME,
        dimension=3072,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )


# Connect to index
index = pc.Index(INDEX_NAME)


# Create LangChain vectorstore wrapper
vectorstore = LangchainPinecone(index, embeddings, text_key="text")


# --------------------------
# 1️⃣ Web Page Scraper
# --------------------------
def scrape_web_page(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])
        return text.strip()[:3000]
    except Exception as e:
        return f"Error scraping {url}: {e}"


# --------------------------
# 2️⃣ PDF Reader
# --------------------------
def read_pdf_from_upload(file) -> str:
    try:
        if isinstance(file, str):
            file_path = file
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                file_path = tmp.name

        doc = fitz.open(file_path)
        text = "".join(page.get_text() for page in doc)
        return text.strip()[:3000]
    except Exception as e:
        return f"Error reading PDF: {e}"


# --------------------------
# 3️⃣ GPT Summarization
# --------------------------
summary_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)

# This is working!!
# --------------------------
# 4️⃣ Unified Ingest Function
# --------------------------
def ingest_content(*args, **kwargs) -> str:
    """Agent-safe ingestion: handles URL, PDF, and extra state argument."""

    source = None

    # Handle flexible calling patterns
    if len(args) > 0:
        first = args[0]
        if isinstance(first, (list, tuple)):
            # Flatten and search for string or file-like object
            for item in first:
                if isinstance(item, str) and item.startswith("http"):
                    source = item
                    break
                if hasattr(item, "read"):  # file-like object
                    source = item
                    break
        elif isinstance(first, str) or hasattr(first, "read"):
            source = first
    elif "source" in kwargs:
        source = kwargs["source"]
    elif "file" in kwargs:
        source = kwargs["file"]

    if not source:
        return "⚠️ No valid source provided."

    # --------------------------
    # Load content
    # --------------------------
    if isinstance(source, str) and source.startswith("http"):
        content = scrape_web_page(source)
    else:
        content = read_pdf_from_upload(source)

    if not content or content.startswith("Error"):
        return f"⚠️ Ingestion failed: {content}"

    # --------------------------
    # Summarize
    # --------------------------
    try:
        summary_prompt = (
            f"Summarize the following text into 3–5 concise, actionable bullet points:\n\n{content[:3000]}"
        )
        summary = summary_llm.call_as_llm(summary_prompt)
    except Exception as e:
        summary = "⚠️ Failed to generate summary."

    # --------------------------
    # Store in Pinecone
    # --------------------------
    doc = Document(page_content=content, metadata={"source": str(source), "summary": summary})
    try:
        vectorstore.add_documents([doc])
        return (
            f"✅ Content from {source} added to Pinecone index.\n"
            f"📝 Summary: {summary}"
        )
    except Exception as e:
        import traceback
        print("\n❌ ERROR TRACEBACK STARTS HERE ❌")
        traceback.print_exc()
        print("❌ ERROR TRACEBACK ENDS HERE ❌\n")
        return f"❌ Failed to ingest content: {e}"


print("✅ Ingested tools are ready!")