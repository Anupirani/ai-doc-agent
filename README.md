# 📄 AI Document Agent

An AI-powered document assistant that lets you upload a document (PDF or TXT), ask questions about it, generate a structured summary, and solve math problems found in it. Built with **Streamlit**, **ChromaDB** (local vector store), **sentence-transformers** (local embeddings), and **Groq** (free-tier LLM inference via an OpenAI-compatible API).

---

## ✨ Features

- **Document Q&A (RAG)** — Upload a PDF or TXT file, and ask natural-language questions. Answers are grounded strictly in the uploaded document, with retrieved context.
- **Map-Reduce Summarization** — Long documents are summarized chunk-by-chunk, then merged into one cohesive bullet-point summary. This avoids context-window limits on large files.
- **Math Solving** — Math-related questions are routed to a code-generation agent that writes and executes Python to compute the answer, then explains the result in plain language.
- **Local Embeddings** — Uses `all-MiniLM-L6-v2` via `sentence-transformers`, so embedding costs nothing and runs offline.
- **Free LLM Inference** — Powered by Groq's free tier (`openai/gpt-oss-120b`, 1,000 requests/day), accessed through the OpenAI SDK.

---

## 🏗️ Architecture

User uploads file
↓
[ingest.py] → Extract text (PDF/TXT) → Split into chunks
↓
[rag_engine.py] → Embed chunks (local) → Store in ChromaDB
↓
User asks a question
↓
[Router in app.py]
├─ "calculate / solve / equation" → [math_solver.py] → Generate + execute Python → Explain result
├─ "summarize" → [summarizer.py] → Map-reduce summary
└─ anything else → [rag_engine.py] → Retrieve top-k chunks → LLM answer


---

## 📁 Project Structure

ai-doc-agent/
├── app.py # Streamlit UI and intent routing
├── ingest.py # File parsing and chunking
├── rag_engine.py # Vector indexing and RAG question answering
├── summarizer.py # Map-reduce document summarization
├── math_solver.py # Code-generating math solver
├── requirements.txt # Python dependencies
├── .env # Local API key (NOT committed)
├── .gitignore # Excludes .env and secrets
└── README.md


---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/ai-doc-agent.git
cd ai-doc-agent


---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/ai-doc-agent.git
cd ai-doc-agent

2. Install dependencies
bash
pip install -r requirements.txt
3. Add your Groq API key
Create a .env file in the project root:

env
GROQ_API_KEY=gsk_your_actual_groq_key_here
Get a free key at console.groq.com/keys — no credit card required.


4. Run the app
bash
streamlit run app.py
Open http://localhost:8501 in your browser.

☁️ Deploy to Streamlit Community Cloud
Push the project to a public GitHub repository. Make sure .env is excluded via .gitignore.

Go to share.streamlit.io and sign in with GitHub.

Click "Create app" → "Yup, I have an app".

Select your repository, branch (main), and main file (app.py).

Open "Advanced settings" → "Secrets" and paste:

toml
GROQ_API_KEY = "gsk_your_actual_groq_key_here"
Click "Deploy". The first build takes 2–5 minutes.

The code reads the key from st.secrets when deployed and from .env when run locally, so no code changes are needed between environments.

🔑 Environment Variables
Variable	Required	Description
GROQ_API_KEY	Yes	Groq API key for LLM inference (free tier)
🧰 Tech Stack
Layer	Tool
UI	Streamlit
LLM inference	Groq (openai/gpt-oss-120b) via OpenAI SDK
Embeddings	sentence-transformers (all-MiniLM-L6-v2)
Vector store	ChromaDB (in-memory)
PDF parsing	pypdf
Chunking	langchain-text-splitters
⚠️ Known Limitations
Scanned PDFs — pypdf cannot extract text from image-only PDFs. An OCR fallback (e.g., EasyOCR or Tesseract) would be needed for scanned documents.

Ephemeral storage on Streamlit Cloud — The ChromaDB index lives in memory and is not persisted between sessions. Users must re-upload their document after the app restarts.

Groq free-tier limits — 1,000 requests/day and 8,000 tokens/minute. Very large documents may hit the per-minute token cap during summarization; adding a short time.sleep() between chunk calls mitigates this.

Math execution safety — math_solver.py runs generated code with a restricted set of builtins. This is safe enough for a prototype but is not a sandbox. For production, execute generated code inside an isolated container (e.g., Docker or E2B).

Free-tier model stability — Free LLM tiers can return 503 (temporary overload) or 429 (quota exhausted). The app does not currently retry on these errors; adding exponential backoff is a recommended next step.

🗺️ Roadmap
□ Add exponential backoff retry for 429/503 responses
□ OCR fallback for scanned PDFs
□ Support for DOCX, PPTX, and CSV files
□ Persistent vector store (SQLite or hosted Chroma)
□ Sandboxed execution for the math solver
□ Source citation display in Q&A answers
📜 License
MIT License — free to use, modify, and distribute.

text

---

A few things worth knowing about this README:

- The **Known Limitations** section is deliberate. Recruiters and reviewers trust projects more when the author acknowledges trade-offs, and it signals you understand the difference between a prototype and a production system.
- The **Architecture** diagram gives anyone landing on the repo an instant mental model of how the pieces connect — this is the single most useful section for a non-technical reader.
- The **deployment section** mirrors exactly what you just did, so if you ever rebuild the project from scratch, you have a checklist.

Once you push this along with the three updated files and `app.py`, your repository will be fully self-documenting.



