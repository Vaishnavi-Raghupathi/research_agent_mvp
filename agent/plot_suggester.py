import re
from agent.llm import generate_response


def suggest_plots(summary: str, equations: list, text: str = "") -> str:
    """
    Use LLM to suggest visualization code for the research paper.
    Returns Python plotting code as string.
    """
    eq_text = "\n".join([
        f"- {eq.get('cleaned', str(eq))}"
        for eq in equations[:5]
    ])

    prompt = f"""You are a Python data visualization expert. Generate matplotlib plotting code for this research paper.

SUMMARY:
{summary[:800]}

KEY EQUATIONS:
{eq_text}

RULES:
- Output ONLY Python code, no explanations
- DO NOT use markdown fences
- Start with 'import' or '#'
- Create 2-3 plots using plt.figure() for each
- Use synthetic/example data to illustrate the paper's concepts
- Add titles, axis labels, and legends to every plot

Python plotting code:"""

    raw = generate_response(prompt)
    return clean_plot_code(raw)


def clean_plot_code(code: str) -> str:
    """Strip markdown fences and prose from LLM response."""
    code = code.strip()
    code = re.sub(r"^```[a-zA-Z]*\n?", "", code)
    code = re.sub(r"\n?```$", "", code)

    # Strip leading prose lines
    lines = code.split('\n')
    clean_lines = []
    in_code = False

    for line in lines:
        stripped = line.strip()
        if not in_code:
            if stripped.startswith(('import ', 'from ', '#', 'def ', 'class ')):
                in_code = True
                clean_lines.append(line)
        else:
            clean_lines.append(line)

    return '\n'.join(clean_lines).strip() if clean_lines else code