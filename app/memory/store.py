from langchain_community.vectorstores import FAISS

# In-memory dict (for prototyping)
session_vectorstores = {}

def save_vectorstore_for_session(session_id: str, vectorstore: FAISS):
    session_vectorstores[session_id] = vectorstore

def get_vectorstore_for_session(session_id: str) -> FAISS:
    return session_vectorstores.get(session_id, None)

def session_exists(session_id: str) -> bool:
    return session_id in session_vectorstores