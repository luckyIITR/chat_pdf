# 📄 PDF Chatbot: Streamlit + FastAPI + LangGraph

This project is a document-based chatbot built using:

* 🧠 LangGraph (LangChain)
* 🔥 FastAPI (backend API for PDF upload and chat)
* 🎨 Streamlit (frontend for user interaction)

It allows users to upload a PDF and chat with it using retrieval-augmented generation (RAG).

---

## 🧱 Architecture Overview

```
User ↔ Streamlit UI ↔ FastAPI Backend ↔ LangGraph ↔ PDF VectorStore
```

* `Streamlit`: User-facing app
* `FastAPI`: API endpoints `/upload` and `/chat`
* `LangGraph`: Manages tool use and conversation logic
* `FAISS`: Stores embedded chunks of uploaded PDFs
* `OpenAI API`: Used for both embeddings and chat generation

---

## 🔧 Project Structure

```
qa_chat_app/
├── app/
│   ├── main.py                # FastAPI entry
│   ├── routes/
│   │   ├── upload.py          # /upload route
│   │   └── chat.py            # /chat route
│   ├── services/
│   │   ├── graph_builder.py   # LangGraph logic
│   │   ├── graph.py           # Compiles and runs graph
│   │   └── pdf_processor.py   # Loads, splits, embeds PDF
│   ├── memory/
│   │   └── store.py           # In-memory session data store
│   └── models/
│       └── schemas.py         # Pydantic models
├── streamlit_app.py          # UI app
├── requirements.txt
├── Dockerfile (optional)
├── .env                      # API keys
```

---

## ⚙️ How It Works

### 1. Upload PDF

* Endpoint: `POST /upload`
* Uses `PyPDFLoader` to extract text
* Splits content using `RecursiveCharacterTextSplitter`
* Embeds chunks using `OpenAIEmbeddings`
* Stores them in an in-memory FAISS vector store
* Assigns a `session_id` (UUID) to track the chat session

### 2. Chat with the Document

* Endpoint: `POST /chat`
* Accepts `message` and `session_id`
* Runs LangGraph with:

  * LLM (OpenAI chat model)
  * Tool (`retrieve(query, session_id)`) bound with session\_id
* Retrieves relevant chunks
* Responds concisely using the context

### 3. Frontend (Streamlit)

* User uploads PDF and gets a session ID
* Asks questions about the document
* UI shows real-time feedback: "Retrieving...", then answer

---

## 📡 Backend Endpoints

### `/upload` (POST)

Uploads and indexes a PDF.

```bash
curl -X POST -F "file=@example.pdf" http://localhost:8000/upload
```

Returns:

```json
{
  "message": "PDF processed successfully.",
  "session_id": "abc123"
}
```

### `/chat` (POST)

Chats using the uploaded PDF.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is this document about?", "session_id": "abc123"}'
```

---

## 🧠 LangGraph Flow

### Tool:

```python
@tool(args_schema={"query": str, "session_id": str})
def retrieve(query, session_id):
    vectorstore = get_vectorstore_for_session(session_id)
    docs = vectorstore.similarity_search(query)
    return formatted_content, docs
```

### Nodes:

* `query_or_respond`: LLM decides whether to answer or call `retrieve`
* `tools`: Executes tool
* `generate`: Responds using retrieved content

### Injecting session\_id

In `query_or_respond()`:

```python
retrieve_with_session = retrieve.bind(session_id=session_id)
llm_with_tools = llm.bind_tools([retrieve_with_session])
response = llm_with_tools.invoke(state["messages"])
```

---

## 💻 Streamlit Frontend

### Key Features

* Uploads PDF to backend
* Chats with session-aware context
* Shows intermediate states like "Retrieving..."

### Example snippet

```python
with st.chat_message("bot"):
    placeholder = st.empty()
    placeholder.markdown("_Retrieving relevant information..._")

response = requests.post(...)
placeholder.markdown(response.text)
```

---

## 🚀 Deployment Guide

### 🔹 Option: Render.com (Easy, Free)

* Create two web services:

  * One for FastAPI (`uvicorn app.main:app`)
  * One for Streamlit (`streamlit run streamlit_app.py`)
* Set environment variables:

  * `OPENAI_API_KEY`, `LANGSMITH_API_KEY`
* Set `API_URL` in Streamlit to point to the FastAPI endpoint

### 🔹 Option: Docker

#### `Dockerfile` (FastAPI or Streamlit)

```Dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ✅ Tips & Extensibility

* Add SQLite-based persistent FAISS
* Add multiple tool types (e.g., summarization)
* Log all user questions and retrieved docs
* Show source documents in chat UI

---

## 🙋 FAQ

**Q: Can I upload multiple PDFs?**

> You can extend session logic to support multiple vectorstores per session.

**Q: Will this retain memory across sessions?**

> Currently memory is in-memory. You can persist with `faiss.write_index()`.

**Q: Can I add citation or source highlighting?**

> Yes. Include doc metadata in `retrieve()` and show it in Streamlit.
