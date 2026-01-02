import os
import streamlit as st
from rag_helper_utility import process_document_to_chroma_db, answer_question

# Set working directory
working_dir = os.path.dirname(os.path.abspath(__file__))

st.title("Jyotbot - Your Indian Astrology Assistant")
st.subheader("Get unbialsed answer based on Vedic Astrology knowledge not what a human thinks! ")

# -------------------------------
# 1. AUTO-LOAD ALL PDFs FROM FOLDER
# -------------------------------

st.subheader("Loading Please wait ...  ")

doc_folder = os.path.join(working_dir, "doc_to_upload")

# Ensure folder exists
if not os.path.exists(doc_folder):
    st.error(f"Folder not found: {doc_folder}")
else:
    for file in os.listdir(doc_folder):
        if file.endswith(".pdf"):
            file_path = os.path.join(doc_folder, file)
            process_document_to_chroma_db(file_path)

    st.success("All documents processed and added to ChromaDB!")

# -------------------------------
# 2. USER QUESTION INPUT
# -------------------------------

user_question = st.text_area("Ask your question about the knowledgebase")

if st.button("Answer"):
    answer = answer_question(user_question)

    st.markdown("### Jyotbot says")
    st.markdown(answer)
