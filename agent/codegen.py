import os
from dotenv import load_dotenv
import pathlib
import re
import google.genai as genai
from google.genai import Client, types
from groq import Groq
import json
import hashlib

# Fix env loading: Ensures it loads correctly regardless of where the script is run
env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

CACHE_FILE = "llm_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def get_cache_key(prompt: str) -> str:
    return hashlib.md5(prompt.encode()).hexdigest()

class LLM:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

class GroqLLM(LLM):
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

class GeminiLLM(LLM):
    def __init__(self, api_key: str):
        self.client = Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.9,
                top_k=40
            )
        )
        return response.text.strip()

def generate_response(prompt: str) -> str:
    cache = load_cache()
    key = get_cache_key(prompt)

    if key in cache:
        return cache[key]

    try:
        groq = GroqLLM(api_key=os.environ["GROQ_API_KEY"])
        result = groq.generate(prompt)
        cache[key] = result
        save_cache(cache)
        return result
    except Exception as e:
        print(f"Error: {e}")
        try:
            gemini = GeminiLLM(api_key=os.environ["GEMINI_API_KEY"])
            result = gemini.generate(prompt)
            cache[key] = result
            save_cache(cache)
            return result
        except Exception as e:
            print(f"Error: {e}")
            return "Error: All models failed."

def generate_code(summary: str, equations: list, text: str = "") -> str:
    """Generate initial code with enhanced context using fallback logic."""

    # Extract the first and last chunks of the text
    chunk_size = 3000
    first_chunk = text[:chunk_size]
    last_chunk = text[-chunk_size:] if len(text) > chunk_size else text

    equations_text = "\n".join(equations[:8])
    # ULTRA-STRICT prompt with system-level instructions
    prompt = f"""You are a code generator. Your ONLY job is to output valid Python code.

DO NOT write explanations.
DO NOT write \"Here is the code\".
DO NOT write \"Let me analyze\".
START with 'import' or '#' ONLY.

Research summary (first 800 chars):
{summary[:800]}

Key equations:
{equations_text}

Introduction and Problem Statement:
{first_chunk}

Conclusions and Results:
{last_chunk}

Write Python code implementing this research. Start your response with 'import' or '#':"""

    return generate_response(prompt)

def fix_code(original_code: str, error_message: str) -> str:
    """Fix broken code with ultra-strict prompt."""

    # Truncate inputs to avoid token limits
    error_snippet = error_message[-400:] if len(error_message) > 400 else error_message
    code_snippet = original_code[:1500] if len(original_code) > 1500 else original_code

    prompt = f"""Fix this Python code. OUTPUT ONLY PYTHON CODE.

DO NOT explain.
DO NOT write \"The error is\".
DO NOT write \"Here's the fix\".
START with 'import' or '#' ONLY.

Error (last part):
{error_snippet}

Broken code:
{code_snippet}

Fixed Python code (start with 'import' or '#'):"""

    return generate_response(prompt)