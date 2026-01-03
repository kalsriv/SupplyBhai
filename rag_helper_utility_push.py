import os
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

working_dir = os.path.dirname(os.path.abspath(__file__))

# Embeddings + LLM
embedding = HuggingFaceEmbeddings()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

# ---------------------------------------------------------
# PROCESS DOCUMENT → CHROMA VECTORSTORE
# ---------------------------------------------------------
def process_document_to_chroma_db(file_path):
    """
    Accepts a FULL file path.
    Loads PDF → splits → embeds → stores in Chroma.
    """

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=50
    )
    texts = text_splitter.split_documents(documents)

    Chroma.from_documents(
        documents=texts,
        embedding=embedding,
        persist_directory=f"{working_dir}/doc_vectorstore"
    )

    return 0

# ---------------------------------------------------------
# BUILD RAG CHAIN
# ---------------------------------------------------------
def build_rag_chain(llm, retriever):
    prompt = ChatPromptTemplate.from_template("""
    You are a supply chain expert. Use ONLY the retrieved context to answer.

    Context:
    {context}

    Question:
    {question}

    Answer:
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
