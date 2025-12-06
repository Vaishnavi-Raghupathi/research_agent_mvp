import os
import requests
from dotenv import load_dotenv
import pathlib
import json
import time
import re

# Fix env loading: Ensures it loads correctly regardless of where the script is run
env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# --- Configuration ---
API_KEY = os.getenv("PERPLEXITY_API_KEY")
# Use valid Perplexity models (updated Dec 2024)
# Option 1: Use sonar-pro for both (most capable)
GENERATE_MODEL = "sonar-pro"
FIX_MODEL = "sonar"

# Option 2: Use llama models if sonar-pro doesn't work
# GENERATE_MODEL = "llama-3.1-sonar-large-128k-chat"
# FIX_MODEL = "llama-3.1-sonar-small-128k-chat"

def extract_code_from_response(text: str) -> str:
    """
    Aggressively extract only Python code from LLM response.
    Handles cases where model adds explanatory text.
    """
    # First try: Look for markdown code blocks
    code_blocks = re.findall(r'```(?:python)?\s*\n(.*?)```', text, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()
    
    # Second try: Find lines that look like Python code
    lines = text.split('\n')
    code_lines = []
    in_code = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines before code starts
        if not stripped and not in_code:
            continue
            
        # Skip numbered lists and bullet points (common in explanations)
        if re.match(r'^\d+\.|^-\s|^\*\s', stripped):
            continue
        
        # Skip obvious prose (starts with common English words or phrases)
        prose_starters = ('The ', 'To ', 'This ', 'Here ', 'Let ', 'I ', 'You ', 
                         'We ', 'It ', 'Note ', 'In ', 'For ', 'With ', 'An ',
                         'Using ', 'Based ', 'First ', 'Second ', 'Each ')
        if any(stripped.startswith(s) for s in prose_starters):
            continue
        
        # Look for Python-like patterns to start code detection
        python_patterns = (
            stripped.startswith(('import ', 'from ', 'def ', 'class ', '#', '@')),
            '=' in stripped and not stripped.startswith(('=', '==')),
            stripped.startswith(('if ', 'for ', 'while ', 'try:', 'except', 'with ')),
            stripped.endswith(':') and any(kw in stripped for kw in ['def', 'class', 'if', 'for', 'while'])
        )
        
        if any(python_patterns):
            in_code = True
            
        if in_code and stripped:
            code_lines.append(line)
    
    if code_lines:
        return '\n'.join(code_lines)
    
    # Last resort: return original and hope for the best
    return text.strip()


def pplx_chat(prompt: str, model: str, max_retries=3):
    """Low-level wrapper for Perplexity API with retry logic."""
    if not API_KEY:
        raise ValueError("PERPLEXITY_API_KEY not found in environment variables.")

    url = "https://api.perplexity.ai/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.1  # Very low temperature for strict code generation
    }

    for attempt in range(max_retries):
        try:
            timeout = 60 + (attempt * 30)
            
            print(f"API call attempt {attempt + 1}/{max_retries} (timeout: {timeout}s)...")
            
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            
            response_json = resp.json()
            if not response_json.get("choices"):
                raise ValueError(f"API response missing 'choices': {response_json}")
                 
            return response_json["choices"][0]["message"]["content"]
            
        except requests.exceptions.Timeout as e:
            print(f"⏱️ Timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"❌ All retries exhausted. Request failed.")
                raise
                
        except requests.exceptions.RequestException as e:
            print(f"Perplexity API Request Failed: {e}")
            if 'resp' in locals():
                print(f"Response content: {resp.text}")
            raise


# ----------------------------------------------------------
# 1. INITIAL CODE GENERATION
# ----------------------------------------------------------

def generate_code(summary: str, equations: list) -> str:
    """Generate initial code with extremely strict prompt."""
    
    # Limit equations to prevent token overflow
    eq_sample = equations[:8]
    eq_text = "\n".join(eq.get("cleaned", str(eq)) for eq in eq_sample)

    # ULTRA-STRICT prompt with system-level instructions
    prompt = f"""You are a code generator. Your ONLY job is to output valid Python code.

DO NOT write explanations.
DO NOT write "Here is the code".
DO NOT write "Let me analyze".
START with 'import' or '#' ONLY.

Research summary (first 800 chars):
{summary[:800]}

Key equations:
{eq_text}

Write Python code implementing this research. Start your response with 'import' or '#':"""

    raw = pplx_chat(prompt, model=GENERATE_MODEL)
    
    # Aggressively clean the response
    cleaned = extract_code_from_response(raw)
    cleaned = cleaned.replace("```python", "").replace("```", "").strip()
    
    # Debug: Show first 200 chars of what we got
    print(f"Generated code preview: {cleaned[:200]}...")
    
    return cleaned


# ----------------------------------------------------------
# 2. FIXING BROKEN CODE
# ----------------------------------------------------------

def fix_code(original_code: str, error_message: str) -> str:
    """Fix broken code with ultra-strict prompt."""
    
    # Truncate inputs to avoid token limits
    error_snippet = error_message[-400:] if len(error_message) > 400 else error_message
    code_snippet = original_code[:1500] if len(original_code) > 1500 else original_code
    
    prompt = f"""Fix this Python code. OUTPUT ONLY PYTHON CODE.

DO NOT explain.
DO NOT write "The error is".
DO NOT write "Here's the fix".
START with 'import' or '#' ONLY.

Error (last part):
{error_snippet}

Broken code:
{code_snippet}

Fixed Python code (start with 'import' or '#'):"""

    raw = pplx_chat(prompt, model=FIX_MODEL)
    
    # Aggressively clean the response
    cleaned = extract_code_from_response(raw)
    cleaned = cleaned.replace("```python", "").replace("```", "").strip()
    
    # Debug: Show first 200 chars
    print(f"Fixed code preview: {cleaned[:200]}...")
    
    return cleaned