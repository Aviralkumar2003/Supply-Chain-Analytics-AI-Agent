import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.analysis_service import AnalysisService


# ---------------------------------------------------
# Page Config
# ---------------------------------------------------

st.set_page_config(
    page_title="Supply Chain Analytics AI Agent",
    layout="wide"
)


# ---------------------------------------------------
# Title
# ---------------------------------------------------

st.title("Supply Chain Analytics AI Agent")
st.caption("AI-powered analysis of supply chain data using natural language queries")


# ---------------------------------------------------
# Session State
# ---------------------------------------------------

if "service" not in st.session_state:
    st.session_state.service = AnalysisService()

if "steps" not in st.session_state:
    st.session_state.steps = []

if "final_answer" not in st.session_state:
    st.session_state.final_answer = None

if "final_sql" not in st.session_state:
    st.session_state.final_sql = None


# ---------------------------------------------------
# Helper: Step Labels
# ---------------------------------------------------

def readable_step(node, output):

    if node == "first_tool_call":
        return "Discovering database tables"

    if node == "tools":

        text = str(output)

        if "sql_db_list_tables" in text:
            return "Listing available tables"

        if "sql_db_schema" in text:
            return "Inspecting table schema"

        if "sql_db_query" in text:
            return "Executing SQL query"

        return "Running database tool"

    if node == "llm":
        return "Planning database query"

    if node == "capture_sql":
        return "SQL query generated"

    if node == "capture_final":
        return "Generating final answer"

    return f"Processing {node}"


# ---------------------------------------------------
# Question Input
# ---------------------------------------------------

st.subheader("Ask a Question")

question = st.text_input(
    "Enter your supply chain question",
    placeholder="Example: What are the top 5 customers by revenue?"
)

analyze = st.button("Analyze", type="primary")


# ---------------------------------------------------
# Execute Analysis
# ---------------------------------------------------

if analyze and question:

    status = st.status("Running analysis...", expanded=True)

    st.session_state.steps = []
    st.session_state.final_answer = None
    st.session_state.final_sql = None

    with status:

        for event in st.session_state.service.analyze_question_stream(question):

            step = event["step"]
            node = step["node"]
            output = step["output"]

            st.session_state.steps = event["steps"]
            st.session_state.final_answer = event["answer"]
            st.session_state.final_sql = event["sql"]

            status.write(readable_step(node, output))

        status.update(label="Analysis complete", state="complete")


# ---------------------------------------------------
# Results
# ---------------------------------------------------

if st.session_state.final_answer:

    st.divider()
    st.header("Results")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Answer")
        st.write(st.session_state.final_answer)

    with col2:
        if st.session_state.final_sql:
            st.subheader("SQL Query")
            st.code(st.session_state.final_sql, language="sql")


# ---------------------------------------------------
# Agent Trace
# ---------------------------------------------------

if st.session_state.steps:

    st.divider()
    st.header("Agent Execution Trace")

    step_labels = [
        f"{i+1}. {readable_step(s['node'], s['output'])}"
        for i, s in enumerate(st.session_state.steps)
    ]

    selected = st.selectbox("Select step to inspect", step_labels)

    index = step_labels.index(selected)
    step = st.session_state.steps[index]

    node = step["node"]
    output = step["output"]

    st.subheader("Step Details")

    if node == "capture_sql" and st.session_state.final_sql:
        st.code(st.session_state.final_sql, language="sql")

    elif node == "capture_final" and st.session_state.final_answer:
        st.write(st.session_state.final_answer)

    else:
        st.json(output)