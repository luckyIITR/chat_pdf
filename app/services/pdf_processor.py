import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.memory.store import save_vectorstore_for_session  # We'll define this next
import tempfile

def process_pdf(file, session_id: str):
    # 1. Load PDF
   # Step 1: Save to a temporary file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)

    with open(temp_path, "wb") as f:
        content = file.file.read()
        f.write(content)
        
    loader = PyPDFLoader(temp_path)
    pages = loader.load()

    # 2. Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.split_documents(pages)

    # 3. Create embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    # 4. Build FAISS vectorstore for this session
    vectorstore = FAISS.from_documents(docs, embedding=embeddings)

    # 5. Save vectorstore for the session
    save_vectorstore_for_session(session_id, vectorstore)