import re

def extract_equations(text: str) -> list:
    """
    Extract mathematical equations as clean strings.
    Compatible with Day-7 pipeline (list[str], no dicts).
    """

    # Ensure input is a string
    if isinstance(text, dict):
        text = text.get('text', str(text))

    equations = []

    # ---------------------------
    # 1. LaTeX-style equations
    # ---------------------------
    latex_patterns = [
        r'\$\$(.*?)\$\$',        # $$ ... $$
        r'\\\[(.*?)\\\]',        # \[ ... \]
        r'\\\((.*?)\\\)',        # \( ... \)
    ]

    for pattern in latex_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            cleaned = match.strip()
            if is_valid_equation(cleaned):
                equations.append(cleaned)

    # ---------------------------
    # 2. Inline algebraic expressions
    # ---------------------------
    inline_pattern = r'([A-Za-z0-9_]+\s*=\s*[^,;\n]{5,120})'
    matches = re.findall(inline_pattern, text)

    for match in matches:
        cleaned = match.strip()
        if is_valid_equation(cleaned) and has_math_symbols(cleaned):
            if cleaned not in equations:
                equations.append(cleaned)

    # ---------------------------
    # Final filtering
    # ---------------------------
    final = []
    seen = set()

    for eq in equations:
        if eq not in seen:
            seen.add(eq)
            final.append(eq)

    # Limit to top 20
    return final[:20]


def is_valid_equation(equation: str) -> bool:
    equation = equation.strip()
    return len(equation) >= 3


def has_math_symbols(equation: str) -> bool:
    math_symbols = ['+', '-', '*', '/', '=', '^', '\\', '(', ')']
    greek_letters = [
        'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega'
    ]
    return any(symbol in equation for symbol in math_symbols) or any(greek in equation.lower() for greek in greek_letters)


# Direct test
if __name__ == "__main__":
    sample = """
    f(x_i) = \\sum_{j=1}^N K(x_i, y_j) \\sigma_j

    $$K(x,y) = \\frac{1}{|x-y|}$$

    x_m = cos((2m - 1)π / (2n))

    This is normal text.
    """

    eqs = extract_equations(sample)
    print(f"Found {len(eqs)} equations:")
    for e in eqs:
        print(" -", e)
