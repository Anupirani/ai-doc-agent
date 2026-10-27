import os
import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Key loading: st.secrets first (cloud), then .env (local) ---
try:
    groq_key = st.secrets["GROQ_API_KEY"]
except (KeyError, FileNotFoundError):
    groq_key = os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=groq_key,
    base_url="https://api.groq.com/openai/v1"
)

chroma_client = chromadb.Client()

# Local embedding model — do NOT use a Groq model name here
default_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

MODEL_NAME = "openai/gpt-oss-120b"


def get_or_create_collection(name="documents"):
    return chroma_client.get_or_create_collection(
        name=name,
        embedding_function=default_ef
    )


def index_document(chunks, collection_name="documents"):
    """Adds document chunks to the vector database."""
    collection = get_or_create_collection(collection_name)

    # Clear old data so a new upload doesn't mix with the previous document
    existing = collection.get()
    if existing and existing.get("ids"):
        collection.delete(ids=existing["ids"])

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids)
    return collection.count()


def query_rag(question, collection_name="documents", top_k=3):
    """Retrieves context and generates an answer."""
    collection = get_or_create_collection(collection_name)

    results = collection.query(query_texts=[question], n_results=top_k)

    if not results["documents"] or not results["documents"][0]:
        return "No relevant context found in the uploaded documents."

    context = "\n\n".join(results["documents"][0])

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer the user's question based ONLY on the provided context. "
                    "If the answer is not in the context, say you don't know."
                ),
            },
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0,
    )
    return response.choices[0].message.content