import os
import tempfile
import subprocess
import uuid

def execute_plot_code(code: str, output_dir="generated_plots"):
    """
    Execute plotting code and save the resulting image.
    Returns (image_path, error_message) tuple.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Generate unique filename
    img_name = f"plot_{uuid.uuid4().hex}.png"
    img_path = os.path.join(output_dir, img_name)

    # Wrap code with proper imports and save command
    final_code = f"""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# User's plotting code
{code}

# Save the figure
plt.tight_layout()
plt.savefig("{img_path}", dpi=150, bbox_inches='tight')
plt.close('all')  # Clean up
"""

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as temp_file:
        temp_file.write(final_code)
        temp_path = temp_file.name

    try:
        # Execute the code
        result = subprocess.run(
            [os.sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )

        # Check if execution was successful
        if result.returncode != 0:
            return None, result.stderr

        # Verify the image was created
        if not os.path.exists(img_path):
            return None, "Plot file was not created"

        return img_path, None

    except subprocess.TimeoutExpired:
        return None, "Plot execution timed out (30s limit)"
    except Exception as e:
        return None, f"Execution error: {str(e)}"
    finally:
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass


def execute_multiple_plots(plot_code: str, output_dir="generated_plots"):
    """
    Execute multiple plot code blocks and return list of successful image paths.
    Tries to intelligently split the code into separate plots.
    """
    plot_paths = []
    
    # Try to split by common plot separators
    # Method 1: Split by plt.figure() calls
    blocks = split_plot_code(plot_code)
    
    if len(blocks) == 1:
        # Single plot - execute as-is
        img_path, error = execute_plot_code(blocks[0], output_dir)
        if img_path:
            plot_paths.append(img_path)
        else:
            print(f"⚠️ Plot execution failed: {error}")
    else:
        # Multiple plots - execute each separately
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
    """
    Intelligently split plot code into separate executable blocks.
    """
    # Remove markdown fences if present
    code = code.replace("```python", "").replace("```", "").strip()
    
    blocks = []
    
    # Method 1: Split by plt.figure() or fig = plt.subplots()
    figure_pattern = r'(?:plt\.figure\(|fig.*?=.*?plt\.subplots\()'
    
    import re
    matches = list(re.finditer(figure_pattern, code))
    
    if len(matches) > 1:
        # Multiple figures detected
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(code)
            block = code[start:end].strip()
            if block:
                blocks.append(block)
    else:
        # Single block or no clear separation
        blocks.append(code)
    
    return blocks


# Test function
if __name__ == "__main__":
    # Test with simple plot
    test_code = """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y)
plt.title('Test Plot')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
"""
    
    img_path, error = execute_plot_code(test_code)
    if img_path:
        print(f"✓ Test plot saved: {img_path}")
    else:
        print(f"✗ Test failed: {error}")

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "generated_plots")