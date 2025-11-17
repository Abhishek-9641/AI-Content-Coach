import os
from dotenv import load_dotenv

from pinecone import Pinecone, ServerlessSpec
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Pinecone as LangChainPinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.vectorstores import Pinecone as PineconeVectorStore



load_dotenv()

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")  # e.g., "us-west1-gcp"
INDEX_NAME = "pinecone-db"

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# Optional: create index if it doesn't exist
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,  # OpenAI embeddings dimension
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-west-2")  # adjust as needed
    )


def build_rag_pipeline(index_name: str = INDEX_NAME):
    """Creates and returns the RAG components: LLM, retriever, memory, and chain."""

    # OpenAI embeddings
    EMBEDDING_MODEL_NAME = "text-embedding-3-large"

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        openai_api_key=OPENAI_API_KEY
    )

      # ✅ Correct: use PineconeVectorStore with api_key, not client
    vectorstore = PineconeVectorStore(index, embeddings, text_key="text")

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        openai_api_key=OPENAI_API_KEY
    )

    # Memory
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        k=5
    )

    # Prompt template
    prompt = PromptTemplate(
        input_variables=["context", "question", "chat_history"],
        template="""
You are an AI assistant specialized in helping AI-driven content creators (YouTube, Instagram, blogs, social media, podcasts).
Always respond clearly and concisely.
Prefer bullet points (3–6) with short, impactful sentences.
Provide practical, actionable insights whenever possible.
Always prefer the knowledge base first. If context is incomplete, use your own knowledge or suitable tools.
Avoid repetition, filler, or overly generic advice.
Tailor answers for creators looking to grow, optimize, or monetize content.
When tools (news, SEO, analytics, etc.) are available, call them only when relevant.
Stay professional, encouraging, and results-oriented.

Conversation history:
{chat_history}

Context:
{context}

Question: {question}

Answer (concise and structured):
"""
    )

    # Build conversational retrieval chain
    conv_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
        output_key="output"
    )

    return conv_chain, retriever, memory, llm



# import os
# from dotenv import load_dotenv
# import pinecone

# from langchain.chat_models import ChatOpenAI
# from langchain.prompts import PromptTemplate
# from langchain.chains import ConversationalRetrievalChain
# from langchain.vectorstores import Pinecone
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.memory import ConversationBufferWindowMemory

# load_dotenv()
# # Load required API keys
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")

# # Connect to your existing index
# PINECONE_ENV = os.getenv("PINECONE_ENV")
# INDEX_NAME = "pinecone-db"


# # Initialize client
# import pinecone

# client = pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)


# def build_rag_pipeline(index_name: str):
#     """Creates and returns the RAG components: LLM, retriever, memory, and chain."""

#     # # Initialize Pinecone
#     # pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

#     # OpenAI embeddings
#     EMBEDDING_MODEL_NAME = "text-embedding-3-large"

#     embeddings = OpenAIEmbeddings(
#         model=EMBEDDING_MODEL_NAME,
#         openai_api_key=OPENAI_API_KEY
#     )

#     # Connect to Pinecone index
#     vectorstore = Pinecone.from_existing_index(
#         index_name=INDEX_NAME,
#         embedding=embeddings,
#         pinecone_api_key=PINECONE_API_KEY,
#     )

#     retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

#     # LLM
#     llm = ChatOpenAI(
#         model="gpt-4o-mini",
#         temperature=0.2,
#         openai_api_key=OPENAI_API_KEY
#     )

#     # Memory
#     memory = ConversationBufferWindowMemory(
#         memory_key="chat_history",
#         return_messages=True,
#         k=5
#     )

#     # Prompt template
#     prompt = PromptTemplate(
#         input_variables=["context", "question", "chat_history"],
#         template="""
# You are an AI assistant specialized in helping AI-driven content creators (YouTube, Instagram, blogs, social media, podcasts).
# Always respond clearly and concisely.
# Prefer bullet points (3–6) with short, impactful sentences.
# Provide practical, actionable insights whenever possible.
# Always prefer the knowledge base first. If context is incomplete, use your own knowledge or suitable tools.
# Avoid repetition, filler, or overly generic advice.
# Tailor answers for creators looking to grow, optimize, or monetize content.
# When tools (news, SEO, analytics, etc.) are available, call them only when relevant.
# Stay professional, encouraging, and results-oriented.

# Conversation history:
# {chat_history}

# Context:
# {context}

# Question: {question}

# Answer (concise and structured):
# """
#     )

#     # Build conversational retrieval chain
#     conv_chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=retriever,
#         memory=memory,
#         combine_docs_chain_kwargs={"prompt": prompt},
#         return_source_documents=True,
#         output_key="output"
#     )

#     return conv_chain, retriever, memory, llm





