import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from services.analysis_service import AnalysisService


st.set_page_config(page_title="Supply Chain Analytics AI Agent", layout="wide")
st.title("Supply Chain Analytics AI Agent")

if "service" not in st.session_state:
    st.session_state["service"] = AnalysisService()


question = st.text_input("Ask a supply chain question:")


if st.button("Analyze") and question:

    with st.spinner("Analyzing..."):
        result = st.session_state["service"].analyze_question(question)

    answer = result.get("answer")
    sql_query = result.get("sql")

    if answer:
        st.subheader("Final Answer")
        st.write(answer)

    if sql_query:
        st.subheader("SQL Query Used")
        st.code(sql_query, language="sql")

    if not answer and not sql_query:
        st.error("No response generated.")