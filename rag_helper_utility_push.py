import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tavily import TavilyClient
load_dotenv()

# Working directory
working_dir = os.path.dirname(os.path.abspath(__file__))


#Calling travily for real time search Max 1000 per day per month for free tier
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def tavily_search(query):
    """
    Lightweight wrapper around Tavily Search API.
    Returns a short, clean text summary for the LLM.
    """
    try:
        result = tavily.search(query=query, max_results=5)
        # Extract text from results
        snippets = [item["content"] for item in result.get("results", [])]
        return "\n\n".join(snippets[:5])
    except Exception as e:
        return f"(Tavily search failed: {str(e)})"
    
# silently fallback to RAG when travily crosses the limit
def tavily_search(query):
    try:
        result = tavily.search(query=query, max_results=5)
        snippets = [item["content"] for item in result.get("results", [])]
        return "\n\n".join(snippets[:5])
    except Exception as e:
        return ""  

# Embeddings + LLM
embedding = HuggingFaceEmbeddings()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2
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

def build_rag_chain(llm, retriever):
    prompt = ChatPromptTemplate.from_template("""
You are SupplyBhai — a senior global supply chain consultant with 20+ years of experience.

You have two sources of information:
1. Retrieved supply chain knowledge (internal KB)
2. Real-time web search results

Use BOTH when relevant.

Rules:
- If the question requires real-time info (news, disruptions, prices, weather, strikes, delays), rely heavily on the web search.
- If the question is conceptual, rely on the internal KB.
- Never mention the words “context”, “retriever”, “documents”, “PDF”, or “search”.
- Answer only supply chain–related questions. Politely decline unrelated topics.
- Write like a senior supply chain consultant: concise, authoritative, and practical.

---

### Internal Knowledge:
{context}

### Real-Time Web Search:
{web}

### User Question:
{question}

### Expert Answer:
""")

    rag_chain = (
        {
            "context": lambda x: retriever.invoke(x["question"]),
            "web": lambda x: tavily_search(x["question"]),
            "question": lambda x: x["question"]
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def answer_question(user_question):
    vectordb = Chroma(
        persist_directory=f"{working_dir}/doc_vectorstore",
        embedding_function=embedding
    )

    retriever = vectordb.as_retriever()

    rag_chain = build_rag_chain(llm, retriever)

    return rag_chain.invoke({"question": user_question})
