import re

def extract_equations(text: str) -> list:
    """
    Extract mathematical equations from text with better filtering.
    Returns list of dicts with 'raw' and 'cleaned' keys.
    """
    equations = []
    
    # Pattern 1: LaTeX-style equations with delimiters
    latex_patterns = [
        r'\$\$(.*?)\$\$',  # Display math $$...$$
        r'\\\[(.*?)\\\]',   # Display math \[...\]
        r'\\\((.*?)\\\)',   # Inline math \(...\)
    ]
    
    for pattern in latex_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            cleaned = match.strip()
            if is_valid_equation(cleaned):
                equations.append({
                    "raw": match,
                    "cleaned": cleaned
                })
    
    # Pattern 2: Common mathematical expressions (fallback)
    # Look for lines with math symbols and reasonable structure
    math_pattern = r'([A-Za-z_]\w*\s*=\s*[^,;\n]{5,100})'
    matches = re.findall(math_pattern, text)
    
    for match in matches:
        cleaned = match.strip()
        if is_valid_equation(cleaned) and has_math_symbols(cleaned):
            # Avoid duplicates
            if not any(eq['cleaned'] == cleaned for eq in equations):
                equations.append({
                    "raw": match,
                    "cleaned": cleaned
                })
    
    # Remove duplicates and filter by quality
    seen = set()
    filtered = []
    for eq in equations:
        key = eq['cleaned']
        if key not in seen and len(key) > 10:  # Min length filter
            seen.add(key)
            filtered.append(eq)
    
    return filtered[:20]  # Limit to top 20 equations


def is_valid_equation(text: str) -> bool:
    """Check if text looks like a valid equation."""
    if len(text) < 5 or len(text) > 300:
        return False
    
    # Must contain some math content
    math_indicators = ['=', r'\sum', r'\int', r'\frac', r'\times', '+', '-', '*', '/']
    if not any(indicator in text for indicator in math_indicators):
        return False
    
    # Exclude if mostly prose
    words = re.findall(r'\b[A-Za-z]{4,}\b', text)
    if len(words) > 15:  # Too many long words = probably prose
        return False
    
    return True


def has_math_symbols(text: str) -> bool:
    """Check if text contains mathematical symbols."""
    math_symbols = [
        '∑', '∫', '∂', '∇', '√', '±', '×', '÷', '≈', '≠', '≤', '≥',
        r'\sum', r'\int', r'\partial', r'\nabla', r'\sqrt', r'\frac',
        r'\alpha', r'\beta', r'\gamma', r'\theta', r'\sigma', r'\omega'
    ]
    return any(symbol in text for symbol in math_symbols)


def format_equation_for_notebook(eq: dict) -> str:
    """Format equation nicely for Jupyter notebook display."""
    cleaned = eq['cleaned']
    
    # If it already has LaTeX delimiters, use as-is
    if cleaned.startswith('\\[') or cleaned.startswith('$$'):
        return cleaned
    
    # Otherwise, wrap in display math
    return f"$${cleaned}$$"


# Example usage and testing
if __name__ == "__main__":
    sample_text = """
    The N-body problem is formulated as f(x_i) = \sum_{j=1}^N K(x_i,y_j)\sigma_j.
    
    $$K(x,y) = \\frac{1}{|x-y|}$$
    
    Chebyshev nodes are given by x_m = cos((2m-1)π/(2n)).
    
    This is just regular text without equations.
    
    The complexity is O(N log N) for the algorithm.
    """
    
    equations = extract_equations(sample_text)
    print(f"Found {len(equations)} equations:")
    for i, eq in enumerate(equations, 1):
        print(f"{i}. {eq['cleaned']}")