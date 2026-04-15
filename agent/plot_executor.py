import os
import sys
import tempfile
import subprocess
import uuid
import pathlib
import re


def execute_plot_code(code: str, output_dir: str = None) -> tuple:
    """
    Execute plotting code and save the resulting image.
    Returns (image_path, error_message) tuple.
    """
    if output_dir is None:
        project_root = pathlib.Path(__file__).parent.parent
        output_dir = str(project_root / "generated_plots")

    os.makedirs(output_dir, exist_ok=True)

    img_name = f"plot_{uuid.uuid4().hex}.png"
    img_path = os.path.join(output_dir, img_name)

    final_code = f"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

{code}

plt.tight_layout()
plt.savefig("{img_path}", dpi=150, bbox_inches='tight')
plt.close('all')
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as f:
        f.write(final_code)
        temp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, temp_path],  # fixed: was os.sys.executable
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )

        if result.returncode != 0:
            return None, result.stderr

        if not os.path.exists(img_path):
            return None, "Plot file was not created"

        return img_path, None

    except subprocess.TimeoutExpired:
        return None, "Plot execution timed out (30s)"
    except Exception as e:
        return None, f"Execution error: {e}"
    finally:
        try:
            os.remove(temp_path)
        except:
            pass


def execute_multiple_plots(plot_code: str, output_dir: str = None) -> list:
    """
    Split plot code into blocks and execute each one.
    Returns list of successful image paths.
    """
    plot_paths = []
    blocks = split_plot_code(plot_code)

    print(f"  Found {len(blocks)} plot block(s)")

    for i, block in enumerate(blocks, 1):
        print(f"  Executing plot {i}/{len(blocks)}...")
        img_path, error = execute_plot_code(block, output_dir)
        if img_path:
            plot_paths.append(img_path)
            print(f"  ✓ Plot {i} saved: {os.path.basename(img_path)}")
        else:
            print(f"  ✗ Plot {i} failed: {error}")

    return plot_paths


def split_plot_code(code: str) -> list:
    """Split plot code into separate executable blocks at each plt.figure() call."""
    code = re.sub(r"^```[a-zA-Z]*\n?", "", code.strip())
    code = re.sub(r"\n?```$", "", code)

    matches = list(re.finditer(
        r'(?:plt\.figure\(|fig.*?=.*?plt\.subplots\()', code
    ))

    if len(matches) > 1:
        blocks = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(code)
            block = code[start:end].strip()
            if block:
                blocks.append(block)
        return blocks

    return [code]