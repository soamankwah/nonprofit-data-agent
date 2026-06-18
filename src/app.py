"""
app.py
Streamlit chat interface for nonprofit staff to query their data
using plain English. No SQL knowledge required.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from agent import answer_question
from pipeline_checker import run_checks, explain_issues

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nonprofit Data Assistant",
    page_icon="📊",
    layout="centered"
)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("📊 Nonprofit Data Assistant")
st.caption("Ask questions about your program data in plain English. No SQL needed.")

# ── Sidebar: Pipeline Check ───────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Daily Data Check")
    st.write("Run automated checks to find data quality issues.")

    if st.button("▶ Run Pipeline Check", use_container_width=True, type="primary"):
        with st.spinner("Checking your data..."):
            issues = run_checks()
            report = explain_issues(issues)
        st.success(f"Found {len(issues)} issue(s)")
        st.markdown("### Report")
        st.markdown(report)

    st.divider()
    st.markdown("**Example questions to try:**")
    example_questions = [
        "Which clients have missed more than one appointment?",
        "How many active clients does each case worker have?",
        "Show me clients who haven't been updated in 30 days.",
        "Which programs have the most no-shows?",
        "List all clients with Pending status.",
    ]
    for q in example_questions:
        if st.button(q, key=q, use_container_width=True):
            st.session_state.pending_question = q

# ── Chat history ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Hello! I'm your data assistant. Ask me anything about your program clients, appointments, or outcomes — in plain English. For example: *'Which clients missed more than two appointments this month?'*"
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Handle sidebar button clicks ─────────────────────────────────────────────
if "pending_question" in st.session_state:
    prompt = st.session_state.pending_question
    del st.session_state.pending_question

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Looking that up..."):
            history = [{"role": m["role"], "content": m["content"]}
                       for m in st.session_state.messages[:-1]]
            response = answer_question(prompt, history)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

# ── Main chat input ───────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about your program data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Looking that up..."):
            history = [{"role": m["role"], "content": m["content"]}
                       for m in st.session_state.messages[:-1]]
            response = answer_question(prompt, history)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
