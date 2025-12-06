import nbformat as nbf
import os

def build_notebook(summary, equations, final_code, plot_paths=None):
    """
    Creates a professional .ipynb notebook with:
    - Title and metadata
    - Executive summary
    - Rendered equations (LaTeX)
    - Installation requirements
    - Documented code with sections
    - Visualization plots (if provided)
    """

    nb = nbf.v4.new_notebook()
    
    # Add metadata
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
    
    # 1. Title Cell
    cells.append(nbf.v4.new_markdown_cell(
        "# Research Paper Implementation\n\n"
        "*Auto-generated from PDF using AI pipeline*\n\n"
        "---"
    ))
    
    # 2. Summary Cell (formatted better)
    summary_md = "## 📄 Paper Summary\n\n"
    
    # Split summary into bullet points if not already formatted
    if '- ' in summary or '• ' in summary:
        summary_md += summary
    else:
        # Convert paragraphs to bullets
        lines = [line.strip() for line in summary.split('\n') if line.strip()]
        summary_md += '\n'.join(f"- {line}" for line in lines)
    
    cells.append(nbf.v4.new_markdown_cell(summary_md))
    
    # 3. Key Equations Section
    if equations and len(equations) > 0:
        eq_md = "## 🔢 Key Mathematical Equations\n\n"
        
        # Filter for displayable equations
        valid_equations = [eq for eq in equations if is_displayable(eq)]
        
        if valid_equations:
            eq_md += "*Extracted equations (LaTeX rendering in Jupyter):*\n\n"
            
            for i, eq in enumerate(valid_equations[:10], 1):
                # Try to get LaTeX format
                latex = eq.get('latex', eq.get('cleaned', ''))
                confidence = eq.get('confidence', 0)
                description = eq.get('description', '')
                page = eq.get('page', '?')
                
                eq_md += f"**Equation {i}** (Page {page}, Confidence: {confidence}/10)\n\n"
                
                # If we have proper LaTeX, display it
                if latex and len(latex) > 5:
                    # Clean LaTeX if needed - wrap in display math
                    if not latex.startswith('$') and not latex.startswith('\\['):
                        latex_display = f"$$\n{latex}\n$$"
                    else:
                        latex_display = latex
                    
                    eq_md += f"{latex_display}\n\n"
                    
                    # Add description if available
                    if description:
                        eq_md += f"*{description}*\n\n"
                else:
                    # Fallback to code block
                    eq_md += f"```\n{latex}\n```\n\n"
                
                eq_md += "---\n\n"
        else:
            eq_md += "*No well-formatted equations could be extracted.*\n\n"
            eq_md += "**Possible reasons:**\n"
            eq_md += "- PDF has equations as images\n"
            eq_md += "- Complex LaTeX lost during extraction\n"
            eq_md += "- Try using Claude Vision API (set ANTHROPIC_API_KEY)\n\n"
        
        cells.append(nbf.v4.new_markdown_cell(eq_md))
    
    # 4. Installation/Requirements Cell
    cells.append(nbf.v4.new_markdown_cell(
        "## 📦 Requirements\n\n"
        "Make sure you have the following installed:\n\n"
        "```bash\n"
        "pip install numpy scipy matplotlib\n"
        "```"
    ))
    
    # 5. Implementation Section Header
    cells.append(nbf.v4.new_markdown_cell(
        "## 💻 Implementation\n\n"
        "*The following code implements the core algorithms described in the paper.*\n\n"
        "**Note:** This is an AI-generated initial implementation. "
        "Review and modify as needed for your specific use case."
    ))
    
    # 6. Code Cell (with better formatting)
    # Add imports comment if not present
    if not final_code.strip().startswith('#'):
        final_code = "# Auto-generated implementation\n\n" + final_code
    
    cells.append(nbf.v4.new_code_cell(final_code))
    
    # 7. Visualizations Section (if plots provided)
    if plot_paths and len(plot_paths) > 0:
        cells.append(nbf.v4.new_markdown_cell(
            "## 📊 Visualizations\n\n"
            "*The following plots illustrate key concepts from the paper.*"
        ))
        
        # Add each plot as an image in markdown
        for i, plot_path in enumerate(plot_paths, 1):
            # Get relative path from notebook location
            rel_path = os.path.relpath(plot_path, "generated_notebooks")
            
            # Add markdown cell with image
            cells.append(nbf.v4.new_markdown_cell(
                f"### Visualization {i}\n\n"
                f"![Plot {i}](../{rel_path})"
            ))
    
    # 8. Usage Example Section
    cells.append(nbf.v4.new_markdown_cell(
        "## 🚀 Usage Example\n\n"
        "Run the cells above, then use the functions as needed:\n\n"
        "```python\n"
        "# Example usage will depend on the specific implementation\n"
        "# Refer to function signatures above\n"
        "```"
    ))
    
    # 9. Notes and Next Steps
    cells.append(nbf.v4.new_markdown_cell(
        "## 📝 Notes & Next Steps\n\n"
        "- ✅ Basic implementation complete\n"
        "- ✅ Visualizations generated\n"
        "- ⚠️ Review equation extraction accuracy\n"
        "- 🔧 Add validation tests\n"
        "- 📊 Customize visualizations as needed\n"
        "- 📚 Add references to original paper\n\n"
        "---\n\n"
        "*Generated with research-to-code pipeline*"
    ))
    
    # Assign cells to notebook
    nb["cells"] = cells

    # Output path with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"generated_notebooks/paper_implementation_{timestamp}.ipynb"
    os.makedirs("generated_notebooks", exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    return out_path


def is_displayable(eq: dict) -> bool:
    """Check if equation is worth displaying."""
    cleaned = eq.get('cleaned', '') or eq.get('latex', '')
    
    # Must have reasonable length
    if len(cleaned) < 5 or len(cleaned) > 300:
        return False
    
    # Must contain mathematical content
    math_chars = ['=', '+', '-', '*', '/', '^', '_', '\\sum', '\\int', '\\frac', 'sum', 'int', 'frac']
    if not any(char in cleaned for char in math_chars):
        return False
    
    # Shouldn't be mostly words (unless it's LaTeX commands)
    if '\\' not in cleaned:  # Not LaTeX
        words = cleaned.split()
        if len(words) > 20:
            return False
    
    return True


# Test the function
if __name__ == "__main__":
    test_summary = """
    - Implements Fast Multipole Method for N-body problems
    - Achieves O(N) complexity using hierarchical decomposition
    - Uses Chebyshev interpolation for kernel approximation
    """
    
    test_equations = [
        {
            "cleaned": "f(x_i) = \\sum_{j=1}^N K(x_i,y_j)\\sigma_j",
            "latex": "f(x_i) = \\sum_{j=1}^N K(x_i,y_j)\\sigma_j",
            "confidence": 10,
            "page": 1,
            "description": "N-body summation formula"
        },
        {
            "cleaned": "x_m = \\cos\\left(\\frac{(2m-1)\\pi}{2n}\\right)",
            "latex": "x_m = \\cos\\left(\\frac{(2m-1)\\pi}{2n}\\right)",
            "confidence": 9,
            "page": 2,
            "description": "Chebyshev nodes"
        }
    ]
    
    test_code = """import numpy as np

def chebyshev_nodes(n):
    \"\"\"Generate Chebyshev nodes.\"\"\"
    k = np.arange(1, n + 1)
    return np.cos((2 * k - 1) * np.pi / (2 * n))

# Example usage
nodes = chebyshev_nodes(8)
print(f"Generated {len(nodes)} Chebyshev nodes")"""
    
    path = build_notebook(test_summary, test_equations, test_code)
    print(f"✓ Test notebook created at: {path}")