import os
import requests
import pathlib
from dotenv import load_dotenv

# Re-load .env path to ensure it works when run from any context
env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(env_path) 

API_KEY = os.getenv("PERPLEXITY_API_KEY") 


def summarize_text(text: str) -> str:
    if not API_KEY:
        raise ValueError("PERPLEXITY_API_KEY not found in environment variables.")

    url = "https://api.perplexity.ai/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        # FIXED: Using valid Perplexity model
        "model": "sonar-pro", 
        "messages": [
            {
                "role": "user",
                "content": (
                    "Summarize the following research text in 6–8 technical bullet points. "
                    "Focus on mathematical ideas, algorithm structure, and main contributions.\n\n"
                    f"TEXT:\n{text}"
                )
            }
        ],
        "max_tokens": 500
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()

        response_json = resp.json()
        if not response_json.get("choices"):
             raise ValueError(f"API response missing 'choices': {response_json}")
             
        return response_json["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        print(f"Perplexity API Request Failed: {e}")
        if 'resp' in locals():
            print(f"Response content: {resp.text}")
        raise
