from agent.llm import generate_response
import re


def generate_code(summary: str, equations: list, text: str = "") -> str:
    chunk_size = 1500  # reduced from 3000
    first_chunk = text[:chunk_size]
    last_chunk = text[-chunk_size:] if len(text) > chunk_size else ""
    equations_text = "\n".join(
        (eq.get("cleaned", "") if isinstance(eq, dict) else str(eq))
        for eq in equations[:5]  # reduced from 8
    )

    prompt = f"""You are a Python code generator. Output ONLY valid Python code.

Rules:
- DO NOT write explanations or prose
- DO NOT use markdown fences like ```python
- START your response with 'import' or '#'
- Implement the research described below as runnable Python

Research summary:
{summary[:800]}

Key equations:
{equations_text}

Introduction:
{first_chunk}

Conclusions:
{last_chunk}

Python code:"""

    raw = generate_response(prompt)
    return clean_code_output(raw)


def fix_code(original_code: str, error_message: str) -> str:
    error_snippet = error_message[-400:]
    code_snippet = original_code[:1500]

    prompt = f"""Fix this broken Python code. Output ONLY the fixed Python code.

Rules:
- DO NOT explain anything
- DO NOT use markdown fences
- START with 'import' or '#'

Error:
{error_snippet}

Broken code:
{code_snippet}

Fixed code:"""

    raw = generate_response(prompt)
    return clean_code_output(raw)


def clean_code_output(code: str) -> str:
    """Strip markdown fences LLMs sometimes add despite instructions."""
    code = code.strip()
    code = re.sub(r"^```[a-zA-Z]*\n?", "", code)
    code = re.sub(r"\n?```$", "", code)
    return code.strip()