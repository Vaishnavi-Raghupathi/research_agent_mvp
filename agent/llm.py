import os
import json
import hashlib
import pathlib
from dotenv import load_dotenv
from groq import Groq
from google.genai import Client, types

# Load .env from project root regardless of where script runs
env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

CACHE_FILE = pathlib.Path(__file__).parent.parent / "llm_cache.json"


def load_cache():
    if CACHE_FILE.exists():
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
    def __init__(self):
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",  # much higher TPD limit
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000  # cap output tokens
        )
        return response.choices[0].message.content.strip()



class GeminiLLM(LLM):
    def __init__(self):
        self.client = Client(api_key=os.environ["GEMINI_API_KEY"])

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",  # fixed — this one actually exists
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
        print("[Cache hit]")
        return cache[key]

    # Try Groq first
    try:
        result = GroqLLM().generate(prompt)
        cache[key] = result
        save_cache(cache)
        return result
    except Exception as e:
        print(f"[Groq failed] {e}")

    # Fallback to Gemini
    try:
        result = GeminiLLM().generate(prompt)
        cache[key] = result
        save_cache(cache)
        return result
    except Exception as e:
        print(f"[Gemini failed] {e}")

    raise RuntimeError("All LLM providers failed.")