import os
import streamlit as st
from rag_helper_utility_push import process_document_to_chroma_db, answer_question
import streamlit as st

from auth import require_subscription

from auth import require_subscription, create_customer_portal, logout

# Require subscription or trial
require_subscription()

st.markdown("""
<style>
/* Main app background */
.stApp {
    background-color: #A3B18A !important;   /* soft olive green */
}

/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #A3B18A !important;
}

/* Optional: remove white padding box around content */
div.block-container {
    background-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)


# Set working directory
working_dir = os.path.dirname(os.path.abspath(__file__))

# st.title("SupplyBhai - Your Supply Chain Assistant 🤖")
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

# st.markdown('<p class="small-text">⏳ Loading…</p>', unsafe_allow_html=True)



st.markdown(
    "<p style='color: green; font-size: 0.8rem;'>✔️ Knowledgebase updated!</p>",
    unsafe_allow_html=True
)

# -------------------------------
# 2. USER QUESTION INPUT
# -------------------------------

user_question = st.text_area("Ask your question about the knowledgebase")

if st.button("🗣 Answer"):
    answer = answer_question(user_question)

    st.markdown("SupplyBhai says")
    st.markdown(answer)

# Optional: Manage subscription + logout buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("⚙️Manage Subscription"):
        url = create_customer_portal(st.session_state.email)
        st.markdown(f"[Open Customer Portal]({url})")

with col2:
    if st.button("🔓 Logout"):
        logout()

