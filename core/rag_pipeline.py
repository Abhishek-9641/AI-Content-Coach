import os
from dotenv import load_dotenv

from pinecone import Pinecone
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory

# ============================
# Load environment variables
# ============================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Pinecone index details
INDEX_NAME = "pinecone-db"

# ============================
# Build RAG Pipeline
# ============================
def build_rag_pipeline(index_name: str = INDEX_NAME):
    """Creates and returns the RAG components: chain, retriever, memory, llm."""

    # 1️⃣ Initialize Pinecone client
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(index_name)
    print(f"✅ Connected to Pinecone index: {index_name}")

    # 2️⃣ Initialize Embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=OPENAI_API_KEY
    )

    # 3️⃣ Link Pinecone index with LangChain
    vectorstore = PineconeVectorStore(index, embeddings, text_key="text")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    print("✅ Retriever initialized.")

    # 4️⃣ Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        openai_api_key=OPENAI_API_KEY
    )

    # 5️⃣ Memory for conversation context
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        k=5
    )

    # 6️⃣ Custom Prompt Template
    prompt = PromptTemplate(
        input_variables=["context", "question", "chat_history"],
        template="""
You are an AI assistant specialized in helping AI-driven content creators 
(YouTube, Instagram, blogs, social media, podcasts).

Always respond clearly and concisely.
Prefer bullet points (3–6) with short, impactful sentences.
Provide practical, actionable insights whenever possible.
Always prefer the knowledge base first; if context is incomplete, use your own knowledge.
Avoid repetition or overly generic advice.
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

    # 7️⃣ Build the Conversational Retrieval Chain
    conv_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
        output_key="output",
        verbose=False
    )

    print("✅ RAG pipeline built successfully.")
    return conv_chain, retriever, memory, llm



# import os
# from dotenv import load_dotenv

# from pinecone import Pinecone
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_community.vectorstores import Pinecone as PineconeVectorStore
# from langchain.prompts import PromptTemplate
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferWindowMemory

# # ============================
# # Load environment variables
# # ============================
# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# # Pinecone index details
# INDEX_NAME = "pinecone-db"

# # ============================
# # Build RAG Pipeline
# # ============================
# def build_rag_pipeline(index_name: str = INDEX_NAME):
#     """Creates and returns the RAG components: chain, retriever, memory, llm."""

#     # 1️⃣ Initialize Pinecone client
#     pc = Pinecone(api_key=PINECONE_API_KEY)
#     index = pc.Index(index_name)
#     print(f"✅ Connected to Pinecone index: {index_name}")

#     # 2️⃣ Initialize Embeddings
#     embeddings = OpenAIEmbeddings(
#         model="text-embedding-3-large",
#         openai_api_key=OPENAI_API_KEY
#     )

#     # 3️⃣ Link Pinecone index with LangChain
#     vectorstore = PineconeVectorStore(index, embeddings, text_key="text")
#     retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
#     print("✅ Retriever initialized.")

#     # 4️⃣ Initialize LLM
#     llm = ChatOpenAI(
#         model="gpt-4o-mini",
#         temperature=0.2,
#         openai_api_key=OPENAI_API_KEY
#     )

#     # 5️⃣ Memory for conversation context
#     memory = ConversationBufferWindowMemory(
#         memory_key="chat_history",
#         return_messages=True,
#         k=5
#     )

#     # 6️⃣ Custom Prompt Template
#     prompt = PromptTemplate(
#         input_variables=["context", "question", "chat_history"],
#         template="""
# You are an AI assistant specialized in helping AI-driven content creators 
# (YouTube, Instagram, blogs, social media, podcasts).

# Always respond clearly and concisely.
# Prefer bullet points (3–6) with short, impactful sentences.
# Provide practical, actionable insights whenever possible.
# Always prefer the knowledge base first; if context is incomplete, use your own knowledge.
# Avoid repetition or overly generic advice.
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

#     # 7️⃣ Build the Conversational Retrieval Chain
#     conv_chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=retriever,
#         memory=memory,
#         combine_docs_chain_kwargs={"prompt": prompt},
#         return_source_documents=True,
#         output_key="output",
#         verbose=False
#     )

#     print("✅ RAG pipeline built successfully.")
#     return conv_chain, retriever, memory, llm






# import os
# from dotenv import load_dotenv

# from pinecone import Pinecone
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_pinecone import PineconeVectorStore
# from langchain.prompts import PromptTemplate
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferWindowMemory


# # ============================
# # Load environment variables
# # ============================
# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# # Pinecone index details
# INDEX_NAME = "pinecone-db"

# # ============================
# # Build RAG Pipeline
# # ============================
# def build_rag_pipeline(index_name: str = INDEX_NAME):
#     """Creates and returns the RAG components: chain, retriever, memory, llm."""

#     # 1️⃣ Initialize Pinecone client
#     pc = Pinecone(api_key=PINECONE_API_KEY)
#     index = pc.Index(index_name)
#     print(f"✅ Connected to Pinecone index: {index_name}")

#     # 2️⃣ Initialize Embeddings
#     embeddings = OpenAIEmbeddings(
#         model="text-embedding-3-large",
#         openai_api_key=OPENAI_API_KEY
#     )

#     # 3️⃣ Link Pinecone index with LangChain
#     vectorstore = PineconeVectorStore(
#         index_name=index_name,
#         embedding=embeddings,
#         pinecone_api_key=PINECONE_API_KEY,
#     )
#     retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
#     print("✅ Retriever initialized.")

#     # 4️⃣ Initialize LLM
#     llm = ChatOpenAI(
#         model="gpt-4o-mini",
#         temperature=0.2,
#         openai_api_key=OPENAI_API_KEY
#     )

#     # 5️⃣ Memory for conversation context
#     memory = ConversationBufferWindowMemory(
#         memory_key="chat_history",
#         return_messages=True,
#         k=5
#     )

#     # 6️⃣ Custom Prompt Template
#     prompt = PromptTemplate(
#         input_variables=["context", "question", "chat_history"],
#         template="""
# You are an AI assistant specialized in helping AI-driven content creators 
# (YouTube, Instagram, blogs, social media, podcasts).

# Always respond clearly and concisely.
# Prefer bullet points (3–6) with short, impactful sentences.
# Provide practical, actionable insights whenever possible.
# Always prefer the knowledge base first; if context is incomplete, use your own knowledge.
# Avoid repetition or overly generic advice.
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

#     # 7️⃣ Build the Conversational Retrieval Chain
#     conv_chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=retriever,
#         memory=memory,
#         combine_docs_chain_kwargs={"prompt": prompt},
#         return_source_documents=True,
#         output_key="output",
#         verbose=False
#     )

#     print("✅ RAG pipeline built successfully.")
#     return conv_chain, retriever, memory, llm
