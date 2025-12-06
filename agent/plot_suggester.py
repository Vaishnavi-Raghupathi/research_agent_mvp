import re
from agent.codegen import pplx_chat

def extract_code_from_response(text: str) -> str:
    """
    Extract Python code from LLM response, removing explanatory text.
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
        
        # Skip obvious prose
        prose_starters = ('The ', 'To ', 'This ', 'Here ', 'Let ', 'I ', 'You ', 
                         'We ', 'It ', 'Note ', 'In ', 'For ', 'With ', 'An ',
                         'Using ', 'Based ', 'First ', 'Second ', 'Each ',
                         'Plot ', 'Figure ', 'These ', 'Create ')
        if any(stripped.startswith(s) for s in prose_starters):
            continue
        
        # Look for Python-like patterns
        python_patterns = (
            stripped.startswith(('import ', 'from ', 'def ', 'class ', '#')),
            'plt.' in stripped,
            'np.' in stripped,
            '=' in stripped and not stripped.startswith('='),
            stripped.startswith(('if ', 'for ', 'while '))
        )
        
        if any(python_patterns):
            in_code = True
            
        if in_code and stripped:
            code_lines.append(line)
    
    if code_lines:
        return '\n'.join(code_lines)
    
    # Last resort: return original
    return text.strip()


def suggest_plots(summary: str, equations: list) -> str:
    """
    Use LLM to suggest visualization code for the research paper.
    Returns Python plotting code as string.
    """
    # Format equations nicely
    eq_text = "\n".join([
        f"- {eq.get('cleaned', str(eq))}" 
        for eq in equations[:5]  # Limit to 5 equations
    ])

    # Ultra-strict prompt
    prompt = f"""Generate Python visualization code for this research paper.

SUMMARY:
{summary[:800]}

KEY EQUATIONS:
{eq_text}

REQUIREMENTS:
1. Create 2-3 informative plots using matplotlib
2. Use synthetic/example data to illustrate concepts
3. Each plot should be in a separate plt.figure()
4. Add clear titles, labels, and legends
5. Output ONLY Python code (no explanations)
6. Start with 'import' or '#'

Generate plotting code now:"""

    print(f"  Requesting plot suggestions from LLM...")
    raw_response = pplx_chat(prompt, model="sonar")
    
    # Extract clean code
    cleaned_code = extract_code_from_response(raw_response)
    
    # Show preview
    preview = cleaned_code[:150].replace('\n', ' ')
    print(f"  Generated code preview: {preview}...")
    
    return cleaned_code


# Test the suggester
if __name__ == "__main__":
    test_summary = "Research on Fast Multipole Method with O(N) complexity"
    test_equations = [
        {"cleaned": "f(x) = sum K(x,y) * q"},
        {"cleaned": "x_m = cos((2m-1)π/(2n))"}
    ]
    
    code = suggest_plots(test_summary, test_equations)
    print("\n=== Generated Code ===")
    print(code[:500])