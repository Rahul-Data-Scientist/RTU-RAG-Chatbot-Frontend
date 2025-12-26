import streamlit as st
import json
import requests

BACKEND_URL = "http://localhost:8000/rag/query"

with open("semester_subjects.json", "r", encoding = "utf-8") as f:
    semester_subjects = json.load(f)

with open("subjects_mapping.json", "r", encoding = "utf-8") as f:
    subjects_mapping = json.load(f)
    
with open("subjects_units.json", "r", encoding = "utf-8") as f:
    subjects_units = json.load(f)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "semester" not in st.session_state:
    st.session_state.semester = 5

if "subject" not in st.session_state:
    st.session_state.subject = "Analysis of Algorithms"

if "unit" not in st.session_state:
    st.session_state.unit = 2


st.sidebar.title("📚 Course Selection")

semester = st.sidebar.selectbox("Select Semester", options = list(semester_subjects.keys()))
subject = st.sidebar.selectbox("Select Subject", options = semester_subjects[semester])
unit = st.sidebar.selectbox("Select Unit", options = subjects_units[subjects_mapping[subject]])

st.session_state.semester = semester
st.session_state.subject = subject
st.session_state.unit = unit

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Current Scope")
st.sidebar.markdown(f"""
- **Semester:** {st.session_state.semester}
- **Subject:** {st.session_state.subject}
- **Unit:** {st.session_state.unit}
""")

st.title("📘 RAG Query Chatbot")

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Ask a question...")

if query:
    with st.chat_message("user"):
        st.markdown(query)
    
    payload = {
        "query": query,
        "chat_history": st.session_state.chat_history,
        "filters": {
            "semester": st.session_state.semester,
            "subject": subjects_mapping[st.session_state.subject],
            "unit": st.session_state.unit
        }
    }
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        streamed_text = ""
        try:
            with requests.post(
                BACKEND_URL,
                json = payload,
                stream = True,
                timeout = 120
            ) as response:
                response.raise_for_status()
                
                for chunk in response.iter_content(decode_unicode = True):
                    if chunk:
                        streamed_text += chunk
                        placeholder.markdown(streamed_text, unsafe_allow_html = True)
        except Exception as e:
            streamed_text = f"❌ Backend error: {e}"
            placeholder.markdown(streamed_text)
    
    st.session_state.chat_history.append({
        "role": "user",
        "content": query
    })
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": streamed_text
    })

