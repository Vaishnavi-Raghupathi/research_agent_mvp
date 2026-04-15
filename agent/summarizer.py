import os
import json
import hashlib
from google.genai import Client, types
from groq import Groq

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

def summarize_text(text: str) -> str:
    """
    Summarize the given text using the Gemini API.

    Args:
        text (str): The input text to summarize.

    Returns:
        str: The summarized text.
    """
    prompt = f"Summarize the following text in 2-3 bullet points:\n{text}"
    return generate_response(prompt)

def ask_question(text: str, question: str) -> str:
    """
    Answer a question based on the given text using the Gemini API.

    Args:
        text (str): The context text to base the answer on.
        question (str): The question to answer.

    Returns:
        str: The answer to the question.
    """
    prompt = f"Based on the following text, answer the question:\n\nTEXT:\n{text}\n\nQUESTION:\n{question}"
    return generate_response(prompt)
