import nbformat as nbf
import os
import re


def build_notebook(summary, equations, final_code, plot_paths=None):
    nb = nbf.v4.new_notebook()

    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.8.0"
        }
    }

    cells = []

    # Title
    cells.append(nbf.v4.new_markdown_cell(
        "# Research Paper Implementation\n\n"
        "*Auto-generated from PDF using AI pipeline*\n\n---"
    ))

    # Summary
    summary_md = "## 📄 Paper Summary\n\n"
    lines = [line.strip() for line in summary.split('\n') if line.strip()]
    summary_md += '\n'.join(f"- {line}" for line in lines)
    cells.append(nbf.v4.new_markdown_cell(summary_md))

    # Equations
    if equations:
        eq_md = "## 🔢 Key Mathematical Equations\n\n"
        valid_equations = [eq for eq in equations if is_displayable(eq)]

        for i, eq in enumerate(valid_equations[:10], 1):
            if isinstance(eq, dict):
                latex = eq.get("latex", "") or eq.get("cleaned", "")
            else:
                latex = str(eq)

            eq_md += f"**Equation {i}**\n\n$$\n{latex}\n$$\n\n---\n\n"

        cells.append(nbf.v4.new_markdown_cell(eq_md))

    # Requirements
    cells.append(nbf.v4.new_markdown_cell(
        "## 📦 Requirements\n\n```bash\npip install numpy scipy matplotlib\n```"
    ))

    # Implementation header
    cells.append(nbf.v4.new_markdown_cell("## 💻 Implementation"))

    # 🔥 CLEAN + SPLIT CODE PROPERLY
    cleaned_code = clean_llm_output(final_code)
    code_blocks = split_code_into_cells(cleaned_code)

    for i, block in enumerate(code_blocks, 1):
        cells.append(nbf.v4.new_markdown_cell(f"### Step {i}"))
        cells.append(nbf.v4.new_code_cell(block))

    # Visualizations
    if plot_paths:
        cells.append(nbf.v4.new_markdown_cell("## 📊 Visualizations"))

        for i, plot_path in enumerate(plot_paths, 1):
            rel_path = os.path.relpath(plot_path, "generated_notebooks")
            cells.append(nbf.v4.new_markdown_cell(
                f"### Visualization {i}\n\n![Plot {i}](../{rel_path})"
            ))

    # Save notebook
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"generated_notebooks/paper_{timestamp}.ipynb"
    os.makedirs("generated_notebooks", exist_ok=True)

    with open(out_path, "w") as f:
        nbf.write(nb, f)

    return out_path


# 🔥 FIX: remove ```python wrappers
def clean_llm_output(code: str):
    code = code.strip()

    if code.startswith("```"):
        code = re.sub(r"^```[a-zA-Z]*\n?", "", code)
        code = re.sub(r"\n```$", "", code)

    return code.strip()


# 🔥 FIX: robust equation handling
def is_displayable(eq):
    if isinstance(eq, dict):
        cleaned = eq.get("cleaned", "") or eq.get("latex", "")
    else:
        cleaned = str(eq)

    if len(cleaned) < 5 or len(cleaned) > 300:
        return False

    math_chars = ['=', '+', '-', '*', '/', '^', '_', '\\']
    return any(char in cleaned for char in math_chars)


# 🔥 FIX: proper multi-cell splitting
def split_code_into_cells(code: str):
    pattern = r'(?=^def |^class |^import |^from |\n# |\nif __name__)'
    blocks = re.split(pattern, code, flags=re.MULTILINE)
    return [b.strip() for b in blocks if b.strip()]