import os
import streamlit as st
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

MODEL_NAME = "openai/gpt-oss-120b"


def summarize_chunks(chunks):
    """Map step: Summarize each chunk independently."""
    chunk_summaries = []

    for chunk in chunks:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "Summarize the following text in 2-3 concise sentences.",
                },
                {"role": "user", "content": chunk},
            ],
            temperature=0,
        )
        chunk_summaries.append(response.choices[0].message.content)

    return chunk_summaries


def reduce_summaries(summaries):
    """Reduce step: Combine chunk summaries into a final summary."""
    combined = "\n\n".join(summaries)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "Combine these partial summaries into one cohesive, bullet-point "
                    "summary of the entire document. Highlight key concepts."
                ),
            },
            {"role": "user", "content": combined},
        ],
        temperature=0,
    )
    return response.choices[0].message.content


def summarize_document(chunks):
    """Orchestrates map-reduce summarization."""
    print("Mapping chunks...")
    partial_summaries = summarize_chunks(chunks)
    print("Reducing summaries...")
    final_summary = reduce_summaries(partial_summaries)
    return final_summary