import streamlit as st
import json
import requests
import uuid
from datetime import datetime
from sidebar_threads import render_threads_sidebar

# ===================== CONFIG =====================
st.set_page_config(page_title="RTU RAG Chatbot")

st.markdown("""
<style>

/* Remove vertical gaps between sidebar buttons */
section[data-testid="stSidebar"] .stButton {
    margin-bottom: -8px;
}

/* Default button style */
section[data-testid="stSidebar"] .stButton button {
    width: 100%;
    text-align: left;
    border-radius: 8px;
}

/* ACTIVE THREAD HIGHLIGHT */
section[data-testid="stSidebar"] .stButton button[kind="secondary"].active-thread {
    background-color: #2E86C1 !important;
    color: white !important;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

BACKEND_BASE = "http://44.213.105.128:8000"

RAG_URL = f"{BACKEND_BASE}/rag/query"
THREADS_URL = f"{BACKEND_BASE}/threads"
THREAD_HISTORY_URL = f"{BACKEND_BASE}/threads"

# ===================== LOAD STATIC DATA =====================
with open("semester_subjects.json", "r", encoding="utf-8") as f:
    semester_subjects = json.load(f)

with open("subjects_mapping.json", "r", encoding="utf-8") as f:
    subjects_mapping = json.load(f)

with open("subjects_units.json", "r", encoding="utf-8") as f:
    subjects_units = json.load(f)

# ===================== SESSION STATE =====================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "chat_threads" not in st.session_state:
    try:
        r = requests.get(THREADS_URL, timeout=10)
        st.session_state.chat_threads = r.json()["threads"]
    except:
        st.session_state.chat_threads = []

if "semester" not in st.session_state:
    st.session_state.semester = 5

if "subject" not in st.session_state:
    st.session_state.subject = "Analysis of Algorithms"

if "unit" not in st.session_state:
    st.session_state.unit = 2

if "thread_registered" not in st.session_state:
    st.session_state.thread_registered = False

if "open_menu_thread" not in st.session_state:
    st.session_state.open_menu_thread = None

if "renaming_thread" not in st.session_state:
    st.session_state.renaming_thread = None


# ===================== UTILITIES =====================
def load_thread_history(thread_id):
    """Fetch conversation from backend"""
    try:
        r = requests.get(f"{THREAD_HISTORY_URL}/{thread_id}", timeout=10)
        return r.json()["messages"]
    except:
        return []


def start_new_chat():
    new_thread = str(uuid.uuid4())
    st.session_state.thread_id = new_thread
    st.session_state.chat_history = []
    st.session_state.thread_registered = False


# ===================== SIDEBAR =====================
st.sidebar.title("📚 Course Selection")

semester = st.sidebar.selectbox(
    "Select Semester",
    options=list(semester_subjects.keys()),
)

subject = st.sidebar.selectbox(
    "Select Subject",
    options=semester_subjects[semester],
)

unit = st.sidebar.selectbox(
    "Select Unit",
    options=subjects_units[subjects_mapping[subject]],
)

st.session_state.semester = semester
st.session_state.subject = subject
st.session_state.unit = unit

st.sidebar.markdown("---")

# ===================== CONVERSATIONS =====================
render_threads_sidebar(
    chat_threads=st.session_state.chat_threads,
    backend_base=BACKEND_BASE,
    load_thread_history=load_thread_history,
    start_new_chat=start_new_chat,
)


st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Current Scope")
st.sidebar.markdown(f"""
- **Semester:** {semester}
- **Subject:** {subject}
- **Unit:** {unit}
""")

# ===================== MAIN UI =====================
st.header("📘 Syllabus-Aware AI Tutor (RAG Powered)")

# Display history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ===================== CHAT INPUT =====================
query = st.chat_input("Ask a question...")

if query:
    # ---- show user message ----
    with st.chat_message("user"):
        st.markdown(query)

    st.session_state.chat_history.append(
        {"role": "user", "content": query}
    )

    payload = {
        "query": query,
        "semester": st.session_state.semester,
        "subject": subjects_mapping[st.session_state.subject],
        "unit": st.session_state.unit,
        "thread_id": st.session_state.thread_id,
    }

    # ---- assistant streaming ----
    with st.chat_message("assistant"):
        placeholder = st.empty()
        streamed_text = ""

        try:
            with requests.post(
                RAG_URL,
                json=payload,
                stream=True,
                timeout=180,
            ) as response:

                response.raise_for_status()

                for chunk in response.iter_content(
                    decode_unicode=True
                ):
                    if chunk:
                        streamed_text += chunk
                        placeholder.markdown(streamed_text)

        except Exception as e:
            streamed_text = f"❌ Backend error: {e}"
            placeholder.markdown(streamed_text)

    st.session_state.chat_history.append(
        {"role": "assistant", "content": streamed_text}
    )

    if not st.session_state.thread_registered:
        try:
            r = requests.get(THREADS_URL, timeout = 10)
            st.session_state.chat_threads = r.json()['threads']

            st.session_state.thread_registered = True

            # refresh UI once
            st.rerun()
        except Exception:
            pass