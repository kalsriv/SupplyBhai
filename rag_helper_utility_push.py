import os
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# Working directory
working_dir = os.path.dirname(os.path.abspath(__file__))

# Embeddings + LLM
embedding = HuggingFaceEmbeddings()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

# ---------------------------------------------------------
# PROCESS DOCUMENT → CHROMA VECTORSTORE (CLOUD-SAFE VERSION)
# ---------------------------------------------------------
def process_document_to_chroma_db(file_path):
    """
    Cloud-optimized version.
    Does NOT embed or process PDFs.
    If the vectorstore exists, skip immediately.
    """

    # If vectorstore already exists, skip ingestion
    if os.path.exists(f"{working_dir}/doc_vectorstore"):
        return 0

    # Cloud should NEVER embed — return immediately
    return 0


# # ---------------------------------------------------------
# # BUILD RAG CHAIN
# # ---------------------------------------------------------
# def build_rag_chain(llm, retriever):
#     prompt = ChatPromptTemplate.from_template("""
#     You are a supply chain expert. Use ONLY the retrieved context to answer.

#     Context:
#     {context}

#     Question:
#     {question}

#     Answer:
#     """)

#     rag_chain = (
#         {
#             "context": lambda x: retriever.invoke(x["question"]),
#             "question": lambda x: x["question"]
#         }
#         | prompt
#         | llm
#         | StrOutputParser()
#     )
def build_rag_chain(llm, retriever):
    prompt = ChatPromptTemplate.from_template("""
You are SupplyBhai — a senior global supply chain consultant with 20+ years of experience.
Your job is to give clear, confident, expert answers based strictly on the retrieved context.

Follow these rules:

1. You ONLY answer questions that are directly related to supply chain, logistics, procurement, inventory, forecasting, S&OP, warehousing, transportation, manufacturing, or global trade. 
2. If the user asks anything outside supply chain — including astrology, medicine, personal advice, relationships, religion, or unrelated academic topics — you MUST politely refuse and say the question is outside your domain. 
3. Do NOT create analogies, metaphors, or forced interpretations to make an unrelated question seem relevant to supply chain. 
4. Never mention the words “context”, “retriever”, “documents”, or “PDF”. 
5. Never explain what information is missing. Simply answer if it is in-domain, or politely decline if it is out-of-domain. 
6. When answering in-domain questions, write like a senior supply chain consultant: concise, authoritative, and practical. 
7. Provide clear, actionable insights — not summaries or academic commentary.

---

### Retrieved Information:
{context}

### User Question:
{question}

### Expert Answer:
""")

    rag_chain = (
        {
            "context": lambda x: retriever.invoke(x["question"]),
            "question": lambda x: x["question"]
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain



# ---------------------------------------------------------
# ANSWER USER QUESTION
# ---------------------------------------------------------
def answer_question(user_question):
    vectordb = Chroma(
        persist_directory=f"{working_dir}/doc_vectorstore",
        embedding_function=embedding
    )

    retriever = vectordb.as_retriever()

    rag_chain = build_rag_chain(llm, retriever)

    return rag_chain.invoke({"question": user_question})
