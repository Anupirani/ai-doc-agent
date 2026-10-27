import os
import io
import contextlib
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

# Whitelisted builtins so generated code can do math but not touch the filesystem
SAFE_BUILTINS = {
    "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
    "len": len, "range": range, "print": print, "pow": pow,
    "int": int, "float": float, "complex": complex, "bool": bool,
    "list": list, "dict": dict, "tuple": tuple, "set": set, "str": str,
    "enumerate": enumerate, "zip": zip, "sorted": sorted, "divmod": divmod,
}


def _extract_code(text):
    """Pulls the Python code out of the LLM's markdown response."""
    if "```python" in text:
        return text.split("```python")[1].split("```")[0]
    if "```" in text:
        return text.split("```")[1].split("```")[0]
    return text


def solve_math(problem):
    """Asks the LLM to write Python, executes it, and returns the real result."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a math solver. Write Python code that solves the user's "
                    "problem and PRINTS the final numeric answer. Output ONLY code inside "
                    "```python ... ``` tags, no explanations. Use only standard math "
                    "functions and the `math` module (import math). Always use print()."
                ),
            },
            {"role": "user", "content": problem},
        ],
        temperature=0,
    )

    code = _extract_code(response.choices[0].message.content)

    # Capture whatever the code prints
    output_buffer = io.StringIO()
    local_vars = {"math": __import__("math")}

    try:
        with contextlib.redirect_stdout(output_buffer):
            exec(code, {"__builtins__": SAFE_BUILTINS, "math": local_vars["math"]}, local_vars)
        printed = output_buffer.getvalue().strip()
    except Exception as e:
        return f"Error executing math code: {e}\n\nGenerated code:\n{code}"

    # If the code didn't print, try to find a result variable
    if not printed:
        for key, value in local_vars.items():
            if key != "math" and not key.startswith("_"):
                printed = f"{key} = {value}"
                break

    if not printed:
        return f"No output produced.\n\nGenerated code:\n{code}"

    # Ask the LLM to present the result nicely
    explanation = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "Explain the math solution clearly in 2-4 sentences using the computed result.",
            },
            {
                "role": "user",
                "content": f"Problem: {problem}\n\nComputed result:\n{printed}",
            },
        ],
        temperature=0,
    )

    return f"{explanation.choices[0].message.content}\n\n**Computed result:** `{printed}`"