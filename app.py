import os
import streamlit as st
from rag_helper_utility_push import process_document_to_chroma_db, answer_question

# Set working directory
working_dir = os.path.dirname(os.path.abspath(__file__))

st.title("SupplyBhai - Your Supply Chain Assistant 🤖")
st.subheader("Ask questions about your global supply chain documents")


# -------------------------------
# 1. AUTO-LOAD ALL PDFs FROM FOLDER
# -------------------------------

# st.subheader("Loading Please wait ...  ")

st.markdown("""
<style>
.small-text {
    font-size: 0.8rem;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="small-text">⏳ Loading…</p>', unsafe_allow_html=True)


# doc_folder = os.path.join(working_dir, "doc_to_upload")

# # Ensure folder exists
# if not os.path.exists(doc_folder):
#     st.error(f"Folder not found: {doc_folder}")
# else:
#     for file in os.listdir(doc_folder):
#         if file.endswith(".pdf"):
#             file_path = os.path.join(doc_folder, file)
#             process_document_to_chroma_db(file_path)

#     # st.success("Knowledgebase updated!")
st.markdown(
    "<p style='color: green; font-size: 0.8rem;'>✔️ Knowledgebase updated!</p>",
    unsafe_allow_html=True
)

# -------------------------------
# 2. USER QUESTION INPUT
# -------------------------------

user_question = st.text_area("Ask your question about the knowledgebase")

if st.button("Answer"):
    answer = answer_question(user_question)

    st.markdown("SupplyBhai says")
    st.markdown(answer)
