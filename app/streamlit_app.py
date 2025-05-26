import streamlit as st
import requests

st.set_page_config(page_title="PDF Chatbot", layout="centered")
st.title("📄 Chat with your PDF")

# Backend API URL
API_URL = "http://localhost:8000"

# Session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF to begin chatting", type=["pdf"])
if uploaded_file and st.session_state.session_id is None:
    with st.spinner("Uploading and processing..."):
        response = requests.post(
            f"{API_URL}/upload",
            files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        )
        if response.ok:
            st.session_state.session_id = response.json()["session_id"]
            st.success("PDF processed! You can now ask questions.")
        else:
            st.error("Failed to upload PDF.")

# Chat interface
if st.session_state.session_id:
    user_input = st.chat_input("Ask a question about the PDF")
    if user_input:
        # Show user message
        st.session_state.chat_history.append(("user", user_input))

        with st.spinner("Thinking..."):
            res = requests.post(f"{API_URL}/chat", json={
                "message": user_input,
                "session_id": st.session_state.session_id
            })
            if res.ok:
                answer = res.json()["response"]
                st.session_state.chat_history.append(("bot", answer))
            else:
                st.session_state.chat_history.append(("bot", "Error: Failed to get response."))

    # Render chat history
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)