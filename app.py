import streamlit as st
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from openai import AuthenticationError

load_dotenv(Path(__file__).resolve().with_name(".env"), override=True)

from ingest import extract_text_from_file, chunk_text
from rag_engine import index_document, query_rag
from summarizer import summarize_document
from math_solver import solve_math

st.set_page_config(page_title="AI Document Agent", layout="wide")
st.title("📄 AI Document Agent")

def show_authentication_error():
    st.error(
        "OpenAI rejected the API key. Replace OPENAI_API_KEY in the project's "
        ".env file with a valid key from https://platform.openai.com/api-keys, "
        "then restart Streamlit."
    )

# Initialize session state
if "document_indexed" not in st.session_state:
    st.session_state.document_indexed = False
if "chunks" not in st.session_state:
    st.session_state.chunks = []

# Sidebar: File Upload
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"])
    
    if uploaded_file is not None:
        if st.button("Process Document"):
            with st.spinner("Extracting and indexing..."):
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                # Process
                try:
                    raw_text = extract_text_from_file(tmp_path)
                    chunks = chunk_text(raw_text)
                    st.session_state.chunks = chunks
                    
                    # Index for RAG
                    index_document(chunks)
                    st.session_state.document_indexed = True
                    st.success(f"Indexed {len(chunks)} chunks!")
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    os.unlink(tmp_path)
    
    if st.session_state.document_indexed:
        st.info("Document ready. Ask questions below.")
        if st.button("Generate Summary"):
            with st.spinner("Summarizing..."):
                try:
                    summary = summarize_document(st.session_state.chunks)
                    st.session_state.summary = summary
                    st.write(summary)
                except AuthenticationError:
                    show_authentication_error()

# Main Chat Area
if st.session_state.document_indexed:
    user_input = st.chat_input("Ask a question about the document...")
    
    if user_input:
        st.chat_message("user").write(user_input)
        try:
            # Check for math intent
            if any(word in user_input.lower() for word in ["calculate", "solve", "equation", "math"]):
                response = solve_math(user_input)
            else:
                response = query_rag(user_input)

            st.chat_message("assistant").write(response)
        except AuthenticationError:
            with st.chat_message("assistant"):
                show_authentication_error()
else:
    st.info("👈 Please upload and process a document to get started.")