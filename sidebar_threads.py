import streamlit as st
import requests


def render_threads_sidebar(
    chat_threads,
    backend_base,
    load_thread_history,
    start_new_chat,
):
    """
    Renders conversation list in sidebar.
    """

    THREADS_URL = f"{backend_base}/threads"

    st.sidebar.title("💬 Conversations")

    # New Chat Button
    if st.sidebar.button("➕ New Chat"):
        start_new_chat()

    for thread in chat_threads:
        thread_id = thread["thread_id"]

        is_active = st.session_state.thread_id == thread_id

        button_label = (
            f"🟢 {thread['title']}"
            if is_active else thread["title"]
        )

        col1, col2 = st.sidebar.columns([6, 1], gap="small")

        # ---------- OPEN THREAD ----------
        with col1:
            if st.button(
                button_label,
                key=f"open_{thread_id}",
                use_container_width=True,
            ):
                st.session_state.thread_id = thread_id
                st.session_state.chat_history = load_thread_history(
                    thread_id
                )
                st.session_state.open_menu_thread = None

        # ---------- MENU BUTTON ----------
        with col2:
            if st.button("⋮", key=f"menu_{thread_id}"):

                if st.session_state.open_menu_thread == thread_id:
                    st.session_state.open_menu_thread = None
                    st.session_state.renaming_thread = None
                else:
                    st.session_state.open_menu_thread = thread_id
                    st.session_state.renaming_thread = None

        # ---------- MENU CONTENT ----------
        if st.session_state.open_menu_thread == thread_id:

            # DELETE
            if st.sidebar.button(
                "🗑️ Delete conversation",
                key=f"delete_{thread_id}",
                use_container_width=True,
            ):
                requests.delete(
                    f"{backend_base}/threads/{thread_id}"
                )

                r = requests.get(THREADS_URL)
                st.session_state.chat_threads = r.json()["threads"]

                if st.session_state.thread_id == thread_id:
                    start_new_chat()

                st.session_state.open_menu_thread = None
                st.rerun()

            # RENAME BUTTON
            if st.sidebar.button(
                "✏️ Rename",
                key=f"rename_{thread_id}",
                use_container_width=True,
            ):
                st.session_state.renaming_thread = thread_id

            # RENAME INPUT
            if st.session_state.renaming_thread == thread_id:

                new_title = st.sidebar.text_input(
                    "Enter new title",
                    value=thread["title"],
                    key=f"rename_input_{thread_id}",
                )

                col_save, col_cancel = st.sidebar.columns(2)

                with col_save:
                    if st.button("✅ Save", key=f"save_{thread_id}"):

                        requests.patch(
                            f"{backend_base}/threads/{thread_id}/rename",
                            json={"title": new_title},
                        )

                        r = requests.get(THREADS_URL)
                        st.session_state.chat_threads = r.json()["threads"]

                        st.session_state.renaming_thread = None
                        st.session_state.open_menu_thread = None

                        st.rerun()

                with col_cancel:
                    if st.button("❌ Cancel", key=f"cancel_{thread_id}"):
                        st.session_state.renaming_thread = None
                        st.rerun()