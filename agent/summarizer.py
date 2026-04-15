from agent.llm import generate_response


def summarize_paper(text: str) -> str:
    prompt = f"""You are a research assistant. Summarize this academic paper clearly.

Include:
- Main objective / problem being solved
- Key methodology or approach
- Main findings or results
- Why this matters

Paper text:
{text[:6000]}

Write a clear, structured summary:"""
    return generate_response(prompt)


def ask_question(text: str, question: str) -> str:
    prompt = f"""Based on the following research paper, answer this question accurately.

PAPER (excerpt):
{text[:5000]}

QUESTION:
{question}

Answer:"""
    return generate_response(prompt)