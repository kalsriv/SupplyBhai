import os
import streamlit as st
from langchain_groq import ChatGroq
from rag_helper_utility_push import process_document_to_chroma_db, answer_question
from auth import require_subscription, create_customer_portal, logout
import pandas as pd

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

# st.title("SupplyBhai - Your Real Time Supply Chain Assistant 🤖")
st.subheader("Ask questions about your global supply chain 📦 🌐")

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

st.markdown(
    "<p style='color: green; font-size: 0.8rem;'>✔️ Knowledgebase updated!</p>",
    unsafe_allow_html=True
)

# -------------------------------
# 2. USER QUESTION INPUT
# -------------------------------

user_question = st.text_area("Ask your question about the global supply chain Knowledgebase: you can also include the topics like Real-time Port disruptions, Current Tarrif, Strike updates, Weather impacts and Company announcements",)

if st.button("🗣 Answer"):
    answer = answer_question(user_question)

    st.markdown("SupplyBhai says")
    st.markdown(answer)

if st.button("🧹 Clear"): 
    st.session_state["user_question"] = "" 

# -------------------------------
# 3. EXCEL ANALYSIS MODULE
# -------------------------------

with st.expander("➕ Upload Excel for Analysis", expanded=False):
    uploaded_excel = st.file_uploader(
        "",
        type=["xlsx", "xls"],
        label_visibility="collapsed"
    )

    if uploaded_excel:
        import pandas as pd
        df = pd.read_excel(uploaded_excel)
        st.success("Excel file uploaded successfully!")

        st.write("### 🔍 Data Preview")
        st.dataframe(df.head())

        from excel_analysis import analyze_supply_chain_excel
        results = analyze_supply_chain_excel(df)

        st.write("### 📈 Key Insights")
        st.json(results)

        if st.button("🧠 Explain These Insights"):
            explanation_prompt = f"""
            You are SupplyBhai, a senior global supply chain consultant.
            Explain the following Excel analysis to a supply chain manager.
            When expliaining, use simple terms and avoid shwing tons of data points, 
            focus on high level insights and recommendations, not raw data, provide 
            a human friendly explanation of the observations.
        

            {results}
            """
            explanation = llm.invoke(explanation_prompt)
            st.write(explanation)


if uploaded_excel:

    df = pd.read_excel(uploaded_excel)
    st.success("Excel file uploaded successfully!")

    st.write("### 🔍 Data Preview")
    st.dataframe(df.head())

    # Run analysis
    from excel_analysis import analyze_supply_chain_excel
    results = analyze_supply_chain_excel(df)

    st.write("### 📈 Key Insights")
    st.json(results)
llm = ChatGroq( model="llama-3.3-70b-versatile", temperature=0.0, api_key=st.secrets["GROQ_API_KEY"] )
    # Optional: Ask SupplyBhai to explain the results
if st.button("🧠 Explain my excel sheet"):
        explanation_prompt = f"""
        You are SupplyBhai, a senior global supply chain consultant.
        Explain the following Excel analysis to a supply chain manager:

        {results}
        """
        explanation = llm.invoke(explanation_prompt)
        st.write(explanation)



# Optional: Manage subscription + logout buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("⚙️Manage Subscription"):
        url = create_customer_portal(st.session_state.email)
        st.markdown(f"[Open Customer Portal]({url})")

# with col2:
#     if st.button("🔓 Logout"):
#         logout()

with col2:
    if st.button("🔓 Logout"):
        st.session_state.clear()
        st.rerun()

        

